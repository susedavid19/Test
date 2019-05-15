import json
import unittest

from django.test import override_settings, tag
from django.urls import reverse
from django.contrib.auth import get_user_model

from expressways.core.tests.selenium_setup import BaseTestCase, Select, WebDriverWait, EC, By
from expressways.core.models import OccurrenceConfiguration
from expressways.calculation.models import CalculationResult

User = get_user_model()

@tag('selenium')
@override_settings(ALLOWED_HOSTS=['*'])
@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class TestUiUx(BaseTestCase):
    fixtures = ['occurrences']

    def setUp(self):
        self.username = 'testuser'
        self.password = '123Expre$$test'
        self.user = User(username=self.username)
        self.user.set_password(self.password)
        self.user.save()

        self.element_class_obj = None

        self.configuration_data = {
            'occurrence': 1,
            'sub_occurrence': 1,
            'lane_closures': 'XI',
            'duration': 15,
            'flow': 300,
            'frequency': 25,
        }

        self.task_id = '1234'
        self.objective1 = 1.111
        self.objective2 = 2.222

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

    @unittest.skip("element wait failed in pipeline")
    def test_invalid_calculate_results(self):
        """
        On home page, when user clicks on calculate results button, 
        since current task calculation result is not yet available,
        no change on objective results default value ie. '-' and error card is displayed
        """
        self.login()
        self.selenium.get(self.live_server_url)
        self.add_new_configuration(self.configuration_data)
        self.selenium.find_element_by_id('calculate_btn').click()

        WebDriverWait(self.selenium, 60).until(EC.presence_of_element_located((By.XPATH, '//div[@id="error-card"]')))
        self.assertTrue(self.selenium.find_element_by_xpath('//*[contains(text(), "An Error Occurred")]'))
        result1 = self.selenium.find_element_by_xpath('//div[@id="result-1"]')
        self.assertEqual('-', result1.text)
        result2 = self.selenium.find_element_by_xpath('//div[@id="result-2"]')
        self.assertEqual('-', result2.text)
