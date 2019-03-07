from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from lxml import etree

from expressways.core.models import SubOccurrence, OccurrenceConfiguration

User = get_user_model()


class TestOccurrenceList(TestCase):
    fixtures = ['occurrences']

    def setUp(self):
        self.user = User.objects.create(username='jane')
        self.client.force_login(self.user)

        self.url = reverse('core:home')

    def test_occurrence_configuration_table_starts_empty(self):
        resp = self.client.get(self.url)

        self.assertEqual(200, resp.status_code)

        doc = etree.HTML(resp.content.decode())

        self.assertEqual(0, len(doc.xpath('//section[@id="list"]/div[@class="row item"]')))

    def test_single_occurrence_configuration_is_displayed(self):
        sub_occurrence = SubOccurrence.objects.first()
        OccurrenceConfiguration.objects.create(sub_occurrence=sub_occurrence,
                                               lane_closures='XX',
                                               duration=60,
                                               flow=300,
                                               frequency=1000)

        resp = self.client.get(self.url)

        doc = etree.HTML(resp.content.decode())

        self.assertEqual(1, len(doc.xpath('//section[@id="configuration-list"]/div[@class="row"]')))
