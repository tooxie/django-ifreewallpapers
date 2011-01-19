# coding=UTF-8
from profile.views.signup import signup, complete_signup, success, email_sent
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', signup, name='signup'),
    url(r'^key/$', complete_signup, name='signup-key'),
    url(r'^email/$', email_sent, name='signup-email'),
    url(r'^key/(?P<key>.*)/$', complete_signup, name='signup-key'),
    url(r'^success/$', success, name='signup-success'),
)
