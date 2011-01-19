# coding=UTF-8
from profile.views.profileviews import public

from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
    url(r'^(?P<slug>.*)/$', public, name='profile'),
)
