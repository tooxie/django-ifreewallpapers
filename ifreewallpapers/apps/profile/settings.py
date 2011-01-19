# coding=UTF-8
from django.conf import settings
from os.path import join

DEFAULT_AVATAR_SIZE = (96, 96)
DEFAULT_AVATAR = join(settings.MEDIA_ROOT, 'avatars/default.png')
AVATARS_DIR = (
    join(settings.MEDIA_ROOT, 'avatars/')
)
AVATARS_DIR = join(settings.MEDIA_ROOT, 'avatars/')
MAX_AVATAR_SIZE=5242880 # 5MB
