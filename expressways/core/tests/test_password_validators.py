from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class TestPasswordValidators(TestCase):
    def setUp(self):
        self.username = 'hero'
        self.password = 'Hero123!'
        self.user = User(username=self.username)
        self.user.set_password(self.password)
        self.user.save()

        self.client.logout()

    def test_password_all_correct_values(self):
        '''
        On password change page,
        when the user submit their old password, new password and new password confirmation,
        the new values should be
        - minimum length of 9 characters
        - at least 1 uppercase character
        - at least 1 number
        - at least 1 symbol character
        no error is raised and the action is successful
        '''
        self.client.force_login(self.user)

        data = {
            'old_password': self.password,
            'new_password1': '123Expre$$',
            'new_password2': '123Expre$$',
        }
        resp = self.client.post(reverse('password_change'), data, follow=True)
        self.assertContains(resp, 'Password change successful')

    def test_password_less_minimum_characters(self):
        '''
        On password change page,
        when the user submit their old password, new password and new password confirmation,
        if the new values have length less than 9 characters, raise error text
        '''
        self.client.force_login(self.user)

        data = {
            'old_password': self.password,
            'new_password1': '1Expre$$',
            'new_password2': '1Expre$$',
        }
        resp = self.client.post(reverse('password_change'), data, follow=True)
        self.assertContains(resp, 'This password is too short. It must contain at least 9 characters')

    def test_password_missing_uppercase(self):
        '''
        On password change page,
        when the user submit their old password, new password and new password confirmation,
        if the new values dont have any uppercase character, raise error text
        '''
        self.client.force_login(self.user)

        data = {
            'old_password': self.password,
            'new_password1': '123expre$$',
            'new_password2': '123expre$$',
        }
        resp = self.client.post(reverse('password_change'), data, follow=True)
        self.assertContains(resp, 'The password must contain at least 1 uppercase letter')

    def test_password_missing_number(self):
        '''
        On password change page,
        when the user submit their old password, new password and new password confirmation,
        if the new values dont have any number, raise error text
        '''
        self.client.force_login(self.user)

        data = {
            'old_password': self.password,
            'new_password1': 'abcexpre$$',
            'new_password2': 'abcexpre$$',
        }
        resp = self.client.post(reverse('password_change'), data, follow=True)
        self.assertContains(resp, 'The password must contain at least 1 digit')

    def test_password_missing_symbol(self):
        '''
        On password change page,
        when the user submit their old password, new password and new password confirmation,
        if the new values dont have any symbol character, raise error text
        '''
        self.client.force_login(self.user)

        data = {
            'old_password': self.password,
            'new_password1': '123expreSS',
            'new_password2': '123expreSS',
        }
        resp = self.client.post(reverse('password_change'), data, follow=True)
        self.assertContains(resp, 'The password must contain at least 1 of following symbols')
