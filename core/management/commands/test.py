from django.core.management import BaseCommand
import time
from core.models import ProductPicture, Product, Vendor
import requests
import tempfile
from django.core import files
import concurrent.futures
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.base import ContentFile
from PIL import Image
from io import StringIO, BytesIO

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
    def make_thumbnail(image, size=(100, 100)):
        """Makes thumbnails of given size from given image"""

        im = Image.open(image)

        im.convert('RGB')  # convert mode

        im.thumbnail(size)  # resize image

        thumb_io = BytesIO()  # create a BytesIO object

        im.save(thumb_io, 'webp', quality=85)  # save image to BytesIO object

        thumbnail = files.File(thumb_io, name=image.name)  # create a django friendly File object

        return thumbnail


    def download(self, obj):
        response = requests.get(obj.picture_src, stream=True)

        if response.status_code != requests.codes.ok:
            print(response)

        file_name = obj.picture_src.split('/')[-1]

        lf = tempfile.NamedTemporaryFile()

        for block in response.iter_content(1024 * 8):

            if not block:
                break


            lf.write(block)

        image_obj_small = files.File(lf)
        image_obj_large = files.File(lf)
        image_obj_medium = files.File(lf)
        image_obj_small.name = file_name + '_s'
        image_obj_large.name = file_name + '_l'
        image_obj_medium.name = file_name + '_m'

        small_img = self.make_thumbnail(image_obj_small, size=(100, 100))
        thumbnail = self.make_thumbnail(image_obj_medium, size=(128, 128))
        large_img = self.make_thumbnail(image_obj_large, size=(216, 216))

        obj.large = large_img
        obj.small = small_img
        obj.medium = thumbnail
        obj.save()

        print(f' image downloaded url => {obj.picture_src}')


    def initial_setup(self):

        start = time.perf_counter()

        # Product.objects.filter(pictures__state='need_resize')

        pps = list(ProductPicture.objects.filter(state='need_resize', product__vendor__name='digikala')[:50])
        # pps = list(ProductPicture.objects.filter(state='need_resize').values_list('picture_src', flat=True)[:50])
        print(f'you have {len(pps)} not downloaded image')

        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(self.download, pps)

        finish = time.perf_counter()

        # Time Analyze

        print(f'Finished in {round(finish-start, 2)} seconds')

    def handle(self, *args, **options):
        self.initial_setup()

