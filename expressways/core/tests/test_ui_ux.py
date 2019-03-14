import socket
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common import desired_capabilities, keys
from selenium.webdriver.support.select import Select

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings, tag
from django.urls import reverse
from django.contrib.auth import get_user_model

from expressways.core.models import OccurrenceConfiguration

User = get_user_model()

@tag('selenium')
@override_settings(ALLOWED_HOSTS=['*'])
class BaseTestCase(StaticLiveServerTestCase):
    """
    Provides base test class which connects to the Docker
    container running selenium.
    """
    host = '0.0.0.0'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.host = socket.gethostbyname(socket.gethostname())
        cls.selenium = webdriver.Remote(
            command_executor='http://selenium:4444/wd/hub',
            desired_capabilities=desired_capabilities.DesiredCapabilities.CHROME,
        )
        cls.selenium.implicitly_wait(5)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

class TestUiUx(BaseTestCase):
    fixtures = ['occurrences']

    def setUp(self):
        self.username = 'testuser'
        self.password = '123Expre$$test'
        self.user = User(username=self.username)
        self.user.set_password(self.password)
        self.user.save()

        self.element_class_obj = None

    def login(self):
        """
        This method will log test user into the application
        """
        self.selenium.get('%s%s' % (self.live_server_url, "/accounts/login/"))
        username_input = self.selenium.find_element_by_id('id_username')
        username_input.send_keys(self.username)
        password_input = self.selenium.find_element_by_id('id_password')
        password_input.send_keys(self.password)

        self.selenium.find_element_by_tag_name('button').click()
        self.element_class_obj = self.selenium.execute_script('return element_class_obj')

    def test_class_is_set_on_tags(self):
        """
        On home page, all relevant tags has its class attribute set to respective value
        """
        self.login()
        self.selenium.get(self.live_server_url)
        for element, className in self.element_class_obj.items():
            select_el = self.selenium.find_element_by_xpath('//{}[@class=" {}"]'.format(element, className))
            self.assertTrue(select_el)
