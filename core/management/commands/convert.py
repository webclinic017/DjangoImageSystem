from django.core.management import BaseCommand
import time
from core.models import ProductPicture, Product, Vendor
import requests
import tempfile
from django.core import files
import concurrent.futures
from PIL import Image
import os
"""
python manage.py system_warmup -----> call all command
pip install psutil
pip install meliae
pip install guppy3
"""


class Command(BaseCommand):
    help = "this is a necessary command if its the first time you run project" \
           "this will setup picture and slug and etc"

    @staticmethod
    def download(obj):
        response = requests.get(obj.picture_src, stream=True)


        if response.status_code != requests.codes.ok:
            pass

        file_name = obj.picture_src.split('/')[-1]
        # file_name = '{}.{}'.format(file_name, 'webp')

        lf = tempfile.NamedTemporaryFile()
        # lf = tempfile.NamedTemporaryFile(suffix='.webp')

        for block in response.iter_content(1024 * 8):

            if not block:
                break

            lf.write(block)

        before_ = str(os.path.getsize(lf.name))

        im = Image.open(lf.name).convert('RGB')

        im.save(lf.name, 'webp')
        im.close()
        after_ = str(os.path.getsize(lf.name))

        obj.large.save(file_name, files.File(lf))

        print(f'{before_} change to {after_}')
        print(f' image downloaded url => {obj.picture_src}')

    def initial_setup(self):

        start = time.perf_counter()

        # Product.objects.filter(pictures__state='need_resize')

        pps = list(ProductPicture.objects.filter(state='need_resize')[:50])
        # pps = list(ProductPicture.objects.filter(state='need_resize').values_list('picture_src', flat=True)[:50])
        print(f'you have {len(pps)} not downloaded image')

        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(self.download, pps)

        finish = time.perf_counter()

        # Time Analyze

        print(f'Finished in {round(finish-start, 2)} seconds')

    def handle(self, *args, **options):
        self.initial_setup()


# Multi thread python ,request downloaded ,Finished in 2.27 seconds