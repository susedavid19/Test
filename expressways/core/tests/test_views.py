from django.test import RequestFactory, TestCase
from django.urls import reverse
from unittest import skip
from unittest.mock import patch, MagicMock

from expressways.core.factories import ConfigurationFactory, RoadFactory, CalculationResultFactory
from expressways.core.views import CalculateView

@patch('expressways.core.views.calculate')
class TestCalculateView(TestCase):
    fixtures = ['designcomponents']

    def setUp(self):
        self.factory = RequestFactory()
        self.view = CalculateView()


    def test_calculation_object_format(self, calculate_mock):
        '''
        Given a object of the correct format
        When the function is called
        Then the returned object contains all the correct fields
        '''
        expected_obj = {
            'lane_closures': 'II',
            'duration': 2.5,
            'flow': 'S',
            'frequency': 10,
            'speed': 70,
            'incidents_cleared': False
        }

        mock_configuration = MagicMock()
        mock_configuration.lane_closures = expected_obj.get('lane_closures')
        mock_configuration.duration = expected_obj.get('duration')
        mock_configuration.flow = expected_obj.get('flow')
        mock_configuration.frequency = expected_obj.get('frequency')
        mock_configuration.speed_limit = expected_obj.get('speed')
        mock_configuration.incidents_cleared = expected_obj.get('incidents_cleared')

        actual_obj = self.view.create_calculation_object(mock_configuration)

        self.assertEqual(expected_obj, actual_obj)

    
    def test_calculation_filters_list_by_road(self, calculate_mock):
        '''
        Given there are OccurrenceConfigurations for many roads
        When I perform a calculation
        Then the calculation is only supplied the OccurrenceConfiguration items that match the road
        ''' 
        road_a = RoadFactory()
        road_b = RoadFactory()

        configurations_a = ConfigurationFactory.create_batch(3, road=road_a)
        configurations_b = ConfigurationFactory.create_batch(5, road=road_b)

        request = self.factory.get(f'/home/{road_a.pk}')
        request.session = {'road_id': road_a.pk}
        response = self.view.post(request)

        expected_config_ids = list(map(lambda config: config.pk, configurations_a))
        expected_items = list(map(self.view.create_calculation_object, configurations_a))

        calculate_mock.delay.assert_called_once_with(expected_config_ids, expected_items)

    
    def test_calculation_sets_task_id_on_session(self, calculate_mock):
        '''
        Given a calculation is performed
        When the view returns the response
        Then the session is updated with the task ID
        '''
        configuration = ConfigurationFactory.create()

        request = self.factory.get(f'/home/{configuration.road.pk}')
        request.session = {'road_id': configuration.road.pk}

        task = MagicMock()
        task.id = 42
        calculate_mock.delay.return_value = task

        self.view.post(request)
        self.assertEqual(task.id, request.session['task_id'])

    def test_calculation_not_performed_when_existing_result_present(self, calculate_mock):
        '''
        Given a calculation has already been performed
        When I perform a calculation with the same OccurrenceConfiguration set
        Then the previous result is returned
        '''        
        road = RoadFactory()
        configurations = ConfigurationFactory.create_batch(3, road=road)
        expected_config_ids = list(map(lambda config: config.pk, configurations))
        expected_items = list(map(self.view.create_calculation_object, configurations))
        dummy_task = 'taskidindb'

        calc = CalculationResultFactory(
            task_id=dummy_task,
            config_ids=expected_config_ids,
            component_ids=[],
            items=expected_items,
        )

        request = self.factory.get(f'/home/{road.pk}')
        request.session = {'road_id': road.pk, 'task_id': 'currenttaskid'}

        task = MagicMock()
        task.id = 42
        calculate_mock.delay.return_value = task

        response = self.view.post(request)
        calculate_mock.delay.assert_not_called()   
        self.assertEqual(200, response.status_code)
        self.assertInHTML(f'<script>var result_url = "/result/{dummy_task}";</script>', response.content.decode())     
