import glob
import os
from shutil import which, copy, move

from PIL import Image
from django.conf import settings
from django.core.management.base import BaseCommand

from api.models import ProductPicturesStatus

DIRECTORY = settings.BASE_DIR
MEDIA_ROOT = settings.MEDIA_ROOT


class Command(BaseCommand):
    # Print iterations progress
    def print_progress_bar(self, iteration_main=0, iteration_sub=0, total_main=100, total_sub=100, prefix_main='',
                           prefix_sub='',
                           suffix_main='', suffix_sub='', decimals_main=3, decimal_sub=1,
                           length=25, fill='█',
                           print_end="\r", single=False):
        """
        Call in a loop to create terminal progress bar
        @params:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : positive number of decimals in percent complete (Int)
            length      - Optional  : character length of bar (Int)
            fill        - Optional  : bar fill character (Str)
            print_end    - Optional  : end character (e.g. "\r", "\r\n") (Str)
        """
        # Print New Line on Complete

        percent_main = ("{0:." + str(decimals_main) + "f}").format(100 * (iteration_main / float(total_main)))
        filled_length_main = int(length * iteration_main // total_main)
        bar_main = fill * filled_length_main + '-' * (length - filled_length_main)

        if not single:
            percent_sub = ("{0:." + str(decimal_sub) + "f}").format(100 * (iteration_sub / float(total_sub)))
            filled_length_sub = int(length * iteration_sub // total_sub)
            bar_sub = fill * filled_length_sub + '-' * (length - filled_length_sub)
            print('\r\r%s |%s| %s%% %s\t%s |%s| %s%% %s  ' % (
                prefix_main, bar_main, percent_main, suffix_main, prefix_sub, bar_sub, percent_sub, suffix_sub),
                  end=print_end)

        else:
            print('\r\r%s |%s| %s%% %s  ' % (
                prefix_main, bar_main, percent_main, suffix_main),
                  end=print_end)

        if iteration_main == total_main:
            self.stdout.write(self.style.SUCCESS('\nFinished'))

    @staticmethod
    def compress(file):
        file_name = file.split('/')[-1].split('.')[:-1]
        path_without_extension = file.split('.')[:-1]
        path_without_extension = '.'.join(path_without_extension)

        if file_name == '':
            return False

        extension = file.split('.')[-1]
        try:
            im = Image.open(file).convert('RGB')
            im.save(f'{path_without_extension}.webp', 'webp')
            im.close()

            out = 0
            if extension.lower() == 'png':
                out = os.system(f'pngquant -f --ext .png --skip-if-larger {file}')

            elif extension.lower() == 'jpeg' or extension.lower() == 'jpg':
                out = os.system(f'jpegoptim -q -m70 {file}')

            else:
                return False

            if out != 0:
                return False

            return True

        except Exception as e:
            return False

    def handle(self, *args, **options):

        if which('pngquant') is not None and which('jpegoptim') is not None:

            status_objects = ProductPicturesStatus.objects.filter(needs_downloading=False, needs_resizing=False,
                                                                  needs_compression=True).all()

            total_products = len(status_objects)

            if total_products == 0:
                self.stdout.write('No compression is required exiting')

            count_p = 0

            self.print_progress_bar(0, 0, 1, 1, 'Total Products',
                                    'Each Product', 'Done Compressing', 'Done Compressing')

            for status_object in status_objects:
                product = status_object.product
                total_images = len(product.pictures) * len(settings.PICTURES_SIZES) + len(settings.MAIN_PICTURE_SIZES)
                count_i = 0
                local_errors = 0

                backup_files = []

                # main_picture
                for picture in product.main_picture.values():
                    if picture == '':
                        count_i += 1
                        continue

                    # shell = os.system(f'cp {DIRECTORY}{picture} {DIRECTORY}{picture}.bak')
                    try:
                        copy(f'{DIRECTORY}{picture}', f'{DIRECTORY}{picture}.bak')

                    except:
                        print(f'Error occured on {product.pk}')
                        if not picture.startswith('/media'):
                            status_object.needs_downloading = True
                            status_object.needs_resizing = False
                            status_object.needs_compression = False

                        else:
                            status_object.needs_compression = None

                        status_object.save()
                        continue

                    backup_files.append(f'{DIRECTORY}{picture}')

                    result = Command.compress(f'{DIRECTORY}{picture}')

                    if not result:
                        local_errors += 1
                        break

                    else:
                        count_i += 1
                        self.print_progress_bar(count_p, count_i, total_products, total_images, 'Total Products',
                                                'Each Product', 'Done Compressing', 'Done Compressing')

                if local_errors:
                    count_p += 1
                    status_object.needs_compression = None
                    status_object.save()

                    for backup_file in backup_files:
                        # shell = os.system(f'mv {DIRECTORY}{backup_file}.bak {DIRECTORY}{backup_file}')
                        move(f'{backup_file}.bak', f'{backup_file}')

                    del backup_files
                    continue

                # pictures
                for picture in product.pictures:
                    for size in picture.values():
                        if size == '':
                            count_i += 1
                            continue

                        # shell = os.system(f'cp {DIRECTORY}{size} {DIRECTORY}{size}.bak')
                        try:
                            copy(f'{DIRECTORY}{size}', f'{DIRECTORY}{size}.bak')

                        except FileNotFoundError:
                            print(f'E error dad ke :D {product.id} Alan Dorostesh mikonan haha')
                            product.pictures = []
                            product.save()

                            continue

                        backup_files.append(f'{DIRECTORY}{size}')
                        result = Command.compress(f'{DIRECTORY}{size}')

                        if not result:
                            local_errors += 1
                            break

                        else:
                            count_i += 1
                            self.print_progress_bar(count_p, count_i, total_products, total_images, 'Total Products',
                                                    'Each Product', 'Done Compressing', 'Done Compressing')

                    if local_errors:
                        status_object.needs_compression = None
                        status_object.save()

                        for backup_file in backup_files:
                            move(f'{backup_file}.bak', f'{backup_file}')

                        backup_files = []
                        break

                status_object.needs_compression = False
                status_object.save()
                count_p += 1

                self.print_progress_bar(count_p, count_i, total_products, total_images, 'Total Products',
                                        'Each Product', 'Done Compressing', 'Done Compressing')

            self.stdout.write(self.style.WARNING('Removing backup files'))
            path = os.path.join(MEDIA_ROOT, 'products/*/*/*.bak')
            backup_files = glob.glob(path)

            total_backups = len(backup_files)
            progressed = 0

            self.print_progress_bar(iteration_main=0, total_main=100,
                                    prefix_main='Total Backups',
                                    suffix_main='Removed', single=True)

            for backup_file in backup_files:
                os.remove(backup_file)

                progressed += 1
                self.print_progress_bar(iteration_main=progressed, total_main=total_backups,
                                        prefix_main='Total Backups',
                                        suffix_main='Removed', single=True)

        else:
            self.stdout.write(self.style.ERROR('pngquant or jpegoptim is not installed.'))
