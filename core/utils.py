import os
from django.db import models


def get_small_image_path(instance, filename):
    return os.path.join('products', 'small', str(instance.product.vendor.name), filename)


def get_medium_image_path(instance, filename):
    return os.path.join('products', 'medium', str(instance.product.vendor.name), filename)


def get_large_image_path(instance, filename):
    return os.path.join('products', 'large', str(instance.product.vendor.name), filename)


import random
import string


def code_gen(size=7, chars=string.ascii_lowercase + string.digits + string.ascii_uppercase):
    return ''.join(random.choice(chars) for _ in range(size))


def create_shortcode(instance, size=7):
    new_code = code_gen(size=size)
    klass = instance.__class__
    qs_exists = klass.objects.filter(short_code=new_code).exists()
    if qs_exists:
        return create_shortcode(instance, size=size)
    return new_code