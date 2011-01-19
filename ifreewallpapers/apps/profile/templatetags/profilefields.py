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

class ProfileFieldsNode(Node):
    def __init__(self, user):
        self.user = user

    def render(self, context):
        user = Variable(self.user).resolve(context)
        for group in user.get_groups()
            pass
        return "<li>nada</li>"

@register.tag('render_fields')
def profile_fields(parser, token):
    bits = token.contents.split()
    if len(bits) > 2:
        raise ValidationError(_(u'Too many values.'))
    return ProfileFieldsNode(bits[1])
