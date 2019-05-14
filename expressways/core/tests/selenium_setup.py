import socket
import os

from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.webdriver.common import desired_capabilities, keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class BaseTestCase(StaticLiveServerTestCase):
    """
    Provides base test class which connects to the Docker
    container running selenium.
    """
    host = '0.0.0.0' # bind to allow external access
    is_remote_driver = os.getenv("SELENIUM_REMOTE", False)

    @classmethod
    def setUpClass(cls):


        super().setUpClass()
        # Set host to externally accessible web server address
        cls.host = socket.gethostbyname(socket.gethostname())
        if cls.is_remote_driver:
            cls.selenium = webdriver.Remote(
                command_executor='http://127.0.0.1:4444/wd/hub',
                desired_capabilities=desired_capabilities.DesiredCapabilities.CHROME,
            )
        else:
            cls.selenium = webdriver.Remote(
                command_executor='http://selenium-hub:4444/wd/hub',
                desired_capabilities=desired_capabilities.DesiredCapabilities.CHROME,
            )
            
        cls.selenium.implicitly_wait(5)

    @classmethod
    def tearDownClass(cls):
        try:
            cls.selenium.quit()
            super().tearDownClass()
        except:
            pass
