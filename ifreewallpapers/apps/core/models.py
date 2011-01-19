# -*- coding: utf-8 -*-
from django.db.models import (BooleanField, CharField, DateTimeField,
    EmailField, FileField, FilePathField, FloatField, ForeignKey, Model,
    PositiveIntegerField, SlugField, permalink,)
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _, ugettext as __

from utils.TuxieMagick import Image

from datetime import datetime

DEFAULT_RESOLUTION = 'ns'

class Resolution(Model):
    RESOLUTION_CHOICES = (
        ('sm', _(u'Standard Monitor')),
        ('ws', _(u'Widescreen Monitor')),
        ('hd', _(u'High Definition')),
        ('tv', _(u'Television')),
        ('md', _(u'Mobile Devices')),
        ('ns', _(u'Non Standard')),
        ('dm', _(u'Dual Monitor')),
    )
    width = PositiveIntegerField(max_length=9)
    height = PositiveIntegerField(max_length=9)
    relation = CharField(max_length=5, blank=True, null=True)
    result = FloatField(blank=True, null=True)
    type = CharField(max_length=2, choices=RESOLUTION_CHOICES)
    downloads = PositiveIntegerField(default=0)

    def __unicode__(self):
        return '%(width)sx%(height)s' % \
              {'width': self.width, 'height': self.height}

