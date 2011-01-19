# coding=UTF-8
from blog.models import Post

from django.forms import Form, ValidationError, CharField, BooleanField, \
    Textarea
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify


class NewPostForm(Form):
    title = CharField(_(u'Title'))
    content = CharField(_(u'Content'), widget=Textarea())
    tags = CharField(_(u'Tags'), required=True)
    draft = BooleanField(label=_(u'Is it a draft?'), required=False)

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.get('user')
            del kwargs['user']
        super(NewPostForm, self).__init__(*args, **kwargs)

    def clean_title(self):
        title = self.cleaned_data.get('title')
        posts = Post.objects.filter(
            blog__owner=self.user, slug=slugify(title)).count()
        if posts > 0:
            raise ValidationError(_(u'You already have a post with that title'))
        return title
