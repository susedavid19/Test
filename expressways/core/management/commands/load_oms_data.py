import os

from django.core.management.base import BaseCommand

from expressways.helpers.data_loader import DataLoader

class Command(BaseCommand):
    help = 'Load OMS excel data to database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            action='store',
            help='File name and its location'
        )

    def handle(self, *args, **options):
        file_name = options['file']
        cur_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(cur_path, 'files/', file_name)
        if os.path.isfile(file_path):
            dl = DataLoader()
            dl.load_to_configuration(file_path)
