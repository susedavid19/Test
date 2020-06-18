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
        parser.add_argument(
            '-s', '--sheet',
            required=True,
            help='Name of active sheet to be processed'
        )
        parser.add_argument(
            '-o', '--output',
            action='store',
            help='Name of output file'
        )
        parser.add_argument(
            '--skiprows',
            action='store',
            nargs='?',
            type=int,
            default=1,
            help='Number of rows to skip in the file before data can be processed'
        )
        parser.add_argument(
            '--header',
            action='store',
            nargs='?',
            type=int,
            default=2,
            help='Number of header rows'
        )
        parser.add_argument(
            '--road',
            action='store',
            nargs='?',
            type=str,
            default='Expressways Test Road',
            help='Name of road these configurations will be put into'
        )


    def handle(self, *args, **options):
        file_path = options['file']
        sheet_name = options['sheet']
        output = options['output']
        skip_rows = options['skiprows']
        header = options['header']
        road_name = options['road']

        if os.path.isfile(file_path):
            dl = DataLoader(output, road_name)
            try:
                dl.load_to_configuration(file_path, sheet_name, skip_rows, header)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'\nFile upload failed. Check content and try again later.\nError: {str(e)}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'\nSuccess: File {file_path} processing completed.'))
        else:
            self.stdout.write(self.style.ERROR(f'\nError: File {file_path} does not exist.'))
