import os

from django.core.management import BaseCommand


"""
python manage.py system_warmup -----> call all command
"""


class Command(BaseCommand):
    help = "this is a necessary command if its the first time you run project" \
           "this will setup picture and slug and etc"

    def initial_setup(self):
        try:
            os.system('python manage.py download')
            os.system('python manage.py resize')
            os.system('python manage.py compress')
        except Exception() as ex:
            self.stdout.write(self.style.ERROR(ex))


    def handle(self, *args, **options):
        self.initial_setup()
