from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, pre_delete
from .models import ProductPicture
from PIL import Image
from django.core.files.base import ContentFile
from django.core import files
from django.core.files.uploadedfile import InMemoryUploadedFile
#
# def pic_small_gen(instance, new_slug=None):
#     # class_model = instance.__class__
#     # class_model.objects.filter(slug=slug).exists()
#     small_size = (156, 156)
#     large_image = Image.open(obj.large)
#     small_pic = large_image.resize(small_size)
#
#     return 'hi'


# def pic_medium_gen(instance, new_slug=None):
#     # class_model = instance.__class__
#     # class_model.objects.filter(slug=slug).exists()
#
#     return slug

# @receiver(post_save, sender=ProductPicture)
# def pic_change(sender, instance, *args, **kwargs):
#     if instance.state == 'downloaded':
#
#         large_image = Image.open(instance.large.file.name).convert('RGB')
#         file_name = str(instance.large.name).split('/')[-1]
#         # large_image.save(large_image, 'webp')
#         small_image = large_image.copy()
#         medium_image = large_image.copy()
#
#         small_size = (156, 156)
#         small_pill = small_image.resize(small_size)
#         instance.small.save(file_name, files.File(small_pill))
#
#         # instance.small = all_hi
#         # instance.small.save(file_name, files.File(all_hi))
#
#         medium_size = (182, 182)
#         medium_pill = medium_image.resize(medium_size)
#         instance.medium.save(file_name, files.File(medium_pill))
#
#         instance.state = 'published'
#
#         instance.save()
#         large_image.close()
#
#         print('OK')
#     else:
#         print('not OK')
#         # instance.small = pic_small_gen(instance)
#         # instance.medium = pic_medium_gen(instance)

#
# @receiver(post_save, sender=ProductPicture)
# def pic_change(sender, instance, *args, **kwargs):
#     if instance.state == 'downloaded':
#
#         new_image = ContentFile(instance.large.read())
#         file_name = str(instance.large.name).split('/')[-1]
#         new_image.name = file_name + '_s'
#         instance.small = new_image
#         instance.save()
#         new_image.name = file_name + '_m'
#         instance.medium = new_image
#         instance.state = 'published'
#         instance.save()
#
#         print('OK')
#     else:
#         print('not OK')