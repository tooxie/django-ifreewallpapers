# coding=UTF-8
from core.exceptions import MissingImageError
from utils.TuxieMagick import Image

from django.template import Library, Node, Template, TemplateSyntaxError, Variable
from django.utils.translation import ugettext as u_
from django.conf import settings

# from PythonMagick import Image
from os import path, makedirs

register = Library()

class ResizedThumbnailNode(Node):
    def __init__(self, filename, dimensions):
        self.image_name = Variable(filename)
        # FIXME: Que pasa cuando no se explicita un ancho, y éste defaultea a
        # 0 px? Testear.
        self.height = int(dimensions[1])
        self.width = int(dimensions[0])
        # print dimensions

    def get_filename(self, context):
        file_path = self.image_name.resolve(context)
        if path.exists(file_path):
            self.image = Image(file_path)
            self.thumb_width, self.thumb_height = self.image.size().dimensions()
            i = file_path.rfind('/')
            return (file_path[:i], file_path[i+1:])
        # TODO:
        # TODO: Implementar un wallpaper por defecto que se va a mostrar en
        # TODO: lugar de los wallpapers que falten mientras alguien lo arregla.
        raise MissingImageError(file_path)

    def should_resize(self):
        if self.thumb_width > self.width or self.thumb_height > self.height:
            return True
        return False

    def render(self, context):
        try:
            image_path, image_name = self.get_filename(context)
        except MissingImageError, e:
            return ''
        # Now to the thumbnail
        size = str(self.width)
        if self.height:
            size += 'x%s' % self.height
        thumb_root = path.join(image_path, 'thumbs', size)
        thumb_path = path.join(thumb_root, image_name)
        # The URL to the thumbnail.
        thumb_url = thumb_path.replace(settings.MEDIA_ROOT, settings.MEDIA_URL)
        # Resizing logic
        if not path.exists(thumb_path):
            # image_file = Image(path.join(image_path, image_name))
            # if image_file.size().width() > self.width:
            if self.should_resize():
                if not path.exists(thumb_root):
                    makedirs(thumb_root)

                rule_width, rule_height = 0, 0
                if self.thumb_width > self.width:
                    rule_width = round(
                        (float(self.width)*float(100))/float(self.thumb_width))
                if self.thumb_height > self.height:
                    rule_height = round(
                        (float(self.height)*float(100))/float(self.thumb_height))

                temp_width, temp_height = None, None
                if rule_height > rule_width:
                    temp_width = (rule_height*self.thumb_width)/100
                    self.image.scale(temp_width, self.height)
                else:
                    temp_height = (rule_width*self.thumb_height)/100
                    self.image.scale(self.width)

                if rule_width != rule_height:
                    x_offset, y_offset = "0", "0"
                    if self.thumb_width > self.width or \
                            self.thumb_height > self.height:
                        if temp_width:
                            x_offset = str((temp_width - self.width) / 2)
                        if temp_height:
                            y_offset = str((temp_height - self.height) / 2)
                        self.image.crop(size + '+' + x_offset + '+' + y_offset)

                self.image.write(thumb_path)

                thumb_url = thumb_path.replace(
                    settings.MEDIA_ROOT, settings.MEDIA_URL)
            else:
                # If I don't need to resize it, then I set the URL to the
                # original image file.
                thumb_url = settings.MEDIA_URL + \
                            image_path[len(settings.MEDIA_ROOT):]
        return thumb_url

def Thumbnail(parser, token):
    """
    The parser of the templatetag.

    Should get at least one argument, the filename. If you pass only one, will
try to get a default from DEFAULT_THUMBNAIL_SIZE from the settings module. If
it doesn't exist will default to a width of 150px.

    If you specify a size as well it will be used. In both cases it first tries
to split the string by 'x', if it's not possible uses the entire string. This
is useful because you can specify width and height or just the width.
    """
    bits = token.contents.split()
    if len(bits) in [2, 3]:
        if len(bits) == 3:
            if 'x' in bits[2]:
                dimensions = bits[2].split('x')
            else:
                dimensions = [bits[2], 0]
        else:
            if 'DEFAULT_THUMBNAIL_SIZE' in settings.get_all_members():
                if 'x' in settings.DEFAULT_THUMBNAIL_SIZE:
                    dimensions = settings.DEFAULT_THUMBNAIL_SIZE.split('x')
                else:
                    dimensions = [settings.DEFAULT_THUMBNAIL_SIZE, None]
            else:
                dimensions = [150, 0]

    else:
        raise TemplateSyntaxError, u_(u"thumb recieves two or three \
            arguments, the file to generate the thumbnail from and \
            optionally the size of the resulting thumbnail.")
    for dim in dimensions:
        try:
            int(dim)
        except:
            raise TemplateSyntaxError, u_(u"Tumbnail's size should be given \
                                            in píxels, as just integers.")
    return ResizedThumbnailNode(bits[1], dimensions)

register.tag('thumb', Thumbnail)
