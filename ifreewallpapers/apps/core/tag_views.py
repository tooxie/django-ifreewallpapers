# coding=UTF-8
from core.models import Wallpaper
from tagging.models import Tag

from django.utils.translation import ugettext_lazy as _
from django.views.generic.list_detail import object_list as generic
from django.shortcuts import get_object_or_404

def list(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)
    wallpapers_id = [item.object.pk for item in tag.items.all()]
    browser_title = _(u'%(tag)s wallpapers') % {'tag': tag_name}
    list_title = _(u'%(tag)s tag wallpapers') % {'tag': tag_name}
    return generic(request, template_name='core/wallpapers.html',
                   queryset=Wallpaper.objects.filter(id__in=wallpapers_id),
                   paginate_by=12, extra_context={'page_title': list_title,
                       'browser_title': browser_title})
    # return 'wallpapers.html', {'wallpapers': wallpapers}

