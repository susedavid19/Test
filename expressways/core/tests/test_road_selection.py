import time 
import unittest
import os

from django.test import override_settings, tag
from django.urls import reverse

from expressways.core.factories import UserFactory, SubOccurrenceFactory, ConfigurationFactory, RoadFactory
from expressways.calculation.models import CalculationResult
from expressways.core.tests.selenium_setup import BaseTestCase, Select, WebDriverWait, By, EC, keys

@override_settings(ALLOWED_HOSTS=['*'])
@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class TestRoadSelection(BaseTestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.force_login(self.user)
        RoadFactory.create_batch(size=5)
        self.road = RoadFactory(
            name='Test Road'
        )

    def test_user_select_road(self):
        '''
        On road selection page, when user selects particular road and confirm,
        user will be redirected to calculation page and chosen road is displayed 
        '''
        resp = self.client.post(reverse('core:road'), {'road': self.road.id})
        self.assertRedirects(resp, reverse('core:home', kwargs={'road_id': self.road.id}))
        resp = self.client.get(reverse('core:home', kwargs={'road_id': self.road.id}))
        self.assertInHTML(f'<div id="road-name" class="row">{self.road.name}</div>', resp.content.decode())

    def test_user_change_road(self):
        '''
        On calculation page, when user clicks to go back to road selection,
        user will be redirected to road selection page 
        '''
        resp = self.client.get(reverse('core:home', kwargs={'road_id': self.road.id}))
        self.assertContains(resp, '<a href="%s">back to road selection</a>' % reverse('core:road'), html=True)

    @unittest.skipIf(os.getenv('SELENIUM_REMOTE'), 'selenium currently failed in pipeline - EOT80')
    @tag('selenium2')
    def test_config_and_road_selection(self):
        '''
        On calculation page, only related configurations to selected road exist
        and on when going back to road selection page, current road is selected by default 
        '''
        sub_occ = SubOccurrenceFactory(name='Spillage')
        right_config = ConfigurationFactory(
            road = self.road,
            sub_occurrence = sub_occ
        )
        # default config has road of M6 Junction x and sub_occurrence of Debris Block Lane
        dummy_config = ConfigurationFactory() 
        dummy_task = '1234'
        session = self.client.session
        session['road_id'] = self.road.id
        session['task_id'] = dummy_task
        session.save()

        obj1 = 1.234
        obj2 = 5.678
        CalculationResult.objects.create(
            task_id=dummy_task,
            config_ids=[right_config.id],
            items=[{
                'lane_closures': right_config.lane_closures,
                'duration': right_config.duration,
                'flow': right_config.flow,
                'frequency': right_config.frequency,
            }],
            objective_1=obj1,
            objective_2=obj2
        )

        self.selenium.get(f'{self.live_server_url}')
        username_input = self.selenium.find_element_by_id('id_username')
        username_input.send_keys(self.user.username)
        password_input = self.selenium.find_element_by_id('id_password')
        password_input.send_keys('123P@s$w0rd')

        self.selenium.find_element_by_tag_name('button').click()

        self.selenium.get(self.live_server_url)
        road_select = Select(self.selenium.find_element_by_id('id_road'))
        road_select.select_by_value(str(self.road.id))
        self.selenium.find_element_by_xpath('//button[@type="submit"]').click()
        
        self.assertEqual(1, len(self.selenium.find_elements_by_xpath('//section[@id="configuration-list"]//div[@class="card"]')))
        self.assertEqual(1, len(self.selenium.find_elements_by_xpath(f'//div[contains(text(), "{sub_occ.name}")]')))
        
        self.selenium.find_element_by_id('calculate_btn').click()
        self.assertEqual(str(obj1), self.selenium.find_element_by_id('result-1').text)        
        self.assertEqual(str(obj2), self.selenium.find_element_by_id('result-2').text)        
        
        self.selenium.find_element_by_xpath('//div[@id="road-header"]//a[@href="/"]').send_keys(keys.Keys.ENTER)
        road_select = Select(self.selenium.find_element_by_id('id_road'))
        self.assertEqual(self.road.name, road_select.first_selected_option.text)        
