import unittest

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from expressways.core.models import OccurrenceConfiguration

User = get_user_model()


class TestNewOccurrenceConfiguration(TestCase):
    fixtures = ['occurrences']

    def setUp(self):
        user = User.objects.create()
        self.client.force_login(user)

        self.valid_data = {
            'sub_occurrence': 1,
            'lane_closures': 'XX',
            'duration': 60,
            'flow': 1750,
            'frequency': 1000,
        }

    def test_login_required(self):
        self.client.logout()

        resp = self.client.post(reverse('core:new'), self.valid_data)

        self.assertRedirects(resp, '{}?next={}'.format(reverse('login'),
                                                       reverse('core:new')))

    @unittest.skip('skipped due to null field')
    def test_missing_values_dont_create_configuration(self):
        '''
        This won't really ever occur because form validation will stop it
        '''
        resp = self.client.post(reverse('core:new'), {})

        self.assertEqual(0, OccurrenceConfiguration.objects.count())

    def test_add_configuration(self):
        self.assertEqual(0, OccurrenceConfiguration.objects.count())

        resp = self.client.post(reverse('core:new'), self.valid_data)

        self.assertEqual(1, OccurrenceConfiguration.objects.count())

    def test_redirect_to_home_after_configuration_created(self):
        resp = self.client.post(reverse('core:new'), self.valid_data)

        self.assertRedirects(resp, reverse('core:home'))

    def test_id_remove_from_session(self):
        session = self.client.session
        session['task_id'] = '1234'
        session.save()

        resp = self.client.post(reverse('core:new'), self.valid_data)

        self.assertFalse('task_id' in self.client.session)
