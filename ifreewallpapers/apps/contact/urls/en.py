# -*- coding: utf-8 -*-
from contact.views import *

from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template as dtt

urlpatterns = patterns('',
    url(r'^$', contact, name='contact_us'),

    url(r'^sent/$', dtt, {'template': 'contact/sent.html'},
        name='contact_email_sent'),

    url(r'^error/$', dtt, {'template': 'contact/error.html'},
        name='contact_email_error')
)
