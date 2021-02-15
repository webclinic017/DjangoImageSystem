import os

from django.core.management import BaseCommand
from core.models import ProductPicture, Product, Vendor

"""
python manage.py system_warmup -----> call all command
"""


class Command(BaseCommand):
    help = "this is a necessary command if its the first time you run project" \
           "this will setup picture and slug and etc"

    def initial_setup(self):
        try:
            pics = ProductPicture.objects.all().exclude(state='need_resize')
            for pic in pics:
                pic.state = 'need_resize'
                pic.save()

        except Exception() as ex:
            self.stdout.write(self.style.ERROR(ex))

    def handle(self, *args, **options):
        self.initial_setup()
