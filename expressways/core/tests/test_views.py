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
        mock_configuration = MagicMock()
        mock_configuration.lane_closures = 'first'
        mock_configuration.duration = 'second'
        mock_configuration.flow = 'third'
        mock_configuration.frequency = 'fourth'

        actual = self.view.create_calculation_object(mock_configuration)
        expected = {
            'lane_closures': 'first',
            'duration': 'second',
            'flow': 'third',
            'frequency': 'fourth',
        }

        self.assertEquals(expected, actual)

    
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
        self.assertEquals(task.id, request.session['task_id'])

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

        calc = CalculationResultFactory(
            config_ids=expected_config_ids,
            component_ids=[],
            items=expected_items,
        )

        request = self.factory.get(f'/home/{road.pk}')
        request.session = {'road_id': road.pk}

        self.view.post(request)
        calculate_mock.delay.assert_not_called()        
