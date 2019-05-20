from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from lxml import etree

from expressways.core.models import Occurrence, SubOccurrence, OccurrenceConfiguration, Road

User = get_user_model()


class TestOccurrenceList(TestCase):
    fixtures = ['occurrences', 'roads']

    def setUp(self):
        self.user = User.objects.create(username='jane')
        self.client.force_login(self.user)

        session = self.client.session
        session['road_id'] = 1
        session.save()

        self.url = reverse('core:home', args=[1])

    def test_occurrence_configuration_table_starts_empty(self):
        resp = self.client.get(self.url)

        self.assertEqual(200, resp.status_code)

        doc = etree.HTML(resp.content.decode())

        self.assertEqual(0, len(doc.xpath('//section[@id="list"]/div[@class="row item"]')))

    def test_single_occurrence_configuration_is_displayed(self):
        sub_occurrence = SubOccurrence.objects.first()
        road = Road.objects.first()
        OccurrenceConfiguration.objects.create(road=road,
                                               sub_occurrence=sub_occurrence,
                                               lane_closures='XX',
                                               duration=60,
                                               flow=300,
                                               frequency=1000)

        resp = self.client.get(self.url)

        doc = etree.HTML(resp.content.decode())

        self.assertEqual(1, len(doc.xpath('//section[@id="configuration-list"]/div[@class="card"]')))
