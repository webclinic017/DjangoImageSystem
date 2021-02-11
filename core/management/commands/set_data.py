from django.core.management import BaseCommand
import json
from ImageService.settings import BASE_DIR
import time
import cProfile
import bz2
import psutil
import os
from meliae import scanner, loader
from guppy import hpy
"""
python manage.py system_warmup -----> call all command
pip install psutil
pip install meliae
pip install guppy3
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

        # Time Analyze

        print(f'Finished in {round(finish-start, 2)} seconds')

        # Cpu Analyze

        # per_cpu = psutil.cpu_percent(interval=1, percpu=True)
        # count_cpu = psutil.cpu_count(logical=False)
        # print(f'CPU count {count_cpu} persentage {per_cpu}')

        # Memory profile

        # h = hpy()
        # print(h.heap())

    def handle(self, *args, **options):
        self.initial_setup()
