import concurrent.futures
import os
from shutil import which

import aria2p
from django.conf import settings
from django.core.management.base import BaseCommand

from api.models import ProductPicturesStatus, Vendor, ProductOriginalPictures
from api.utils import config_reader

DOWNLOAD_DIRECTORY = os.path.join(settings.BASE_DIR, 'downloads/products/')
HOST = 'http://localhost'
PORT = 6800
SECRET = ''

PROXY_ADDRESS = ''


class DownloadFailedException(Exception):
    pass


class ProductHasNoPicturesException(Exception):
    pass


class ResourceNotFoundException(Exception):
    pass


class Command(BaseCommand):

    def __init__(self):
        self.conf = config_reader()
        super().__init__()

    def download(self, vendor_id, aria, proxy_for):

        vendor_name = Vendor.objects.get(pk=vendor_id).name
        self.stdout.write(f'Downloader for {vendor_name} started')

        product_original_pictures = ProductOriginalPictures.objects \
            .filter(vendor_id=vendor_id, product__pictures_status__needs_downloading=True)

        # print(product_original_pictures)
        total_vendor_product_download = product_original_pictures.count()
        progressed = 0

        for product_original_picture in product_original_pictures:
            product = product_original_picture.product
            picture_status = product.pictures_status

            main_picture = product_original_picture.main_picture
            pictures = product_original_picture.pictures

            try:
                downloads = []
                if vendor_name not in proxy_for:
                    if main_picture != '':
                        downloads = [
                            aria.add_uris(
                                [main_picture],
                                options={
                                    'dir': DOWNLOAD_DIRECTORY + f'{product.id}',
                                    'out': 'main_picture',
                                    'max-concurrent-downloads': 4,
                                    'split': 4,
                                    'timeout': 15,
                                },
                            )]

                    count = 1
                    if type(pictures) == list and len(pictures) > 0:
                        for picture in pictures:
                            downloads.append(
                                aria.add_uris(
                                    [picture],
                                    options={
                                        'dir': DOWNLOAD_DIRECTORY + f'{product.id}',
                                        'out': f'{count}',
                                        'max-concurrent-downloads': 4,
                                        'split': 4,
                                        'timeout': 15,
                                    },
                                )
                            )
                        count += 1

                else:
                    if main_picture != '':
                        downloads = [
                            aria.add_uris(
                                [main_picture],
                                options={
                                    'dir': DOWNLOAD_DIRECTORY + f'{product.id}',
                                    'out': 'main_picture',
                                    'max-concurrent-downloads': 4,
                                    'split': 4,
                                    'timeout': 20,
                                    'http-proxy': PROXY_ADDRESS,
                                },
                            )]

                    count = 1
                    if type(pictures) == list and len(pictures) > 0:
                        for picture in pictures:
                            downloads.append(
                                aria.add_uris(
                                    [picture],
                                    options={
                                        'dir': DOWNLOAD_DIRECTORY + f'{product.id}',
                                        'out': f'{count}',
                                        'max-concurrent-downloads': 4,
                                        'split': 4,
                                        'timeout': 20,
                                        'http-proxy': PROXY_ADDRESS,
                                    },
                                )
                            )
                        count += 1

                download_is_active = True if len(downloads) > 0 else False

                completed = 0

                if len(downloads) == 0:
                    raise ProductHasNoPicturesException()

                while download_is_active:
                    for i in range(len(downloads)):
                        if downloads[i].live.has_failed:
                            if downloads[i].live.error_code == '3':
                                raise ResourceNotFoundException()

                            raise DownloadFailedException()

                        if downloads[i].live.status == 'complete':
                            completed += 1

                        if len(downloads) == completed:
                            download_is_active = False
                            break

                del downloads

            except ResourceNotFoundException as _:
                self.stdout.write(
                    self.style.ERROR(f'Resource not found: {product.id}, Vendor {vendor_name}'))
                picture_status.needs_downloading = None
                picture_status.needs_resizing = False
                picture_status.needs_compression = False
                picture_status.save()
                progressed += 1
                continue

            except ProductHasNoPicturesException as _:
                self.stdout.write(
                    self.style.ERROR(
                        f'Product has no pictures to download: Product id {product}, Vendor {vendor_name}. Skipping...'))
                picture_status.needs_downloading = None
                picture_status.needs_resizing = False
                picture_status.needs_compression = False
                picture_status.save()
                progressed += 1
                continue

            except (DownloadFailedException, Exception):
                self.stdout.write(
                    self.style.ERROR(f'Error on downloading pictures: product_id {product.id}, Vendor: {vendor_name}'))
                picture_status.needs_downloading = None
                picture_status.needs_resizing = False
                picture_status.needs_compression = False
                picture_status.save()
                progressed += 1
                continue

            picture_status.needs_downloading = False
            picture_status.needs_resizing = True
            picture_status.needs_compression = False
            picture_status.save()

            progressed += 1
            percentage = progressed / total_vendor_product_download * 100
            self.stdout.write(f'{vendor_name}: {percentage:0.3f}%')

        self.stdout.write(self.style.SUCCESS(f'Downloader for {vendor_name} finished successfully'))

    def add_arguments(self, parser):

        parser.add_argument('-vendors', type=str, nargs='*',
                            default=self.conf['download']['vendors'].split() if self.conf['download'][
                                                                                    'vendors'].split() != [
                                                                                    '[]'] else [],
                            help='Takes vendors')

        parser.add_argument('-exclude', type=str, nargs='*',
                            default=self.conf['download']['exclude'].split() if self.conf['download'][
                                                                                    'exclude'].split() != [
                                                                                    '[]'] else [],
                            help='Excludes')

        parser.add_argument('-proxy_for', type=str, nargs='*',
                            default=self.conf['download']['proxy_for'].split() if self.conf['download'][
                                                                                      'proxy_for'].split() != [
                                                                                      '[]'] else [],
                            help='Takes list of vendors that need proxy')

        parser.add_argument('retry', type=str, nargs='?',
                            default='retry' if self.conf['download']['method'] == 'retry' else None,
                            help='Retries to resize those pictures that got error.')

    def handle(self, *args, **options):
        global PROXY_ADDRESS

        if settings.INTERFACE_DOWNLOAD_IMAGES:

            vendors_filter = options.get('vendors')
            exclude = options.get('exclude')
            proxy_for = options.get('proxy_for')
            _filter = options.get('retry')

            if _filter is None:
                _filter = True

            elif _filter == 'retry':
                _filter = None

            print("vendors: ", "all" if vendors_filter is [] else vendors_filter)
            print("exclude: ", exclude)
            print("proxy will be enabled for:", proxy_for)
            print("filter: ", "all" if _filter else "retry")

            PROXY_ADDRESS = self.conf['download']['proxy']

            if which('aria2c') is not None:
                vendors = ProductPicturesStatus.objects.filter(needs_downloading=_filter).values(
                    'product__original_pictures__vendor').distinct()

                if vendors.exists():
                    # os.system('aria2c --enable-rpc')
                    aria = aria2p.API(
                        aria2p.Client(
                            host=HOST,
                            port=PORT,
                            secret=SECRET,
                        )
                    )

                    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                        try:
                            for vendor in vendors:

                                if vendor['product__original_pictures__vendor'] is not None:
                                    if len(vendors_filter) > 0:
                                        vendor_name = Vendor.objects.get(
                                            pk=vendor['product__original_pictures__vendor']).name

                                        if vendor_name in vendors_filter and vendor_name not in exclude:
                                            executor.submit(self.download, vendor['product__original_pictures__vendor'],
                                                            aria, proxy_for)

                                    else:
                                        vendor_name = Vendor.objects.get(
                                            pk=vendor['product__original_pictures__vendor']).name

                                        if vendor_name not in exclude:
                                            executor.submit(self.download, vendor['product__original_pictures__vendor'],
                                                            aria, proxy_for)

                        except Exception as ex:
                            self.stderr('An error occurred in concurrent state')

                else:
                    self.stdout.write(self.style.ERROR("There's no Vendor in ProductOriginalPictures model"))

            else:
                self.stdout.write(self.style.ERROR('aria2c is not installed.'))

        else:
            self.stdout.write(self.style.ERROR('Downloading pictures are disabled.'))
            self.stdout.write('You can enable this feature in project settings.')
