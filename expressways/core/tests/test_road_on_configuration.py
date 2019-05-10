from django.test import TestCase
from django.urls import reverse

from expressways.core.factories import UserFactory, ConfigurationFactory
from expressways.core.models import OccurrenceConfiguration, Road

class TestRoadOnConfiguration(TestCase):
    def setUp(self):
        self.test_admin = UserFactory(superuser=True)
        self.client.force_login(self.test_admin)

    def test_add_configuration_with_road(self):
        '''
        New occurrence configuration with road should be added successfully into the table
        '''
        self.assertEqual(OccurrenceConfiguration.objects.all().count(), 0)
        config = ConfigurationFactory()
        self.assertEqual(OccurrenceConfiguration.objects.all().count(), 1)
        self.assertTrue(OccurrenceConfiguration.objects.get(road=config.road))

    def test_edit_road_on_configuration(self):
        '''
        On admin occurrence configuration change page,
        road field should be readonly 
        '''
        config = ConfigurationFactory()
        data = {
            'object_id': config.id
        }
        resp = self.client.get(reverse('admin:core_occurrenceconfiguration_change', kwargs=data))
        html = resp.content.decode()
        self.assertInHTML(f'<div class="readonly">{config.road.name}</div>', html)

    def test_delete_configuration_with_road(self):
        '''
        When specific road is deleted from the road table,
        all related configuration should be deleted as well from the configuration table
        '''
        config = ConfigurationFactory()
        self.assertEqual(OccurrenceConfiguration.objects.all().count(), 1)
        self.assertEqual(Road.objects.all().count(), 1)
        Road.objects.filter(name=config.road.name).delete()
        self.assertEqual(Road.objects.all().count(), 0)
        self.assertEqual(OccurrenceConfiguration.objects.all().count(), 0)