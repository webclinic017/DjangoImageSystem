from shutil import rmtree

from django.core.management.base import BaseCommand

from api.models import ProductPicturesStatus
from api.utils import *
from .download import DOWNLOAD_DIRECTORY


class Command(BaseCommand):
    """Custom command to initial the resize operation"""

    help = 'Starts the resizing operation.'

    @staticmethod
    def remove_directories(products):

        products_count = len(products)
        for i in range(products_count):
            folder_name = products[i].id

            try:
                rmtree(os.path.join(DOWNLOAD_DIRECTORY, str(folder_name)))
            except Exception as e:
                print(e)

            print_progress_bar(iteration_main=i + 1, total_main=products_count, single=True,
                               prefix_main='Download Files', suffix_main='Deleted')

    @staticmethod
    def insert_products(products, status_objects):
        # chunk_size = 50
        #
        # product_chunks = [products[i:i + chunk_size] for i in range(0, len(products), chunk_size)]
        # status_chunks = [status_objects[i:i + chunk_size] for i in range(0, len(status_objects), chunk_size)]
        #
        # for i in range(len(product_chunks)):
        #     Product.objects.bulk_update(product_chunks[i], ['main_picture', 'pictures'])
        #     ProductPicturesStatus.objects.bulk_update(status_chunks[i],
        #                                               ['needs_downloading', 'needs_resizing', 'needs_compression'])

        # Changed Bulk to Save
        products_count = len(products)
        for i in range(products_count):
            products[i].save()
            status_objects[i].save()
            print_progress_bar(iteration_main=i + 1, total_main=products_count, single=True,
                               prefix_main='Products', suffix_main='Saved')

    def resize(self, _filter):

        self.stdout.write('Starting operation...')

        if settings.INTERFACE_DOWNLOAD_IMAGES:
            status_objects = ProductPicturesStatus.objects.filter(needs_downloading=False, needs_resizing=_filter,
                                                                  needs_compression=False)

            if status_objects.count() == 0:
                self.stdout.write(self.style.WARNING('No picture needs to be resized.'))

            else:
                self.stdout.write(self.style.SUCCESS('Starting resizing pictures'))

                all_count = status_objects.count()
                done_count = 0
                products_to_insert = []
                status_objects_to_insert = []

                for status_object in status_objects:
                    product = status_object.product

                    main_picture_address = ''
                    if len(product.main_picture) > 0:
                        try:
                            main_picture_address = product.main_picture['large']
                            product.main_picture = ProductPictureResizer(product,
                                                                         main=True).resize_and_save_main()

                        except ProductNoMainPictureException:
                            self.stdout.write(
                                self.style.WARNING(f'product_id {product.id} has no main_picture'))

                        except ProductMainPictureAlreadyResizedException:
                            self.stdout.write(
                                self.style.WARNING(f'product_id {product.id} main_picture already resized'))

                        except DownloadedPictureNotFound as d:
                            self.stderr.write(
                                f'Downloaded file not found. Possibly 404 on source url.'
                                f' Download flag set to None for product {product.id}.')
                            self.stdout.write(str(d))
                            status_object.needs_downloading = None
                            status_object.needs_resizing = False
                            status_object.needs_compression = False
                            status_object.save()
                            # self.remove_directory(product)
                            done_count += 1
                            continue

                        except Exception as e:
                            self.stderr.write(f'An exception occurred for product {product.id}')
                            self.stdout.write(str(e))
                            status_object.needs_resizing = None
                            status_object.save()
                            done_count += 1
                            continue

                    if len(product.pictures) > 0:
                        try:
                            if main_picture_address != product.pictures[0]['medium']:
                                product.pictures = ProductPictureResizer(product).resize_and_save()

                            else:
                                print(f'Interface error. main_pictures is in pictures. Automatically fixed Product: '
                                      f'{product.id}')
                                product.pictures = []

                        except ProductNoPicturesException:
                            self.stdout.write(
                                self.style.WARNING(f'product_id {product.id} pictures list is empty.'))

                        except ProductPicturesAlreadyResizedException:
                            self.stdout.write(
                                self.style.WARNING(f'product_id {product.id} pictures already resized'))

                        except DownloadedPictureNotFound as d:
                            self.stderr.write(
                                f'Downloaded file not found. Possibly 404 on source url.'
                                f'Download flag set to None for product {product.id}.')

                            self.stdout.write(str(d))
                            status_object.needs_downloading = None
                            status_object.needs_resizing = False
                            status_object.needs_compression = False
                            status_object.save()
                            # self.remove_directory(product)
                            done_count += 1
                            continue

                        except Exception as e:
                            self.stderr.write(f'An exception occurred for product {product.id}')
                            self.stdout.write(str(e))
                            status_object.needs_resizing = None
                            status_object.save()
                            done_count += 1
                            continue

                    # Adding product to bulk later
                    products_to_insert.append(product)

                    status_object.needs_downloading = False
                    status_object.needs_resizing = False
                    status_object.needs_compression = True

                    # Adding status to bulk later
                    status_objects_to_insert.append(status_object)

                    done_count += 1
                    progress_percentage = done_count / all_count * 100

                    # self.stdout.write(f'{done_count} products done resizing: {progress_percentage:0.3f}%')
                    print_progress_bar(iteration_main=done_count, total_main=all_count, single=True,
                                       prefix_main='Products', suffix_main='Done Resizing')

                    # Apply the changes
                    if len(products_to_insert) > 250:
                        self.insert_products(products_to_insert, status_objects_to_insert)
                        self.remove_directories(products_to_insert)
                        products_to_insert = []
                        status_objects_to_insert = []

                # Final attempt to apply the changes
                print('Final insertion to database')
                self.insert_products(products_to_insert, status_objects_to_insert)
                self.stdout.write(self.style.SUCCESS('Done'))

                # Delete downloaded files

                print('Final downloaded files deletion')
                self.remove_directories(products_to_insert)
                self.stdout.write(self.style.SUCCESS('Done'))

                self.stdout.write(self.style.SUCCESS('Resizing finished.'))

        else:
            self.stdout.write(self.style.ERROR('Downloading Pictures are disabled.'))
            self.stdout.write('You can enable this feature in project settings.')

    def add_arguments(self, parser):
        parser.add_argument('retry', type=str, nargs='?', default=None,
                            help='Retries to resize those pictures that got error.')

    def handle(self, *args, **options):
        params = options.get('retry', None)

        if params is None:
            self.resize(_filter=True)

        elif params == 'retry':
            self.resize(_filter=None)
