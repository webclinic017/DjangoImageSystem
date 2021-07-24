from django.core.management import BaseCommand
import time
from core.models import ProductPicture, Product, Vendor
import requests
import tempfile, shutil
from django.core import files
import concurrent.futures
from django.core.files.base import ContentFile
from PIL import Image
from io import StringIO

"""
you have 50 not downloaded image
First Try Finished in 13.9 seconds
Second Try Finished in 12.94 seconds
Third Try Finished in 12.51 seconds
"""


def download(obj):
    response = requests.get(obj.picture_src, stream=True)

    if response.status_code != requests.codes.ok:
        pass

    file_name = obj.picture_src.split('/')[-1]

    lf = tempfile.NamedTemporaryFile()

    for block in response.iter_content(1024 * 8):

        if not block:
            break

        lf.write(block)

    IMAGES_PATH = '/home/amirbahador/Desktop/Pics/'
    shutil.copy(lf.name, IMAGES_PATH + file_name)


class Command(BaseCommand):
    help = "this is a necessary command if its the first time you run project" \
           "this will setup picture and slug and etc"

    @staticmethod
    def process_img(obj):

        new_image = Image.open(StringIO(obj.large.read()))
        convert_image = new_image.convert('RGB')
        file_name = str(obj.large.name).split('/')[-1]
        convert_image.save(file_name, 'webp')

        new_image.name = file_name + '_s'
        obj.small = new_image
        obj.save()
        print('small is saved')
        new_image.name = file_name + '_m'
        obj.medium = new_image
        obj.state = 'published'
        obj.save()
        print('med is saved')


    def download(self, obj):
        print("hi")
        response = requests.get(obj.picture_src, stream=True)

        if response.status_code != requests.codes.ok:
            print(response.status_code)

        file_name = obj.picture_src.split('/')[-1]

        lf = tempfile.NamedTemporaryFile()
        # lf = tempfile.NamedTemporaryFile()

        for block in response.iter_content(1024 * 8):

            if not block:
                break


            lf.write(block)

        IMAGES_PATH = '/home/amirbahador/Desktop/Pics/'
        shutil.copy(lf.name, IMAGES_PATH+file_name)

        # obj.state = 'downloaded'
        # obj.large.save(file_name, files.File(lf))

        # self.process_img(obj)

        print(f' image downloaded url => {obj.picture_src}')



    def initial_setup(self):

        start = time.perf_counter()

        # Product.objects.filter(pictures__state='need_resize')

        pps = list(ProductPicture.objects.filter(state='need_resize')[:50])
        # pps = list(ProductPicture.objects.filter(state='need_resize').values_list('picture_src', flat=True)[:50])
        print(f'you have {len(pps)} not downloaded image')

        with concurrent.futures.ProcessPoolExecutor() as executor:
            executor.map(download, pps)

        finish = time.perf_counter()

        # Time Analyze

        print(f'Finished in {round(finish-start, 2)} seconds')

    def handle(self, *args, **options):
        self.initial_setup()


# Multi thread python ,request downloaded ,Finished in 2.27 seconds

