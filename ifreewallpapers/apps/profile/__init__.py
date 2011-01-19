# coding=UTF-8
from profile.models import Profile
from profile import settings as _settings

from django.conf import settings as django_settings
from django.contrib.auth.models import User
from django.db.models import signals

import os

# Within the django-profile-account app you will find two different concepts,
# profile and account (duh):
# Profile refers to all the information that is public, non-editable.
# Account is all the data that can be edited, but only by it's owner.
# The same information is sometimes profile and sometimes account, it only
# depends on the views through which such information is being accessed.

def new_user(sender, instance, **kwargs):
    if not Profile.objects.filter(user=instance).count():
        profile = Profile(user=instance)
        profile.save()
    else:
        profile = Profile.objects.get(user=instance)

    avatars = os.path.join(_settings.AVATARS_DIR, profile.slug)
    if not os.path.exists(avatars):
        os.makedirs(avatars)

    # FIXME:
    # FIXME: Lanzar señal que atrape la app core y cree sus directorios.
    wallpapers = os.path.join(django_settings.UPLOAD_DIR, profile.slug)
    if not os.path.exists(wallpapers):
        os.makedirs(wallpapers)

    return True
    
signals.post_save.connect(new_user, sender=User)
