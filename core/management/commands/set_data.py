from django.core.management import BaseCommand
import json

"""
python manage.py system_warmup -----> call all command
"""


class Command(BaseCommand):
    help = "this is a necessary command if its the first time you run project" \
           "this will setup picture and slug and etc"

    def initial_setup(self):
        try:
            with open('../../../data/digikala.txt', 'r') as json_file:
                my_data = json.load(json_file)
                print(my_data)

        except Exception() as ex:
            self.stdout.write(self.style.ERROR(ex))

    def handle(self, *args, **options):
        self.initial_setup()
