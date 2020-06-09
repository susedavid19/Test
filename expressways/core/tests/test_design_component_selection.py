from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils.encoding import force_text
import json

from unittest import skip
from unittest.mock import patch, MagicMock

from expressways.core.factories import UserFactory, DesignComponentFactory, EffectInterventionFactory, ConfigWithEffectFactory, RoadFactory, CalculationResultFactory
from expressways.core.views import CalculateView, ResultView
from expressways.core.models import DesignComponent
from expressways.calculation.import_model import frequency_change, duration_bin

@patch('expressways.core.views.calculate')

class TestDesignComponentSelection(TestCase):
    fixtures = ['designcomponents']

    def setUp(self):
        self.factory = RequestFactory()
        self.view = CalculateView()
        self.road = RoadFactory()

    def test_calculation_with_design_component(self, calculate_exp_mock):
        '''
        Given there are OccurrenceConfigurations for selected road and selected design component
        When I select related design component and perform a calculation
        Then the items are sent to expressways calculation, not for baseline 
        '''
        component = DesignComponentFactory()
        effect = EffectInterventionFactory(design_component=component)
        configurations = ConfigWithEffectFactory.create_batch(3, effect=effect, road=self.road)

        request = self.factory.get(f'/home/{self.road.pk}')
        request.session = {'road_id': self.road.pk}
        request.POST = {'design_components': [component.pk]}
        response = self.view.post(request)

        expected_config_ids = list(map(lambda config: config.pk, configurations))
        expected_component_ids = [component.pk for config in configurations]
        freq_val = [0, 0, 0]
        dur_val = [0, 0, 0]
        expected_items = list(map(self.view.create_expressways_object, configurations, freq_val, dur_val))

        calculate_exp_mock.delay.assert_called_once_with(expected_config_ids, expected_items, expected_component_ids )


    def test_expressways_calculation_object_format(self, calculate_exp_mock):
        '''
        Given an object of the correct format with to be applied frequency and duration values
        When the function is called
        Then the returned object contains all the correct fields
        '''
        mock_configuration = MagicMock()
        mock_configuration.lane_closures = 'first'
        mock_configuration.duration = 30
        mock_configuration.flow = 'third'
        mock_configuration.frequency = 50
        dur_val = -20
        freq_val = 10

        actual = self.view.create_expressways_object(mock_configuration, freq_val, dur_val)
        expected = {
            'lane_closures': 'first',
            'duration': 30,
            'flow': 'third',
            'frequency': 50,
            'duration_change': -0.2,
            'frequency_change': 0.1

        }

        self.assertEqual(expected, actual)

    def test_expressways_value_to_use(self, calculate_exp_mock):
        '''
        Given a list of positive and negative values of possible duration or frequency change
        When the function is called
        Then the returned value is as expected
        '''
        # if all values are negative, choose one with largest absolute value
        mock_list = [-2, -6, 0, -1]
        ret_val = self.view.value_to_use(mock_list)
        self.assertEqual(-6, ret_val)
 
        # if all values are positive, choose one with largest absolute value
        mock_list = [4, 8, 0, 1]
        ret_val = self.view.value_to_use(mock_list)
        self.assertEqual(8, ret_val)
 
        # if there are mixed of negative and positive, ignore the negatives and choose one with largest absolute value
        mock_list = [-15, -6, 0, 2, 10]
        ret_val = self.view.value_to_use(mock_list)
        self.assertEqual(10, ret_val)

    def test_selecting_vms_not_tos(self, calculate_exp_mock):
        '''
        On calculation page
        When user selects Variable Message Sign without Traffic Officer Service design component,
        Specific error is raised
        However, when both are selected, no error is then raised
        '''
        request = self.factory.get(f'/home/{self.road.pk}')
        request.session = {'road_id': self.road.pk}
        request.POST = {'design_components': ['4']}
        response = self.view.post(request)
       
        html = response.content.decode()
        self.assertIn('<p>Error: * VMS has to be selected together with Traffic Officer Service</p>', html)

        request.POST = {'design_components': ['3', '4']}
        response = self.view.post(request)

        html = response.content.decode()
        self.assertNotIn('<p>Error: * VMS has to be selected together with Traffic Officer Service</p>', html)

    @patch('expressways.core.views.AsyncResult')
    def test_view_expressways_calculation_result_only(self, async_result, calculate_exp_mock):
        '''
        Given there are calculation results
        When user selects related design component with expected configuration, 
        Then calculation result is populated with expected value
        '''
        result_view = ResultView()
        
        task = MagicMock()
        task.id = 23
        calculate_exp_mock.delay.return_value = task

        async_obj = MagicMock()
        async_obj.failed.return_value = False
        async_result.return_value = async_obj

        test_objective = {
            "pti": 2.468,
            "journey": 3.579,
            "speed": 4.681
        }

        component = DesignComponent.objects.get(id=1)
        effect = EffectInterventionFactory(design_component=component)
        configuration = ConfigWithEffectFactory(effect=effect, road=self.road)
        calc = CalculationResultFactory(
            task_id=task.id,
            config_ids=[configuration.pk],
            component_ids=[component.pk],
            items=[self.view.create_expressways_object(configuration, 5, -5)],
            objective_pti=test_objective.get('pti'),
            objective_journey=test_objective.get('journey'),
            objective_speed=test_objective.get('speed')
        )

        request = self.factory
        request.session = {}
        response = result_view.get(request, task.id)

        async_result.assert_called_once_with(task.id)
        expressways_expected = {
            "objective_pti": "-", 
            "objective_journey": "-", 
            "objective_speed": "-", 
            "objective_exp_pti": str(test_objective.get('pti')), 
            "objective_exp_journey": str(test_objective.get('journey')),
            "objective_exp_speed": str(test_objective.get('speed'))
        }
        self.assertJSONEqual(json.dumps(expressways_expected), force_text(response.content))

    def test_expressways_frequency_change(self,  calculate_exp_mock):
        '''
        Given a list of positive and negative percentages of frequency change along with a list of frequencies
        When the function is called
        Then the returned list of frequencies is as expected
        '''

        mock_freqs = [55]
        mock_perc = [-0.2]
        expected = [44]
        self.assertEqual(frequency_change(mock_freqs, mock_perc), expected)

        mock_freqs = [55]
        mock_perc = [0.2]
        expected = [66]
        self.assertEqual(frequency_change(mock_freqs, mock_perc), expected)

        mock_freqs = [55, 20, 35]
        mock_perc = [0.2, -0.1, 0.1]
        expected = [66, 18, 38]
        self.assertEqual(frequency_change(mock_freqs, mock_perc), expected)

    def test_expressways_duration_bin(self, calculate_exp_mock):
        '''
        Given a list of positive and negative percentages of duration change along with a list of frequencies
        and the relevant durations
        When the function is called
        Then the returned list of frequencies is as expected
        '''

        # The simple version: single percentage and no other available durations to transfer so acts as the frequency
        # change
        mock_freqs = [55]
        mock_perc = [-0.2]
        mock_duration = [15]
        expected = [44]
        self.assertEqual(duration_bin(mock_freqs, mock_perc, mock_duration), expected)

        # The standard test: three available durations with three duration percentages (both positive and negative)
        # Starting from the largest duration value, we multiply the frequency with the relevant percentage and we add
        # (the negative) result to the final frequency keeping only the integer part. Therefore 46 - 10% = 42 and we
        # keep a -0.6 that we propagate to the next duration by multiplying with the ratio of the durations (60/30). The
        # -1.2 is combined with the percentage change of 30 (1.6) and the result 0.4 doesn't affect the second frequency.
        # However, the 0.4 is multiplied again with the ratio 30/15 and the result 0.8 is combined with the 20*0.3
        # giving a total of 6.8 that is rounded up to 7 as this is the last smallest duration.

        mock_freqs = [20, 16, 46]
        mock_perc = [0.3, 0.1, -0.1]
        mock_duration = [15, 30, 60]
        expected = [27, 16, 42]
        self.assertEqual(duration_bin(mock_freqs, mock_perc, mock_duration), expected)
