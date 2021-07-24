from django.conf import settings
from django.core.management import BaseCommand

from api.models import Product, ProductOriginalPictures, ProductPicturesStatus, Vendor


def do_it(product, product_original_picture, product_picture_status):
    main_pic = {}

    for index in settings.MAIN_PICTURE_SIZES:
        main_pic.update({f'{index}': ''})

    # main picture
    for key in main_pic.keys():
        main_pic[key] = product_original_picture.main_picture

    # picture
    pic_list = []
    for pic in product_original_picture.pictures:

        pictures = {}
        for key in settings.PICTURES_SIZES:
            pictures.update({f'{key}': pic})

        pic_list.append(pictures)

    product.main_picture = main_pic
    product.pictures = pic_list
    product.save()

    product_picture_status.needs_downloading = True
    product_picture_status.needs_resizing = False
    product_picture_status.needs_compression = False
    product_picture_status.save()


class Command(BaseCommand):
    # Todo Complete help command

    def add_arguments(self, parser):
        parser.add_argument('-vendors', type=str, nargs='*', default=None,
                            help='Retries to resize those pictures that got error.')

        parser.add_argument('-ids', type=str, nargs='*', default=None,
                            help='Retries to resize those pictures that got error.')

        parser.add_argument('hotfix', type=str, nargs='?', default=None,
                            help='Retries to resize those pictures that got error.')

    def handle(self, *args, **options):
        ids = options.get('ids', None)
        vendors = options.get('vendors', None)
        hot_fix = options.get('hotfix', None)
        print(hot_fix)

        self.rollback(ids, vendors, hot_fix)

    def rollback(self, ids, vendors, hot_fix):

        if ids:
            for _id in ids:
                print(f'rolling back id {_id}')
                product = Product.objects.get(pk=_id)
                product_original_picture = ProductOriginalPictures.objects.get(product=product)
                product_picture_status, created = ProductPicturesStatus.objects.get_or_create(product=product)
                do_it(product, product_original_picture, product_picture_status)

        if vendors:
            for vendor in vendors:
                product_original_pictures = ProductOriginalPictures.objects.filter(
                    vendor=Vendor.objects.get(name=vendor)).all()

                for product_original_picture in product_original_pictures:
                    product = Product.objects.get(pk=product_original_picture.product.id)
                    product_picture_status, created = ProductPicturesStatus.objects.get_or_create(product=product)
                    print(f'rolling back {product.id}')
                    do_it(product, product_original_picture, product_picture_status)

        if hot_fix:
            print('Started hotfix')
            pps = ProductPicturesStatus.objects.filter(needs_compression=True)

            count = 0
            for p in pps:
                if not p.product.main_picture['small'].startswith('/media'):
                    product = p.product
                    product_original_picture = ProductOriginalPictures.objects.get(product=product)
                    print(f' rolling back {product.id}')
                    do_it(product, product_original_picture, p)
                    count += 1

            print(f'{count} products rolled back')