# TODO:
# TODO: Todo el puntaje que genere un wallpaper debe estar asociado
# TODO: exclusivamente al wallpaper en si, y no al usuario. Por
# TODO: transitiva el usuario es quien cobra los puntos generados.
class Wallpaper(Model):
    resolution = ForeignKey(Resolution, blank=True, null=True,
        related_name='resolution')
    uploader = ForeignKey(User, blank=True, null=True) # is it an orphan?
    file = FilePathField(max_length=255, recursive=True, blank=True, null=True,
        path=settings.UPLOAD_DIR)
    author = CharField(max_length=50, blank=True, null=True)
    title = CharField(max_length=100, blank=True, null=True)
    slug = SlugField(max_length=100, unique=True)
    date = DateTimeField(auto_now_add=True)
    rating = FloatField(default=0)
    viewed = PositiveIntegerField(default=0)
    downloads = PositiveIntegerField(default=0)
    inappropriate = BooleanField(default=False)
    adopted = DateTimeField(blank=True, null=True) # Iname
    forgiven = BooleanField(default=False) # Limbo

    def save(self, *args, **kwargs):
        if not self.id:
            ping = True
        else:
            ping = False
        if self.file:
            self.resolution = self.guess_resolution()
        self.slug = self.get_slug()
        super(Wallpaper, self).save(*args, **kwargs)
        if ping:
            self.ping_google()

    def ping_google(self):
        from django.contrib.sitemaps import ping_google

        try:
            ping_google()
        except:
            pass

    def __unicode__(self):
        return self.get_title()

    @permalink
    def get_absolute_url(self):
        return 'view_wallpaper', tuple(), {'slug': self.slug}

    def adopt(self, *args, **kwargs):
        try:
            self.uploader = args[0]
            self.title = kwargs['title']
            self.tags = kwargs['tags']
            self.inappropriate = kwargs['inappropriate']
            self.adopted_on = datetime.now()
            self.save()
        except Exception, e:
            print e
            return False
        return True

    def get_tags(self):
        return self.tags
    tags = property(get_tags)

    def get_comments(self, count=False):
        from django.contrib.comments.models import Comment
        from django.contrib.contenttypes.models import ContentType

        ctype = ContentType.objects.get_for_model(Wallpaper)
        comments = Comment.objects.filter(
            content_type=ctype.id, object_pk=self.id)
        if count:
            return comments.count()
        else:
            return comments.get()
    comments = property(get_comments)

    def get_comments_count(self):
        return self.get_comments(True)
    comments_count = property(get_comments_count)

    def get_title(self):
        if not self.title:
            return __(u"Untitled")
        return self.title

    def wallpaper_exists(self, slug):
        try:
            wp = Wallpaper.objects.get(slug=slug)
            if wp.id == self.id:
                return False
            return True
        except:
            return False

    def guess_resolution(self):
        size = self.get_size().split('x')
        resolution, created = Resolution.objects.get_or_create(
            width=size[0], height=size[1], defaults={'type': DEFAULT_RESOLUTION})
        return resolution

    def get_display_resolutions(self):
        size = self.get_size().split('x')
        resolutions = Resolution.objects.exclude(
            type='ns').filter(
                width__lte=size[0], height__lte=size[1]).order_by(
                    'type', '-width', '-height')
        return resolutions

        # TODO:
        # TODO: Intento fallido. La idea era mostrar los grupos de resoluciones
        # TODO: en el siguiente orden: El grupo que tiene la resolución más
        # TODO: descargada va primero, pero dentro de ese grupo, el orden es
        # TODO: alfabético. Porque las resoluciones más comunes están quedando
        # TODO: muy abajo en la lista.
        """
        from django.db import connection

        size = self.get_size().split('x')
        resolutions = []
        cursor = connection.cursor()
        sql = "SELECT DISTINCT type FROM core_resolution ORDER BY downloads"
        cursor.execute(sql)
        for row in cursor.fetchall():
            print row
            for resolution in Resolution.objects.exclude(
                type='ns').filter(
                    width__lte=size[0], height__lte=size[1],
                    type=row[0]).order_by(
                        '-width', '-height'):
                resolutions.append(resolution)
        return resolutions
        """

    resolutions = property(get_display_resolutions)

    def get_size(self, filename=None):
        from PIL import Image
        if filename:
            image = Image.open(filename)
        else:
            image = Image.open(self.file)
        return '%ix%i' % (image.size[0], image.size[1])

    def get_rating(self):
        return Wallpaper.rating.get_for_object(self).get_average()

    def _width(self):
        if self.resolution:
            return self.resolution.width
    width = property(_width)

    def _height(self):
        if self.resolution:
            return self.resolution.height
    height = property(_height)

    def get_for_resolution(self, resolution):
        from os import path, makedirs
        from math import ceil

        dest_width, dest_height = [int(side) for side in resolution.split('x')]
        # /path/to/directory
        file_root = self.file[:self.file.rfind('/')]
        # filename.ext
        file_name = self.file[self.file.rfind('/') + 1:]
        # /path/to/directory/1280x800
        dest_root = path.join(file_root, resolution)
        # /path/to/directory/1280x800/filename.ext
        dest_path = path.join(dest_root, file_name)
        if not path.exists(dest_path):
            if not path.exists(dest_root):
                makedirs(dest_root)
            file_orig = Image(self.file)
            if self.width != dest_width or self.height != dest_height:
                rule_width = round(
                    (float(dest_width)*float(100))/float(self.width))
                rule_height = round(
                    (float(dest_height)*float(100))/float(self.height))
                temp_width, temp_height = dest_width, dest_height
                if rule_height > rule_width:
                    # TODO:
                    # TODO: Testear caso en que ancho sea flotante.
                    temp_width = (rule_height*self.width)/100
                    file_orig.scale(temp_width, dest_height)
                else:
                    temp_height = (rule_width*self.height)/100
                    file_orig.scale(dest_width)
                if rule_width != rule_height:
                    x_offset = str((temp_width-dest_width)/2)
                    y_offset = str((temp_height-dest_height)/2)
                    file_orig.crop(str(resolution)+'+'+x_offset+'+'+y_offset)
            wmark_file = settings.WATERMARK_FILE
            wmark = Image(wmark_file)
            if wmark.size().width() > dest_width and dest_width > 200:
                wmark_file = wmark_file[:wmark_file.rfind('.')] + '-small' + \
                             wmark_file[wmark_file.rfind('.'):]
            # FIXME:
            # FIXME: La marca de agua no se ve en sistemas que implementan
            # FIXME: barras de herramientas inferiores. Hay que colocarla unos
            # FIXME: 50px mas arriba.
            # file_orig.watermark(wmark_file)
            file_orig.comment(settings.COMMENT)
            file_orig.write(dest_path)
        return dest_path

    def get_resolution(self, filename=None):
        from PIL import Image
        if filename:
            image = Image.open(filename)
        else:
            image = Image.open(self.file)
        relation = float(image.size[0])/float(image.size[1])
        if relation == float(2)/float(3):
            return '2:3' #iPhone's resolution
        elif relation == float(5)/float(4):
            return '5:4'
        elif relation == float(4)/float(3):
            return '4:3'
        elif relation == float(3)/float(2):
            return '3:2'
        elif relation == float(8)/float(5):
            return '8:5'
        elif relation == float(5)/float(3):
            return '5:3'
        elif relation == float(16)/float(9):
            return '16:9'
        elif relation == float(17)/float(9):
            return '17:9'
        # 5:4 1.25
        # 4:3 1.333333333333333333
        # 3:2 1.5
        # 8:5 1.6
        # 5:3 1.666666666666666667
        # 16:9 1.777777777777777778
        # 17:9 1.888888888888888889

    def get_slug(self):
        from django.template.defaultfilters import slugify
        if self.title:
            self.slug = slug = slugify(self.title)
            if len(slug) > 250:
                self.slug = slug = slug[0:251]
        else:
            self.slug = slug = '__untitled__'
        x = 0
        while self.wallpaper_exists(slug):
            slug = '%(slug)s-%(index)i' % \
                  {'slug': self.slug, 'index': x}
            x += 1
        return slug

    def random_slug(self, **kwargs):
        # print kwargs
        try:
            forgiven = kwargs['forgiven']
        except:
            forgiven = False
        try:
            user = kwargs['user']
        except:
            return None
        try:
            exclude = kwargs['exclude']
        except:
            exclude = None
        wallpaper = Wallpaper.objects.filter(
            forgiven=forgiven).order_by('?')
        if exclude:
            wallpaper = wallpaper.exclude(slug=exclude)
        if user.is_authenticated():
            wallpaper = wallpaper.exclude(limbo__votes__judge=user)
        try:
            return wallpaper[0].slug
        except:
            return None

    # Hack alert!
    def uploaded_by(self, user=None):
        if user:
            if self.uploader:
                if self.uploader == user:
                    who = _(u"Uploaded by you")
                else:
                    who = _(u"Uploaded by %(user)s" % \
                            {'user': self.uploader.username})
            else:
                who = _(u"Uploaded")
        else:
            who = _(u"Uploaded by %(user)s" % self.uploader)
        return who

class Waiting(Model):
    wallpaper = ForeignKey(Wallpaper)
    user = ForeignKey(User, blank=True, null=True)
    email = EmailField()
    sent = BooleanField(default=False)

    class Meta:
        unique_together = ("wallpaper", "user")

class Views(Model):
    wallpaper = ForeignKey(Wallpaper, related_name='user_views')
    user = ForeignKey(User, blank=True, null=True)
    when = DateTimeField(auto_now_add=True)
