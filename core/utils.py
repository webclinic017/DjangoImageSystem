import os
from django.db import models


def get_small_image_path(instance, filename):
    return os.path.join('products', 'small', str(instance.product.vendor.name), filename)


def get_medium_image_path(instance, filename):
    return os.path.join('products', 'medium', str(instance.product.vendor.name), filename)


def get_large_image_path(instance, filename):
    return os.path.join('products', 'large', str(instance.product.vendor.name), filename)