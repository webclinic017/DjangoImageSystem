import os
import sys
import time
from configparser import ConfigParser
from datetime import datetime, timedelta
from hashlib import sha256
from io import BytesIO
from random import shuffle

import requests
from PIL import Image
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils import timezone

# resampling filters (also defined in Imaging.h)
NEAREST = NONE = 0
BOX = 4
BILINEAR = LINEAR = 2
HAMMING = 5
BICUBIC = CUBIC = 3
LANCZOS = ANTIALIAS = 1

DOWNLOAD_ROOT = settings.DOWNLOAD_ROOT


class CategoryNoPictureException(Exception):
    pass


class ProductNoMainPictureException(Exception):
    pass


class ProductNoPicturesException(Exception):
    pass


class ProductMainPictureAlreadyResizedException(Exception):
    pass


class ProductPicturesAlreadyResizedException(Exception):
    pass


class CategoryPictureAlreadyException(Exception):
    pass


class DownloadedPictureNotFound(Exception):
    pass


class BaseResizer:
    """Abstract Base Resizer Class that other future Resizers would extend this.

    :raises NotImplementedError: to check if child class has implemented methods or not
    """

    def resize(self, *args):
        raise NotImplementedError("Abstract method not implemented")

    def save(self, *args):
        raise NotImplementedError("Abstract method not implemented")

    def resize_and_save(self, *args):
        raise NotImplementedError("Abstract method not implemented")


class CategoryPictureResizer(BaseResizer):
    """CategoryPictureCompressor Class that resizes categories' picture and save them in media directory"""

    def __init__(self, category):
        """Initial class method that gets category instance and downloads its picture from the `picture` URLField,
        creates a unique name for the picture and keep it for next operations.

        :param category: the category which we are going to work with.
        """

        self.category = category

        if self.category.picture != '':
            response = requests.get(self.category.picture)

            # self.image_name = self.category.picture.split('/')[-1]
            self.image = Image.open(BytesIO(response.content))
        else:
            raise CategoryNoPictureException()

        self.image_name = self.category.name.replace(' ', '-').replace('/', '') + '.' + str(self.image.format.lower())

    def save(self, image, folder_name=100, _format='JPEG'):
        """Saves the image in the given folder_name

        :param image: the image to be saved.
        :param folder_name: the given size to determine which directory image should be saved. Default is the smallest.
        :param _format: the format of is needed for PIL for saving operation. Default is 'JPEG'.
        :return: the path of the file location.
        """

        path = f'categories/{folder_name}x{folder_name}/{self.image_name}'
        save_path = f'{settings.MEDIA_ROOT}{path}'
        image.save(save_path, format=_format)

        return settings.MEDIA_URL + path

    def resize(self, size, resampling=ANTIALIAS):
        """Creates a copy of image, then resizes it with the given size and resampling (Optional).

        :param size: Tuple of width & height
        :param resampling: Optional resampling method that is used for resizeing. More resampling methods are listed
            first lines of the current file.
        :return: the resized image
        """

        #   n * n
        #
        # ratio = min(n / width, n / height)
        # new_size = (int(width * ratio), height * ratio)
        # image = image.resize(new_size, Image.LANCZOS)

        image = self.image.copy()
        image.thumbnail(size, resampling)
        return image

    def resize_and_save(self, resampling=ANTIALIAS):
        """The function that is used in Category.save().
        creates dictionary of paths. Keys are sizes and values are list of images.
        resizes the images with the demanded sizes, saves them and appends them to paths dictionary

        :return: paths dictionary
        """

        paths = {
            '100x100': '',
            '128x128': '',
            '216x216': '',
        }
        _format = self.image.format

        # 216 * 216

        size = (216, 216)
        image = self.resize(size, resampling=resampling)
        path = self.save(image, 216, _format)
        paths['216x216'] = path

        # 128 * 128

        size = (128, 128)
        image = self.resize(size, resampling=resampling)
        path = self.save(image, 128, _format)
        paths['128x128'] = path

        # 100 * 100

        size = (100, 100)
        image = self.resize(size, resampling=resampling)
        path = self.save(image, 100, _format)
        paths['100x100'] = path

        return paths


