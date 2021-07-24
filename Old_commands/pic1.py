from django.core.management import BaseCommand
import time
from core.models import ProductPicture, Product, Vendor
import requests
import tempfile
from django.core import files
# import aria2p
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

        # Product.objects.filter(pictures__state='need_resize')

        pps = ProductPicture.objects.filter(state='need_resize')
        print(f'you have {pps.count()} not downloaded image')
        for index, pic in enumerate(pps):
            # Stream the image from the url
            response = requests.get(pic.picture_src, stream=True)

            # Was the request OK?
            if response.status_code != requests.codes.ok:
                # Nope, error handling, skip file etc etc etc
                continue

            # Get the filename from the url, used for saving later
            file_name = pic.picture_src.split('/')[-1]

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
            pic.large.save(file_name, files.File(lf))

            print(f'{index} image downloaded url => {pic.picture_src}')

            if index > 50:
                break

        finish = time.perf_counter()

        # Time Analyze

        print(f'Finished in {round(finish-start, 2)} seconds')

    def handle(self, *args, **options):
        self.initial_setup()


# single thread python ,request downloaded ,Finished in 12.9 seconds