# coding=UTF-8
from core.models import Wallpaper

from utils.decorators import render_response
to_response = render_response('core/')

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

@to_response
def force_forgive(request, wallpaper_id):
    if not request.user.is_authenticated():
        raise Http404
    if not request.user.is_superuser:
        raise Http404
    wallpaper = get_object_or_404(Wallpaper, id=wallpaper_id)
    wallpaper.forgiven = True
    wallpaper.save()
    return HttpResponseRedirect(
        reverse('view_wallpaper', kwargs={'slug': wallpaper.slug}))
