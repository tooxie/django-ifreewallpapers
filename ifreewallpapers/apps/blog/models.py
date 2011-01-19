# coding=UTF-8
from django.db.models import Model, ForeignKey, DateTimeField, CharField, \
    TextField, SlugField
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

class Blog(Model):
    owner = ForeignKey(User, related_name="blogs", unique=True,
        verbose_name=_(u'Owner of the blog'))
    cdate = DateTimeField(_(u'Creation date'), auto_now_add=True)
    title = CharField(_(u'Blog title'), max_length=255)


class Post(Model):
    DRAFT = 'D'
    PUBLISHED = 'P'
    STATUS_CHOICES = (
        (DRAFT, _(u'Draft')),
        (PUBLISHED, _(u'Published')))

    blog = ForeignKey(Blog, related_name="posts")
    title = CharField(_(u'Title'), max_length=150, unique=True)
    slug = SlugField(_(u'Slug'), unique=True)
    status = CharField(_(u'Status'), max_length=1, choices=STATUS_CHOICES,
        blank=False, null=False)
    source = TextField(_(u'Content'), blank=False, null=False)
    html = TextField(_(u'Content in HTML format'))
    cdate = DateTimeField(_(u'Created at'), auto_now_add=True)
    udate = DateTimeField(_(u'Updated at'))

    def save(self):
        from django.contrib.markup.templatetags.markup import textile
        from django.template.defaultfilters import slugify

        from datetime import datetime

        if not self.id:
            if not self.user:
                # FIXME:
                # FIXME: ¿No debería lanzar una excepción?
                return None
            self.blog, created = Blog.objects.get_or_create(
                owner=self.user,
                defaults={'title': _(u"%(user)s's blog") % \
                    {'user': self.user.username}})
        self.slug = slugify(self.title)
        if self.draft:
            self.status = self.DRAFT
        else:
            self.status = self.PUBLISHED
        self.html = textile(self.source)
        self.udate = datetime.now()
        super(Post, self).save()
