from django.core.management import BaseCommand
import time
from core.models import ProductPicture, Product, Vendor
import requests
import tempfile
from django.core import files
import concurrent.futures
from django.core.files.base import ContentFile
from PIL import Image
from io import StringIO
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
        response = requests.get(obj.picture_src, stream=True)

        if response.status_code != requests.codes.ok:
            pass

        file_name = obj.picture_src.split('/')[-1]

        lf = tempfile.NamedTemporaryFile()

        for block in response.iter_content(1024 * 8):

            if not block:
                break


            lf.write(block)

        obj.state = 'downloaded'
        obj.large.save(file_name, files.File(lf))

        # self.process_img(obj)

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

from PIL import Image as Img
# import StringIO

# class Images(models.Model):
#     image = models.ImageField()
#
#     def save(self, *args, **kwargs):
#         if self.image:
#             img = Img.open(StringIO.StringIO(self.image.read()))
#             if img.mode != 'RGB':
#                 img = img.convert('RGB')
#             img.thumbnail((self.image.width/1.5,self.image.height/1.5), Img.ANTIALIAS)
#             output = StringIO.StringIO()
#             img.save(output, format='JPEG', quality=70)
#             output.seek(0)
#             self.image= InMemoryUploadedFile(output,'ImageField', "%s.jpg" %self.image.name.split('.')[0], 'image/jpeg', output.len, None)
#         super(Images, self).save(*args, **kwargs)