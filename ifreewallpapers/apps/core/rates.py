# coding=UTF-8
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse

from core.models import Wallpaper

RATING_SCALE = (
    (1, _(u'Should be deleted!')),
    (2, _(u'Is not good.')),
    (3, _(u'Is not bad.')),
    (4, _(u'Is very good.')),
    (5, _(u'Should go to the front page!')),
)

def do_rate(user, rate, slug):
    wallpaper = get_object_or_404(Wallpaper, slug=slug)
    if user.is_authenticated():
        object_rates = Wallpaper.rating.get_for_object(wallpaper)
        if object_rates:
            my_rating = object_rates.rates.filter(user=user)
            if my_rating.count() > 0:
                for object_rate in my_rating:
                    object_rate.delete()
    Wallpaper.rating.add_rate(wallpaper, rate, user)
    print Wallpaper.rating.get_for_object(wallpaper).get_average()
    return HttpResponseRedirect(reverse(
        'view_wallpaper', kwargs={'slug': slug}))

def get_rate(wallpaper, user):
    i_rated = None
    if user.is_authenticated():
        try:
            my_rating = Wallpaper.rating.get_for_object(wallpaper).rates.get(
                user=user)
            i_rated = RATING_SCALE[my_rating.rate - 1][1]
        except:
            pass
    return ((
        {'score': 1, 'opinion': RATING_SCALE[0][1], 'stars': 'one'},
        {'score': 2, 'opinion': RATING_SCALE[1][1], 'stars': 'two'},
        {'score': 3, 'opinion': RATING_SCALE[2][1], 'stars': 'three'},
        {'score': 4, 'opinion': RATING_SCALE[3][1], 'stars': 'four'},
        {'score': 5, 'opinion': RATING_SCALE[4][1], 'stars': 'five'},
    ), i_rated)
