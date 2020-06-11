import os

from django.core.management.base import BaseCommand

from expressways.helpers.data_loader import DataLoader

class Command(BaseCommand):
    help = '''
        Load OMS excel data to database.
        Run the command as "manage.py load_oms_data <file name with full path and extension>"
        Example: python3 manage.py load_oms_data /data/expressways/core/management/files/OMS.xlsx
    '''

    def add_arguments(self, parser):
        parser.add_argument(
            '-f', '--file',
            required=True,
            help='Name of file with full path and extension'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        if os.path.isfile(file_path):
            dl = DataLoader()
            try:
                dl.load_to_configuration(file_path)
            except:
                self.stdout.write(self.style.ERROR('Error: File upload failed. Check content and try again later.'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Success: File {file_path} is now uploaded.'))
        else:
            self.stdout.write(self.style.ERROR(f'Error: File {file_path} does not exist.'))
