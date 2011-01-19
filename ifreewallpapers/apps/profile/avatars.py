# coding=UTF-8
from profile.models import Avatar
from profile import settings as _settings

from django.conf import settings

from os.path import join

def avatar_to_url(avatar):
    root = join(_settings.AVATARS_DIR, avatar.profile.user.username)
    return path_to_url(join(root, avatar.name[avatar.name.rfind('/')+1:]))

def path_to_url(path):
    try:
        return path.replace(settings.MEDIA_ROOT, settings.MEDIA_URL)
    except:
        return ''

def handle_avatar(uploaded_file, profile, remove_original=True):
    from django.template.defaultfilters import slugify
    from os.path import exists, join
    from os import remove

    filename = uploaded_file.name[uploaded_file.name.rfind('/') + 1:]
    x = 0
    root = profile.avatars_root()
    while exists(join(root, filename)):
        filename = '%i-%s' % (x, uploaded_file.name[uploaded_file.name.rfind('/') + 1:])
        x += 1
    avatar_file = open(join(root, filename), 'w+b')
    avatar_file.write(uploaded_file.read())
    avatar_file.close()
    uploaded_file.close()
    if remove_original:
        remove(uploaded_file.name)
    avatar = Avatar()
    avatar.profile = profile
    avatar.name = avatar_file.name
    avatar.save()
    return avatar
