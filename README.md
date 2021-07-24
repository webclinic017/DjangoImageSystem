# DjangoImageSystem


### Delete ImageField

1. Signals
    ```python
        import os
        import uuid
        
        from django.db import models
        from django.dispatch import receiver
        from django.utils.translation import ugettext_lazy as _
        
        
        class MediaFile(models.Model):
            file = models.FileField(_("file"),
                upload_to=lambda instance, filename: str(uuid.uuid4()))
        
        
        # These two auto-delete files from filesystem when they are unneeded:
        
        @receiver(models.signals.post_delete, sender=MediaFile)
        def auto_delete_file_on_delete(sender, instance, **kwargs):
            """
            Deletes file from filesystem
            when corresponding `MediaFile` object is deleted.
            """
            if instance.file:
                if os.path.isfile(instance.file.path):
                    os.remove(instance.file.path)
        
        
        @receiver(models.signals.pre_save, sender=MediaFile)
        def auto_delete_file_on_change(sender, instance, **kwargs):
            """
            Deletes old file from filesystem
            when corresponding `MediaFile` object is updated
            with new file.
            """
            if not instance.pk:
                return False
        
            try:
                old_file = MediaFile.objects.get(pk=instance.pk).file
            except MediaFile.DoesNotExist:
                return False
        
            new_file = instance.file
            if not old_file == new_file:
                if os.path.isfile(old_file.path):
                    os.remove(old_file.path)
    ```

2. Django Clean up
 - pip install django-cleanup
 
    ```python
       INSTALLED_APPS = (
           'django_cleanup', # should go after your apps
       )
    ```
   
### Complete Resize Download Compress

```python
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
        image_obj_small.name = '{}_{}.{}'.format(file_name, 's', 'webp')
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


```

### Dynamic Path

```python
import os
from django.db import models


def get_small_image_path(instance, filename):
    return os.path.join('products', 'small', str(instance.product.vendor.name), filename)


def get_medium_image_path(instance, filename):
    return os.path.join('products', 'medium', str(instance.product.vendor.name), filename)


def get_large_image_path(instance, filename):
    return os.path.join('products', 'large', str(instance.product.vendor.name), filename)


class ProductPicture(models.Model):
    picture_src = models.URLField()
    state = models.CharField(default='need_resize', max_length=512)
    small = models.ImageField(upload_to=get_small_image_path, blank=True, null=True)
    medium = models.ImageField(upload_to=get_medium_image_path, blank=True, null=True)
    large = models.ImageField(upload_to=get_large_image_path, blank=True, null=True)

```