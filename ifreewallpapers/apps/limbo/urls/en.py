# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from django.conf import settings

from core.models import Wallpaper

list_dict = {
    'queryset': Wallpaper.objects.filter(forgiven=False,
            resolution__width__gte=1024, resolution__height__gte=600).order_by(
                '-date'),
    'paginate_by': 9,
    'template_name': 'limbo/index.html',
    'template_object_name': 'wallpaper',
}

urlpatterns = patterns('django.views.generic.list_detail',
    url(r'^$', 'object_list', dict(list_dict), name='limbo'),
)

urlpatterns += patterns('limbo.views',
    url(r'^save/(?P<slug>.*)/$', 'judge_wallpaper', kwargs={'decision': 'save'}, name='save_it'),
    url(r'^doom/(?P<slug>.*)/$', 'judge_wallpaper', kwargs={'decision': 'doom'}, name='doom_it'),
)
