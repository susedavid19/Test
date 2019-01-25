from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from expressways.core.models import SubOccurrence, OccurrenceConfiguration

User = get_user_model()


class TestDeleteOccurrenceConfiguration(TestCase):
    fixtures = ['occurrences']

    def setUp(self):
        user = User.objects.create()
        self.client.force_login(user)

        sub_occurrence = SubOccurrence.objects.get(pk=1)

        self.occurrence_config = OccurrenceConfiguration.objects.create(
            sub_occurrence=sub_occurrence,
            lane_closures='XX',
            duration=60,
            flow=1750,
            frequency=1000,
        )

        self.delete_url = reverse('core:delete', args=[self.occurrence_config.pk])

    def test_login_required(self):
        self.client.logout()

        resp = self.client.post(self.delete_url)

        self.assertRedirects(resp, '{}?next={}'.format(reverse('login'),
                                                       self.delete_url))

    def test_delete_configuration(self):
        self.assertEqual(1, OccurrenceConfiguration.objects.count())

        resp = self.client.post(self.delete_url)

        self.assertEqual(0, OccurrenceConfiguration.objects.count())

    def test_redirect_to_home_after_deletion(self):
        resp = self.client.post(self.delete_url)

        self.assertRedirects(resp, reverse('core:home'))

    def test_id_remove_from_session(self):
        session = self.client.session
        session['task_id'] = '1234'
        session.save()

        resp = self.client.post(self.delete_url)

        self.assertFalse('task_id' in self.client.session)
