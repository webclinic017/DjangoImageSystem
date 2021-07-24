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
import glob
from pathlib import Path, PurePath
"""

"""


def resizer(img_path):
    resize_path = Path("/home/abb/Desktop/resize_pics/")

    new_image = Image.open(img_path)
    convert_image = new_image.convert('RGB')
    file_name = Path(img_path).stem
    convert_image.save(str(PurePath(resize_path, file_name + "_s" + '.webp')), 'webp')
    convert_image.save(str(PurePath(resize_path, file_name + "_m" + '.webp')), 'webp')
    convert_image.save(str(PurePath(resize_path, file_name + "_l" + '.webp')), 'webp')

    print('med is saved')


class Command(BaseCommand):
    help = "this is a necessary command if its the first time you run project" \
           "this will setup picture and slug and etc"


    def initial_setup(self):

        image_list = []
        path = "/home/abb/Desktop/pics"
        for filename in glob.glob(path + '/*.jpg'):  # assuming jpg

            image_list.append(filename)

        start = time.perf_counter()

        # for i in image_list:
        #     resizer(i)


        with concurrent.futures.ProcessPoolExecutor() as executor:
            executor.map(resizer, image_list)

        finish = time.perf_counter()

        # Time Analyze

        print(f'Finished in {round(finish-start, 2)} seconds')

    def handle(self, *args, **options):
        self.initial_setup()


# Multi thread python ,request downloaded ,Finished in 2.27 seconds

