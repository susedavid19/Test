from django.core.management import call_command
from django.test import TestCase

class TestProformaLoader(TestCase):
    def setUp(self):
        self.test_file = '/data/expressways/core/tests/data/Test_Proforma.xlsx'
        self.test_sheet = 'Test Sheet'

    def test_loading_good_case(self):
        call_command('load_oms_data', file=self.test_file, sheet=self.test_sheet)
        pass

    def test_loading_invalid_file(self):
        pass
    
    def test_loading_no_file_param(self):
        pass

    