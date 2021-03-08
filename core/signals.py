import os
import uuid

from django.db import models
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _


class MediaFile(models.Model):
    file = models.FileField(_("file"),
        upload_to=lambda instance, filename: str(uuid.uuid4()))


# These two auto-delete files from filesystem when they are unneeded:

@receiver(models.signals.post_delete, sender=MediaFile)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


@receiver(models.signals.pre_save, sender=MediaFile)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = MediaFile.objects.get(pk=instance.pk).file
    except MediaFile.DoesNotExist:
        return False

    new_file = instance.file
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)



# pip install django-cleanup

# INSTALLED_APPS = (
#      ...
#     'django_cleanup', # should go after your apps
# )