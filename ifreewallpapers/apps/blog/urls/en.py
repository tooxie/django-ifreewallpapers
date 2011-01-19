# coding=UTF-8
from blog.views.admin import do_post
from blog.views.entries import index, view_post

from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^post/$', do_post, name="blog-do_post"),
    url(r'^posts/(?P<username>.*)/$', index, name="blog-index"),
    url(r'^post/(?P<username>.*)/(?P<slug>.*)/$', view_post, name="blog-view_post"),
)
