# coding=UTF-8
from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from core.models import Wallpaper
from utils.decorators import render_response
to_response = render_response('home/')

from random import random as rnd

@to_response
def index(request):
    ctype = ContentType.objects.get_for_model(Wallpaper)
    comments = Comment.objects.filter(
        is_removed=False, content_type=ctype).order_by(
            '-submit_date')[:10]
    top_new = Wallpaper.objects.filter(
        inappropriate=False, forgiven=True).order_by(
            '-date')[:3]
    """
    top_viewed = Wallpaper.objects.filter(
        resolution__width__gte=800, resolution__height__gte=800,
        inappropriate=False, forgiven=True).order_by(
            '-views')[:10] # Slideshow
    """
    used = [wp.id for wp in top_new]
    highlight = Wallpaper.objects.filter(
        resolution__width__gte=1024, resolution__height__gte=768,
        inappropriate=False, forgiven=True).exclude(
            id__in=used).order_by(
                '-downloads')[:20] # Slideshow
    highlight = highlight[int(rnd()*len(highlight))]
    # used.extend([wp.id for wp in highlight])
    used.append(highlight.id)
    top_downloaded = Wallpaper.objects.filter(
        resolution__width__gte=1024, resolution__height__gte=768,
        inappropriate=False, forgiven=True).exclude(
            id__in=used).order_by(
                '-downloads')[:3]
    used.extend([wp.id for wp in top_downloaded])
    see_also = Wallpaper.objects.filter(
        resolution__width__gte=1024, resolution__height__gte=768,
        inappropriate=False, forgiven=True).exclude(
            id__in=used).order_by(
                '-rating', '?')[:12]
    return 'index.html', {'top_rated': [],
                          'top_downloaded': top_downloaded,
                          'highlight': highlight,
                          'top_new': top_new,
                          'top_comments': comments,
                          'see_also': see_also}
