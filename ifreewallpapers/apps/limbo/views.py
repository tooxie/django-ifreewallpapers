# coding=UTF-8
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse

from utils.decorators import render_response
to_response = render_response('limbo/')

# CONSTANTS
LIMBO_SAVE = 'save'
LIMBO_DOOM = 'doom'

# FIXME: Falta una función que me diga si ese wallpaper ya fue votado por el
# FIXME: usuario actual. Lo idea sería que estuviera en el profile del usuario,
# FIXME: pero mientras no pueda meterle mano (hasta hacer un checkout limpio y
# FIXME: entrar a meterle código) lo meto en la vista del detalle del wallpaper.
@login_required
@to_response
def judge_wallpaper(request, slug, decision):
    """This view processes a vote for a wallpaper from the user."""
    from core.models import Wallpaper
    from limbo.models import Decision, Wallpaper as LimboWallpaper

    try:
        wp = Wallpaper.objects.exclude(uploader=request.user).get(slug=slug)
        being_judged, created = LimboWallpaper.objects.get_or_create(
            wallpaper=wp)
    except:
        raise Http404
    if decision == LIMBO_SAVE:
        being_judged.save_it(request.user)
    elif decision == LIMBO_DOOM:
        being_judged.doom_it(request.user)
    return HttpResponseRedirect(
        reverse('view_wallpaper', kwargs={'slug': wp.slug}))
