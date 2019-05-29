from django.test import RequestFactory, TestCase
from django.urls import reverse
from unittest import skip
from unittest.mock import patch, MagicMock

from expressways.core.factories import DesignComponentFactory, EffectInterventionFactory, ConfigWithEffectFactory, RoadFactory
from expressways.core.views import CalculateView

@patch('expressways.core.views.calculate')
@patch('expressways.core.views.calculate_expressways')
class TestDesignComponentSelection(TestCase):
    fixtures = ['designcomponents']

    def setUp(self):
        self.factory = RequestFactory()
        self.view = CalculateView()

    def test_calculation_with_design_component(self, calculate_exp_mock, calculate_mock):
        '''
        Given there are OccurrenceConfigurations for selected road and selected design component
        When I select related design component and perform a calculation
        Then the items are sent to expressways calculation, not for baseline 
        '''
        road = RoadFactory()
        component = DesignComponentFactory()
        effect = EffectInterventionFactory(design_component=component)
        configurations = ConfigWithEffectFactory.create_batch(3, effect=effect, road=road)

        request = self.factory.get(f'/home/{road.pk}')
        request.session = {'road_id': road.pk}
        request.POST = {'design_components': [component.pk]}
        response = self.view.post(request)

        expected_config_ids = list(map(lambda config: config.pk, configurations))
        expected_component_ids = [component.pk for config in configurations]
        expected_items = list(map(self.view.create_calculation_object, configurations))

        calculate_exp_mock.delay.assert_called_once_with(expected_config_ids, expected_component_ids, expected_items)
        calculate_mock.delay.assert_not_called()

    def test_expressways_calculation_object_format(self, calculate_exp_mock, calculate_mock):
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
        dur_val = -10
        freq_val = 10

        actual = self.view.create_expressways_object(mock_configuration, freq_val, dur_val)
        expected = {
            'lane_closures': 'first',
            'duration': 27,
            'flow': 'third',
            'frequency': 55,
        }

        self.assertEquals(expected, actual)

    def test_expressways_value_to_use(self, calculate_exp_mock, calculate_mock):
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
        mock_list = [-15, -6, 0, 10]
        ret_val = self.view.value_to_use(mock_list)
        self.assertEqual(10, ret_val)
 