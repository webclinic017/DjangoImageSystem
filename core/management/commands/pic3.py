from django.core.management import BaseCommand
import time
from core.models import ProductPicture, Product, Vendor


class Command(BaseCommand):
    help = "this is a necessary command if its the first time you run project" \
           "this will setup picture and slug and etc"

    def initial_setup(self):

        start = time.perf_counter()

        finish = time.perf_counter()

        # Time Analyze

        print(f'Finished in {round(finish-start, 2)} seconds')


    def handle(self, *args, **options):
        self.initial_setup()
