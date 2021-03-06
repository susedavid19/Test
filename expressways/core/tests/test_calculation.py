from django.test import RequestFactory, TestCase
from django.utils.encoding import force_text
from unittest.mock import patch, MagicMock
import json

from expressways.core.views import CalculateView, ResultView
from expressways.core.factories import RoadFactory, CalculationResultFactory, ConfigurationFactory
from expressways.core.models import OccurrenceConfiguration
from expressways.calculation.models import CalculationResult
from expressways.calculation.metrics import incidents_cleared
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client
User = get_user_model()

class TestCalculation(TestCase):
    fixtures = ['designcomponents', 'operationalobjectives']

    def setUp(self):
        self.factory = RequestFactory()
        self.view = CalculateView()
        self.road = RoadFactory()
        self.client = Client()

    @patch('expressways.core.views.calculate')
    @patch('expressways.core.views.AsyncResult')
    def test_view_baseline_calculation_result_only(self, async_result, calculate_mock):
        '''
        Given there are calculation results
        When user proceeds with expected configuration, 
        Then only baseline calculation result is populated with expected value
        '''
        result_view = ResultView()
        
        task = MagicMock()
        task.id = 23
        calculate_mock.delay.return_value = task

        async_obj = MagicMock()
        async_obj.failed.return_value = False
        async_result.return_value = async_obj

        test_objective = {
            'incident': 1.357,
            'pti': 2.468,
            'journey': 3.579,
            'speed': 4.681
        }

        configuration = ConfigurationFactory(road=self.road)
        calc = CalculationResultFactory(
            task_id=task.id,
            config_ids=[configuration.pk],
            component_ids=[],
            items=[self.view.create_calculation_object(configuration)],
            objective_incident=test_objective.get('incident'),
            objective_pti=test_objective.get('pti'),
            objective_journey=test_objective.get('journey'),
            objective_speed=test_objective.get('speed')
        )

        request = self.factory
        request.session = {}
        response = result_view.get(request, task.id)

        async_result.assert_called_once_with(task.id)
        baseline_expected = {
            'objective_incident': str(test_objective.get('incident')), 
            'objective_pti': str(test_objective.get('pti')), 
            'objective_journey': str(test_objective.get('journey')),
            'objective_speed': str(test_objective.get('speed')),
            'objective_exp_incident': '-', 
            'objective_exp_pti': '-', 
            'objective_exp_journey': '-', 
            'objective_exp_speed': '-'
        }
        self.assertJSONEqual(json.dumps(baseline_expected), force_text(response.content))

    @patch('expressways.core.views.calculate')
    @patch('expressways.core.views.AsyncResult')
    def test_result_display(self, async_result, calculate_mock):
        '''
        Given there are calculation results
        When user proceeds with expected configuration, 
        Then result is displayed in expected format
        '''
        task = MagicMock()
        task.id = 23
        calculate_mock.delay.return_value = task

        async_obj = MagicMock()
        async_obj.failed.return_value = False
        async_result.return_value = async_obj

        test_objective = {
            'incident': 1.357,
            'pti': 2.468,
            'journey': 3.579,
            'speed': 4.681
        }

        configuration = ConfigurationFactory(road=self.road)
        calc = CalculationResultFactory(
            task_id=task.id,
            config_ids=[configuration.pk],
            component_ids=[],
            items=[self.view.create_calculation_object(configuration)],
            objective_incident=test_objective.get('incident'),
            objective_pti=test_objective.get('pti'),
            objective_journey=test_objective.get('journey'),
            objective_speed=test_objective.get('speed')
        )

        data = {
            'task_id': task.id,
            'road_id': self.road.id
        }

        result_view = ResultView()
        request = self.factory
        request.session = data
        response = result_view.get(request, task.id)

        async_result.assert_called_once_with(task.id)

        resp = self.client.post(reverse('core:calculate'), data)
        self.assertEqual(302, resp.status_code)

    def get_ic_result(self):
        '''
        Helper function to calculate incidents cleared result given current occurrence configurations
        '''
        items = []
        for config in OccurrenceConfiguration.objects.all():
            items.append(self.view.create_calculation_object(config))
        
        return incidents_cleared(items)

    def test_incidents_cleared(self):
        '''
        Given a list of occurrence configurations with/out incidents cleared characteristics
        When the function is called
        Then the returned value is as expected
        '''
        config_ic_less60 = ConfigurationFactory(
                    road=self.road,
                    flow='Medium',
                    frequency=2,
                    duration=10.0,
                    incidents_cleared=True,
                    )
        config_ic_more60_1 = ConfigurationFactory(
                    road=self.road,
                    flow='Medium',
                    frequency=4,
                    duration=90.0,
                    incidents_cleared=True,
                    )
        config_ic_more60_2 = ConfigurationFactory(
                    road=self.road,
                    flow='High',
                    frequency=2,
                    duration=90.0,
                    incidents_cleared=True,
                    )

        self.assertEqual(OccurrenceConfiguration.objects.count(), 3)
        sum_less_than_hour = config_ic_less60.frequency
        sum_filtered_list = config_ic_less60.frequency + config_ic_more60_1.frequency + config_ic_more60_2.frequency
        self.assertEqual(self.get_ic_result(), 100 * (sum_less_than_hour / sum_filtered_list))

        OccurrenceConfiguration.objects.all().delete()
        config_non_ic_1 = ConfigurationFactory(
                    road=self.road,
                    flow='High',
                    frequency=2,
                    duration=10.0,
                    incidents_cleared=False,
                    )
        config_non_ic_2 = ConfigurationFactory(
                    road=self.road,
                    flow='Low',
                    frequency=2,
                    duration=10.0,
                    incidents_cleared=True,
                    )

        self.assertEqual(OccurrenceConfiguration.objects.count(), 2)
        # none of the configurations is related to incidents cleared so expect zero
        self.assertEqual(self.get_ic_result(), 0)