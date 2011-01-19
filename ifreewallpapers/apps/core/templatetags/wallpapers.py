# coding=UTF-8
from core.models import Wallpaper

from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _
from django.template import Library, Node, Context, TemplateSyntaxError, \
                            Variable, loader
register = Library()

class WallpaperNode(Node):
    def __init__(self, **kwargs):
        self.offset = kwargs.get('offset', 0)
        self.how_many = kwargs.get('how_many', 0)
        self.user = kwargs.get('user', 'user')

    def render(self, context):
        user = Variable(self.user).resolve(context)
        query = Wallpaper.objects.filter(uploader=user)
        if self.offset:
            if self.how_many:
                 query = query[self.offset:self.how_many]
            else:
                 query = query[self.offset:]
        else:
            if self.how_many:
                 query = query[:self.how_many]
            else:
                 query = list(query)
        wallpaper_template = loader.get_template('core/my_wallpaper.html')
        return wallpaper_template.render(Context({'my_wallpapers': query}))

@register.tag('my_wallpapers')
def _parser(parser, token):
    bits = token.contents.split()
    args = len(bits)
    offset = 0
    how_many = 0
    user = None
    if args > 4:
        raise TemplateSyntaxError, _(u"The 'wallpapers' tag requires up to \
           three arguments: the user, the offset and the number of wallpapers \
           to retrieve.")
    elif args < 2:
        raise TemplateSyntaxError, _(u"Username required.")
    try:
        if args == 2:
            user = bits[1]
        if args == 3:
            user = bits[1]
            offset = int(bits[1])
        if args == 4:
            user = bits[1]
            offset = int(bits[1])
            how_many = int(bits[2])
    except:
        raise TemplateSyntaxError, _(u"The third and fourth argument should be\
                                       integers indiating how many wallpapers\
                                       to retrieve.")
    return WallpaperNode(offset=offset, how_many=how_many, user=user)
