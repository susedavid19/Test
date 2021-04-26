import os
from io import StringIO
from django.core.management import call_command
from django.test import TestCase

from expressways.core.models import OccurrenceConfiguration, EffectIntervention

class TestProformaLoader(TestCase):
    def setUp(self):
        '''
        Using specifically created excel file below for test, of which 1 sheet ie. Test Sheet 
        has 2 rows of valid records and one of them with valid effect intervention.
        There is also another sheet ie. Invalid Sheet with invalid record that has 
        blank lane closure and speed value.
        '''
        file_path = os.path.dirname(os.path.abspath(__file__))
        self.test_file = os.path.join(file_path, 'data/Test_Proforma.xls')
        self.test_sheet = 'Test Sheet'
        self.invalid_sheet = 'Invalid Sheet'
        self.io = StringIO()

    def test_loading_good_case(self):
        '''
        Given the file and sheet names supplied are valid
        When running the load_oms_data management command
        Then expected number of configuration records get added
        '''
        self.assertEqual(0, OccurrenceConfiguration.objects.all().count())
        self.assertEqual(0, EffectIntervention.objects.all().count())        
        call_command('load_oms_data', file=self.test_file, sheet=self.test_sheet)
        self.assertEqual(2, OccurrenceConfiguration.objects.all().count())        
        self.assertEqual(1, EffectIntervention.objects.all().count())        

    def test_running_multiple(self):
        '''
        Given the file and sheet names supplied are valid and the same as before
        When re-running the load_oms_data management command
        Then no new number of configuration records get added
        '''
        call_command('load_oms_data', file=self.test_file, sheet=self.test_sheet)        
        self.assertEqual(2, OccurrenceConfiguration.objects.all().count())        
        call_command('load_oms_data', file=self.test_file, sheet=self.test_sheet)        
        self.assertEqual(2, OccurrenceConfiguration.objects.all().count())        

    def test_loading_invalid_file(self):
        '''
        Given the file is invalid
        When running the load_oms_data management command
        Then no records get added and command error is raised
        '''
        invalid_file = '/data/somerubbish.file'
        call_command('load_oms_data', file=invalid_file, sheet=self.test_sheet, stdout=self.io)        
        self.assertEqual(0, OccurrenceConfiguration.objects.all().count())   
        self.assertIn(f'Error: File {invalid_file} does not exist.', self.io.getvalue())
    
    def test_loading_invalid_data(self):
        '''
        Given the file is valid, but the data within is invalid
        When running the load_oms_data management command
        Then no record gets added and command error is raised
        '''
        call_command('load_oms_data', file=self.test_file, sheet=self.invalid_sheet, stdout=self.io)        
        self.assertEqual(0, OccurrenceConfiguration.objects.all().count())   
        self.assertIn('File upload failed. Check content and try again later.', self.io.getvalue())

    