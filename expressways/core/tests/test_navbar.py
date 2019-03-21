from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class TestNav(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='sarah')
        self.client.force_login(self.user)

    def test_greeting(self):
        resp = self.client.get(reverse('core:home'))

        self.assertContains(resp, 'Hello, {}'.format(self.user.username))

    def test_no_admin_link_for_none_staff(self):
        resp = self.client.get(reverse('core:home'))

        self.assertInHTML('<a class="nav-link" href="{}">Admin</a>'.format(reverse('admin:index')),
                          resp.content.decode(),
                          count=0)

    def test_admin_link_for_staff(self):
        self.user.is_staff = True
        self.user.save()

        resp = self.client.get(reverse('core:home'))

        self.assertInHTML('<a class="nav-link" href="{}">Admin</a>'.format(reverse('admin:index')),
                          resp.content.decode())

    def test_logout_link(self):
        resp = self.client.get(reverse('core:home'))

        self.assertInHTML('<a class="nav-link" href="{}">Logout</a>'.format(reverse('logout')),
                          resp.content.decode())

    def test_change_password_link(self):
        resp = self.client.get(reverse('core:home'))

        self.assertInHTML('<a class="nav-link" href="{}">Change Password</a>'.format(reverse('password_change')),
                          resp.content.decode())