class ProductPictureResizer(BaseResizer):
    """ProductPictureCompressor that compresses the product main_picture and pictures list, then saves them in the media
    directory.

    This are the sizes:

        118 - > xsmall
        156 - > small
        182 - > medium
        192 - > large
        328 - > xlarge
        562 - > xxlarge
    """

    def __init__(self, product, main=False):
        """Initial class method that gets the product and does the compression for main_picture or pictures list

        :param product: the product which we are going to work with.
        :param main: determines that self is working with main_picture or pictures list.
        """

        self.product = product

        if main:
            if self.product.main_picture != '':
                if self.product.main_picture['small'] != '':
                    if self.product.main_picture['small'].startswith('/'):
                        raise ProductMainPictureAlreadyResizedException()

                    # response = requests.get(self.product.main_picture['small'])

                    # self.image_name = self.category.picture.split('/')[-1]
                    # self.main_image = Image.open(BytesIO(response.content))
                    try:
                        self.main_image = Image.open(f'{DOWNLOAD_ROOT}products/{product.id}/main_picture')

                    except FileNotFoundError as _:
                        raise DownloadedPictureNotFound

                else:
                    raise ProductNoMainPictureException()
            else:
                raise ProductNoMainPictureException()

        else:
            if len(self.product.pictures) > 0:
                self.images = list()
                # self.images.append(self.main_image)

                count = 1
                for pic in self.product.pictures:
                    if pic['xsmall'].startswith('/') or pic['xsmall'] == '':
                        continue

                    # response = requests.get(pic['xsmall'])
                    # self.images.append(Image.open(BytesIO(response.content)))
                    self.images.append(Image.open(f'{DOWNLOAD_ROOT}products/{product.id}/{count}'))
                    count += 1

                if len(self.images) == 0:
                    raise ProductPicturesAlreadyResizedException()

    def save(self, image, folder_name='xsmall', image_name='unnamed-picture.jpg', _format='JPEG'):
        """Saves the image in the given folder_name with given image_name

        :param image: the image we're going to save.
        :param folder_name: the folder where we want to save image.
        :param image_name: the file name we want to use.
        :param _format: the image format
        :return: the path of saved image.
        """

        path = os.path.join('products', folder_name)
        save_path = os.path.join(settings.MEDIA_ROOT, path)
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        save_path = os.path.join(save_path, image_name)

        image.save(save_path, format=_format)

        return os.path.join(settings.MEDIA_URL, os.path.join(path, image_name))

    def resize(self, image, size, resampling=ANTIALIAS):
        """Resizes the copy of given image with the size and the resampling method.

        :param image: the original image.
        :param size: Tuple of width and height for resizing.
        :param resampling: the resampling method. See more on first lines of the file.
        :return: the Resized images
        """

        image = image.copy()
        width, height = image.size

        ratio = min(size[0] / width, size[1] / height)
        new_size = (int(width * ratio), int(height * ratio))
        image = image.resize(new_size, Image.ANTIALIAS)

        return image

    def resize_and_save_main(self, resampling=ANTIALIAS):
        """This method is used in Product.save() method when `main=True`. Compresses the product's main_picture
        and saves it.

        :param resampling: the resampling method. See more on first lines of the file.
        :return: returns the path of saved main images.
        """

        paths = {
            'xxlarge': "",
            'xlarge': "",
            'large': "",
            'medium': "",
            'small': "",
            'xsmall': ""
        }

        folder_name = f'{self.product.id}'
        image_name = 'main' + f'.{self.main_image.format.lower()}'
        _format = self.main_image.format

        # 562 * 562 -> xxlarge
        size = (562, 562)
        image = self.resize(self.main_image, size, resampling=resampling)
        path = self.save(image, os.path.join(folder_name, 'xxlarge'), image_name, _format)
        paths['xxlarge'] = path
        image.close()

        # 328 * 328 -> xlarge
        size = (328, 328)
        image = self.resize(self.main_image, size, resampling=resampling)
        path = self.save(image, os.path.join(folder_name, 'xlarge'), image_name, _format)
        paths['xlarge'] = path
        image.close()

        # 192 * 192 -> large
        size = (192, 192)
        image = self.resize(self.main_image, size, resampling=resampling)
        path = self.save(image, os.path.join(folder_name, 'large'), image_name, _format)
        paths['large'] = path
        image.close()

        # 182 * 182 -> medium
        size = (182, 182)
        image = self.resize(self.main_image, size, resampling=resampling)
        path = self.save(image, os.path.join(folder_name, 'medium'), image_name, _format)
        paths['medium'] = path
        image.close()

        # 156 * 156 -> small
        size = (156, 156)
        image = self.resize(self.main_image, size, resampling=resampling)
        path = self.save(image, os.path.join(folder_name, 'small'), image_name, _format)
        paths['small'] = path
        image.close()

        # 118 * 118 -> xsmall
        size = (118, 118)
        image = self.resize(self.main_image, size, resampling=resampling)
        path = self.save(image, os.path.join(folder_name, 'xsmall'), image_name, _format)
        paths['xsmall'] = path
        image.close()

        self.main_image.close()

        return paths

    def resize_and_save(self, resampling=ANTIALIAS):
        """This method is used in Product.save() method when `main=False`. Compresses the product's pictures and saves
        them.

        :return: returns the path of saved main images.
        """

        pictures = list()

        folder_name = f'{self.product.id}'
        for index in range(len(self.images)):
            image_to_process = self.images[index]
            _format = image_to_process.format
            image_name = str(index + 1) + f'.{image_to_process.format.lower()}'

            paths = dict()

            # 562 * 562 -> xxlarge
            size = (562, 562)
            image = self.resize(image_to_process, size, resampling=resampling)
            path = self.save(image, os.path.join(folder_name, 'xxlarge'), image_name, _format)
            paths.update({'xxlarge': path})
            image.close()

            # 328 * 328 -> xlarge
            size = (328, 328)
            image = self.resize(image_to_process, size, resampling=resampling)
            path = self.save(image, os.path.join(folder_name, 'xlarge'), image_name, _format)
            paths.update({'xlarge': path})
            image.close()

            # 182 * 182 -> medium
            size = (182, 182)
            image = self.resize(image_to_process, size, resampling=resampling)
            path = self.save(image, os.path.join(folder_name, 'medium'), image_name, _format)
            paths.update({'medium': path})
            image.close()

            # 118 * 118 -> xsmall
            size = (118, 118)
            image = self.resize(image_to_process, size, resampling=resampling)
            path = self.save(image, os.path.join(folder_name, 'xsmall'), image_name, _format)
            paths.update({'xsmall': path})
            image.close()

            pictures.append(paths)

            self.images[index].close()

        return pictures


def print_progress_bar(iteration_main=0, iteration_sub=0, total_main=100, total_sub=100, prefix_main='',
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
        sys.stdout.write('\r\r%s |%s| %s%% %s\t%s |%s| %s%% %s  %s' % (
            prefix_main, bar_main, percent_main, suffix_main, prefix_sub, bar_sub, percent_sub, suffix_sub,
            print_end), )

    else:
        sys.stdout.write('\r\r%s |%s| %s%% %s  %s' % (
            prefix_main, bar_main, percent_main, suffix_main, print_end), )

    if iteration_main == total_main:
        sys.stdout.write('\n')


def config_reader(file_name=os.path.join(settings.BASE_DIR, 'api/management/commands/config.ini'),
                  section='download'):
    conf = ConfigParser()
    conf.read(file_name)
    return conf


def token_generator(user):
    epoch = str(time.mktime(datetime.now().timetuple()))
    hashed_word = sha256(default_token_generator.make_token(user).encode()).hexdigest()
    raw_token = list(str(epoch + hashed_word))
    shuffle(raw_token)
    return ''.join(raw_token).replace('.', 'S')[:50]


def get_n_days_ago(n=30):
    today = timezone.now()
    n_days_ago = today - timedelta(days=n)
    return n_days_ago
