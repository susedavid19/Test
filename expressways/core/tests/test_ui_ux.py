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

    @unittest.skip("adding new configuration section from home page currently disabled")
    def test_class_is_set_on_tags(self):
        """
        On home page, all relevant tags has its class attribute set to respective value
        """
        self.login()
        self.selenium.get(self.live_server_url)
        for element, className in self.element_class_obj.items():
            list_elements = self.selenium.find_elements_by_xpath('//{}[@class=" {}"]'.format(element, className))
            self.assertNotEqual(0, len(list_elements))

    def add_new_configuration(self, data):
        """
        This method will add new occurrence configuration through the form
        """
        self.selenium.find_element_by_xpath('//a[@data-toggle="collapse"]').click()
        occurrence = Select(self.selenium.find_element_by_id('id_occurrence'))
        occurrence.select_by_value(str(data['occurrence']))
        sub_occurrence = Select(self.selenium.find_element_by_id('id_sub_occurrence'))
        sub_occurrence.select_by_value(str(data['sub_occurrence']))
        lane_closures = Select(self.selenium.find_element_by_id('id_lane_closures'))
        lane_closures.select_by_value(str(data['lane_closures']))
        duration = Select(self.selenium.find_element_by_id('id_duration'))
        duration.select_by_value(str(data['duration']))
        flow = Select(self.selenium.find_element_by_id('id_flow'))
        flow.select_by_value(str(data['flow']))
        self.selenium.find_element_by_id('id_frequency').send_keys(data['frequency'])
        self.selenium.find_element_by_id('save_btn').click()
        self.selenium.implicitly_wait(5)

    @unittest.skip("adding new configuration section from home page currently disabled")
    def test_add_new_configuration(self):
        """
        On home page, when user clicks on 'Add a new occurrence...' section,
        then make relevant selections and click on 'Save',
        occurrence configuration table will be updated with right values
        """
        self.login()
        self.selenium.get(self.live_server_url)
        self.assertEqual(0, len(self.selenium.find_elements_by_xpath('//section[@id="configuration-list"]//div[@class="card"]')))
        self.add_new_configuration(self.configuration_data)
        self.assertTrue(self.selenium.find_element_by_xpath('//section[@id="configuration-list"]//div[@class="card"]'))

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
