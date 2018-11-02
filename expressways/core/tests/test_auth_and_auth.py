from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user
from django.contrib.auth.models import AnonymousUser

from django.contrib.auth import get_user_model

User = get_user_model()

class TestAuthAndAuth(TestCase):
    def setUp(self):
        self.username = 'fred'
        self.password = 'fred123'
        self.user = User(username=self.username)
        self.user.set_password(self.password)
        self.user.save()

        self.client.logout()

    def test_login_form(self):
        resp = self.client.get(reverse('login'))

        html = resp.content.decode()
        self.assertInHTML('<input type="text" name="username" autofocus required id="id_username">', html)
        self.assertInHTML('<input type="password" name="password" required id="id_password">', html)

    def test_user_logs_in_successfully(self):
        '''
          Given user is on the login page
          When the user input a valid username
          And inputs a valid password
          Then the user is logged into the OMS tool
        '''
        self.assertTrue(get_user(self.client).is_anonymous)

        data = {
            'username': self.username,
            'password': self.password,
        }
        resp = self.client.post(reverse('login'), data)

        self.assertEqual(get_user(self.client), self.user)
        self.assertRedirects(resp, reverse('core:home'))

    def test_user_enters_wrong_password(self):
        '''
          Given user is on the login page
          When the user input a valid username
          and input Invalid password
          Then a message is displayed informing the user that the credentials are invalid
        '''
        self.assertTrue(get_user(self.client).is_anonymous)

        data = {
            'username': self.username,
            'password': 'WRONG',
        }
        resp = self.client.post(reverse('login'), data)

        self.assertEqual(200, resp.status_code)
        self.assertTrue(get_user(self.client).is_anonymous)
        self.assertContains(resp, 'Please enter a correct username and password')

    def test_user_has_active_session(self):
        '''
          Given the user logged in recently
          And the user has an active session
          When the returns to the Tool
          Then the user is automatically redirected to the logged in screen
        '''
        self.client.force_login(self.user)

        resp = self.client.get(reverse('core:home'))

        self.assertEqual(200, resp.status_code)

    def test_user_session_has_expired(self):
        '''
          Given the users active session has expired
          When the user returns to the tool
          Then the user is returned to the login page
        '''
        resp = self.client.get(reverse('core:home'))
        self.assertRedirects(resp, '{}?next={}'.format(reverse('login'),
                                                       reverse('core:home')))
