from django.core.management import BaseCommand
import time
from core.models import ProductPicture, Product, Vendor
import requests
import tempfile
from django.core import files
import concurrent.futures

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
        # Stream the image from the url
        response = requests.get(obj.picture_src, stream=True)

        # Was the request OK?
        if response.status_code != requests.codes.ok:
            # Nope, error handling, skip file etc etc etc
            pass

        # Get the filename from the url, used for saving later
        file_name = obj.picture_src.split('/')[-1]

        # Create a temporary file
        lf = tempfile.NamedTemporaryFile()

        # Read the streamed image in sections
        for block in response.iter_content(1024 * 8):

            # If no more file then stop
            if not block:
                break

            # Write image block to temporary file
            lf.write(block)

        # # Create the model you want to save the image to
        # image = Image()

        # Save the temporary image to the model#
        # This saves the model so be sure that it is valid
        obj.large.save(file_name, files.File(lf))

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