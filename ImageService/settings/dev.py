from .base import *

DEBUG = True

try:
    from ImageService.settings.local import *
except Exception:
    pass

