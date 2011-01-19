# coding=UTF-8
from profile import settings as _settings
from profile.models import Profile, Avatar
# import Image
# from PythonMagick import Image
from utils.TuxieMagick import Image

from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.template.defaultfilters import slugify
from django.template import Library, Node, TemplateSyntaxError, Variable

from os import path, makedirs
import time

register = Library()

class ResizedThumbnailNode(Node):
    def __init__(self, width, height, user, default):
        try:
            self.width = int(width)
        except:
            self.width = Variable(width)

        try:
            self.height = int(height)
        except:
            self.height = Variable(height)

        if not user:
            self.username = 'user'
        else:
            self.username = user

        self.default = default

    def get_user(self, context):
        return Variable(self.username).resolve(context)

    def sizes_ok(self, with_original=False):
        if with_original:
            orig_width = self.orig_width
            orig_height = self.orig_height
        else:
            orig_width, orig_height = _settings.DEFAULT_AVATAR_SIZE
            orig_height = _settings.DEFAULT_AVATAR_SIZE[1]
        return self.width >= orig_width and self.height >= orig_height

    def both_sides_equals(self, fname):
        return self.orig_width == self.orig_height

    def resize(self, orig='', dest=''):
        if not path.exists(orig):
            # print orig, 'does not exists'
            return None
        if path.exists(dest):
            # print dest, 'already exists'
            return True
        if not dest:
            dest = orig
        self.orig.scale(self.width, self.height)
        if self.orig.write(dest):
            # print 'resizing done, returning...'
            return self.as_url(dest)
        else:
            print ' *** ERROR *** '
            return None # damn! Close but no cigar...

    def get_file(self, profile=None):
        default = False
        file_name = None
        # username = slugify(profile.user.username)
        file_root = _settings.AVATARS_DIR
        # La diferencia entre self.default y default es que el primero indica
        # que tengo que devolver el avatar por defecto, mientras que el segundo
        # marca si estoy devolviendo el avatar por defecto o no.
        if self.default:
            default = True
        else:
            if profile is not None:
                # Este try es por si en profile.avatar existe una relación a un
                # avatar que no existe en la tabla de avatars.
                try:
                    if profile.avatar:
                        file_name = profile.avatar.name
                except:
                    profile.avatar = None
                    profile.save()
                    default = True
        if not file_name or  not path.exists(path.join(file_root, file_name)):
            file_name = _settings.DEFAULT_AVATAR
            default = True
        avatar_file = path.join(file_root, file_name)
        self.orig = Image(avatar_file)
        self.orig_width = self.orig.size().width()
        self.orig_height = self.orig.size().height()
        if not self.sizes_ok(with_original=True):
            if default:
                file_name = file_name[file_name.rfind('/')+1:]
                file_name = '%(width)i-%(name)s' % \
                    {'width': self.width, 'name': file_name}
                new_avatar = path.join(file_root, file_name)
            else:
                new_avatar = '' # Hack alert!
            self.resize(avatar_file, new_avatar)
        return (file_name, default)

    def as_url(self, path):
        from profile.avatars import path_to_url

        return path_to_url(path)

    def render(self, context):
        try:
            # If size is not an int, then it's a Variable, so try to resolve it.
            if not isinstance(self.width, int):
                self.width = int(self.width.resolve(context))
            self.user = self.get_user(context)
        except Exception, e:
            print e
            return '' # just die...
        profile = self.user.get_profile()
        if not profile:
            return ''
        file_root = _settings.AVATARS_DIR
        file_name, defaulting = self.get_file(profile)
        file_path = path.join(file_root, file_name)
        return self.as_url(path.join(file_root, file_name))

@register.tag('avatar')
def Thumbnail(parser, token):
    bits = token.contents.split()
    username, default = None, False
    width, height = _settings.DEFAULT_AVATAR_SIZE

    if len(bits) == 2:
        if bits[1] == 'default':
            default = True
        else:
            username = bits[1]
    elif len(bits) == 3:
        username = bits[1]
        default = bits[2]
    return ResizedThumbnailNode(width, height, username, default)
