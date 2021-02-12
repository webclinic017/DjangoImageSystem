from django.core.management import BaseCommand
import time
from core.models import ProductPicture, Product, Vendor
import requests
import tempfile
from django.core import files
import aria2p
"""
python manage.py system_warmup -----> call all command
pip install psutil
pip install meliae
pip install guppy3
"""
HOST = 'http://localhost'
PORT = 6800
SECRET = ''


class Command(BaseCommand):
    help = "this is a necessary command if its the first time you run project" \
           "this will setup picture and slug and etc"

    def initial_setup(self):

        start = time.perf_counter()

        # Product.objects.filter(pictures__state='need_resize')
        aria = aria2p.API(
            aria2p.Client(
                host=HOST,
                port=PORT,
                secret=SECRET,
            )
        )

        pps = ProductPicture.objects.filter(state='need_resize')
        print(f'you have {pps.count()} not downloaded image')
        for index, pic in enumerate(pps):

            # aria api connect

            # aria.add(pic.picture_src)


            # list downloads
            downloads = aria.get_downloads()

            for download in downloads:
                print(download.name, download.download_speed)


            print(f'{index} image downloaded url => {pic.picture_src}')

            if index > 50:
                break

        finish = time.perf_counter()

        # Time Analyze

        print(f'Finished in {round(finish-start, 2)} seconds')

    def handle(self, *args, **options):
        self.initial_setup()


# single thread python ,request downloaded ,Finished in 12.9 seconds