from django.core.management import call_command
from django.test import TestCase

class TestProformaLoader(TestCase):
    def test_loading_good_case(self):
        call_command('load_oms_data', args=[], kwargs={})
        pass

    def test_loading_invalid_file(self):
        pass
    
    def test_loading_no_file_param(self):
        pass

    