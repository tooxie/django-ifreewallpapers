# -*- coding: utf-8 -*-
from core.hacks import force_forgive
from core.models import Wallpaper
from core.views import *
from friends.views import *

from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin, sitemaps
from django.views.generic.simple import direct_to_template as dtt

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'home.views.index', name='home'),
    url(r'^upload/wallpaper/$', upload, name='upload_wallpaper'),
    url(r'^upload/successful/$', upload_successful, name='upload_successful'),
    url(r'^download/wallpaper/$', wallpaper, name='download_wallpaper'),
    url(r'^wallpaper/(?P<slug>.*)/$', wallpaper, name='view_wallpaper'),
    url(r'^favourite/(?P<slug>.*)/$', toggle_fav, name='fav_wallpaper'),
    url(r'^manage/wallpaper/(?P<slug>.*)/$', manage_wallpaper, name='manage_wallpaper'),
    url(r'^adopt/(?P<slug>.*)/$', adopt, name='adopt_wallpaper'),
    url(r'^orphan/$', orphan, name='orphan_wallpaper'),
    url(r'^tell-a-friend/$', tell_a_friend, name='tell_a_friend'),
    url(r'^let-me-know/$', let_me_know, name='let_me_know'),

    # Contact
    (r'^contact/$', include('contact.urls.en')),

    # FAQ
    url(r'^faq/free-wallpapers-limbo/$', dtt, {'template': 'static/faq/limbo.html'},
         name='faq-limbo'),

    # Rating
    url(r'^rate/(?P<rate>[1-5]{1})/(?P<slug>.*)/$', rate, name='rate_wallpaper'),

    # Limbo
    (r'^limbo/', include('limbo.urls.en')),

    # Profile
    (r'^account/', include('profile.urls.account-en')),
    (r'^profile/', include('profile.urls.profile-en')),

    # Blog
    (r'^blog/', include('blog.urls.en')),
    (r'^blogger/', include('blog.urls.en')),

    # django-tagging
    url(r'^tag/(?P<tag_name>.*)/$', 'core.tag_views.list', name='objects_tagged'),

    # django-friends
    url(r'^friend/(?P<username>.*)/$', friend_user, name='friend_user'),

    # django.contrib.comments
    (r'^comments/', include('django.contrib.comments.urls')),

    # hacks
    url(r'^force/wallpaper/(?P<wallpaper_id>.*)/$', force_forgive, name='hack-force_forgive'),

    # Media:
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT }),

    # admin docs:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # admin:
    ('^admin/(.*)', admin.site.root),

    # Si no matchea, que busque en otra app:
    # (r'^', include('userprofile.urls')),
)

base_dict = {
    'paginate_by': 9,
    'template_name': 'core/index.html',
    'template_object_name': 'wallpaper',
}

latest_dict = {
    'queryset': Wallpaper.objects.filter(
        forgiven=True).order_by('-date'),
}
latest_dict.update(base_dict)

dload_dict = {
    'queryset': Wallpaper.objects.filter(
        forgiven=True).order_by('-downloads'),
}
dload_dict.update(base_dict)

urlpatterns += patterns('django.views.generic.list_detail',
    url(r'^latest/$', 'object_list', latest_dict, name='latest'),
    url(r'^most-downloaded/$', 'object_list', dload_dict, name='downloaded'),
)

# Sitemaps framework
forgiven_info_dict = {
    'queryset': Wallpaper.objects.filter(forgiven=True).order_by('-date'),
    'date_field': 'date',
}

limbo_info_dict = {
    'queryset': Wallpaper.objects.filter(forgiven=False).order_by('-date'),
    'date_field': 'date',
}

sitemaps = {
    'forgiven': sitemaps.GenericSitemap(forgiven_info_dict, changefreq='weekly'),
    'limbo': sitemaps.GenericSitemap(limbo_info_dict, changefreq='weekly'),
}
urlpatterns += patterns('django.contrib.sitemaps.views',
    url(r'^sitemap.xml$', 'index', {'sitemaps': sitemaps}),
    url(r'^sitemap-(?P<section>.+)\.xml$', 'sitemap', {'sitemaps': sitemaps}),
)
