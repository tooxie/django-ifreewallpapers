# -*- coding: utf-8 -*-
from core.models import Wallpaper
from profile.views.accountviews import (avatar, change_email, change_password,
    change_personal, delete_avatar, disabled, location, login, logout,
    lost_password, make_avatar, manage_avatars, overview, public,)

# from django.contrib.auth import views
from django.conf.urls.defaults import *
# from django.conf import settings

urlpatterns = patterns('',
    url(r'^$', overview, name='account-index'),
    url(r'^avatar/$', avatar, name='account-change_avatar'),
    url(r'^avatar/delete/$', delete_avatar, name='account-delete_avatar'),
    url(r'^avatar/make/(?P<keyword>.*)/$', make_avatar,
        name='account-make_avatar',
        kwargs={'model': Wallpaper, 'match': 'slug', 'file': 'file'}),
    url(r'^avatars/$', manage_avatars, name='account-manage_avatars'),
    url(r'^disabled/(?P<username>.*)/$', disabled, name='account-disabled'),
    url(r'^e-mail/$', change_email, name='account-change_email'),
    url(r'^location/$', location, name='account-change_location'),
    url(r'^login/$', login, name='account-login'),
    url(r'^logout/$', logout, name='account-logout'),
    url(r'^password/change/$', change_password,
        name='account-change_password'),
    url(r'^password/lost/$', lost_password, name='account-lost_password'),
    url(r'^personal/$', change_personal, name='account-change_personal'),

    # Signup
    (r'^signup/', include('profile.urls.signup-en')),

    # Blog
    (r'^blog/$', include('blog.urls.en')),
)
