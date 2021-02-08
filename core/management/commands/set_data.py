from django.core.management import BaseCommand
import json
from ImageService.settings import BASE_DIR
import time
import bz2
"""
python manage.py system_warmup -----> call all command
"""


class Command(BaseCommand):
    help = "this is a necessary command if its the first time you run project" \
           "this will setup picture and slug and etc"

    def initial_setup(self):

        start = time.perf_counter()

        data_address = str(BASE_DIR) + '/data/okala-images.json'
        with open(data_address, 'r', encoding='utf-8') as json_file:
            my_data = json.load(json_file)
            # print(my_data)

        finish = time.perf_counter()

        print(f'Finished in {round(finish-start, 2)} seconds')

    def handle(self, *args, **options):
        self.initial_setup()
