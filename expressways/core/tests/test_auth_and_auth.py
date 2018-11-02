from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from django.conf import settings

from freezegun import freeze_time

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
        self.assertInHTML('<input id="id_username" name="username" type="text" autofocus>', html)
        self.assertInHTML('<input id="id_password" name="password" type="password">', html)

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

    def test_password_change(self):
        '''
          When the user selects the option to change their password
          And the user submits their old password, new password and new password confirmation
          Then their password is updated to the new value
          And they are shown a confirmation message
        '''
        self.client.force_login(self.user)

        resp = self.client.get(reverse('password_change'))
        html = resp.content.decode()
        self.assertInHTML('<input type="password" name="old_password" autofocus id="id_old_password">', html)
        self.assertInHTML('<input type="password" name="new_password1" id="id_new_password1">', html)
        self.assertInHTML('<input type="password" name="new_password2" id="id_new_password2">', html)

        data = {
            'old_password': self.password,
            'new_password1': 'ahmesa:uX6AinoShox3j',
            'new_password2': 'ahmesa:uX6AinoShox3j',
        }
        resp = self.client.post(reverse('password_change'), data, follow=True)
        self.assertContains(resp, 'Password change successful')

    def test_session_timeout(self):
        self.assertEqual(600, settings.SESSION_COOKIE_AGE)  # 10 minutes

        with freeze_time('2018-11-02 14:48'):
            self.client.force_login(self.user)

        # Still logged in after 5 minutes
        with freeze_time('2018-11-02 14:53'):
            self.assertFalse(get_user(self.client).is_anonymous)

        # Logged out after 10 minutes
        with freeze_time('2018-11-02 14:58'):
            self.assertTrue(get_user(self.client).is_anonymous)
