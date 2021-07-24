from django.core.management import BaseCommand
import json
from ImageService.settings import BASE_DIR
import time

from core.models import ProductPicture, Product, Vendor


class Command(BaseCommand):
    help = "this is a necessary command if its the first time you run project" \
           "this will setup picture and slug and etc"

    def initial_setup(self):

        start = time.perf_counter()

        vendor, created = Vendor.objects.get_or_create(name='digikala')

        data_address = str(BASE_DIR) + '/data/digikala-images.json'
        with open(data_address, 'r', encoding='utf-8') as json_file:
            my_data = json.load(json_file)
            for index, link in enumerate(my_data):
                pp = ProductPicture.objects.create(
                    picture_src=link
                )
                Product.objects.create(
                    pictures=pp,
                    vendor=vendor
                )
                print(f'{index} obj created')

        finish = time.perf_counter()

        # Time Analyze

        print(f'Finished in {round(finish-start, 2)} seconds')

    def handle(self, *args, **options):
        self.initial_setup()

