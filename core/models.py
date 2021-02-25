from django.db import models
import uuid
from core.utils import get_large_image_path, get_medium_image_path, get_small_image_path


class ModifyDate(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ProductPicture(models.Model):
    picture_src = models.URLField()
    state = models.CharField(default='need_resize', max_length=512)
    small = models.ImageField(upload_to=get_small_image_path, blank=True, null=True)
    medium = models.ImageField(upload_to=get_medium_image_path, blank=True, null=True)
    large = models.ImageField(upload_to=get_large_image_path, blank=True, null=True)


class Vendor(models.Model):
    name = models.CharField(max_length=512)


class Product(ModifyDate):
    product_hash = models.UUIDField(default=uuid.uuid4, editable=False)
    pictures = models.OneToOneField(ProductPicture, blank=True, null=True, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, blank=True, null=True)


