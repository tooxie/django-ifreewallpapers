# coding=UTF-8
from django.conf import settings

from md5 import md5

def next(request):
    next = request.GET.get('next', '/')
    if request.META.get('PATH_INFO', '/') == settings.LOGOUT_URL:
        if next.startswith('/account/'):
            next = '/'
    return next

def do_gonzo(*args, **kwargs):
    hash_this = ''
    for arg in args:
        hash_this += '%s$' % str(arg)
    for arg in kwargs:
        hash_this += '%s$' % str(kwargs.get(arg))
    hash_this += settings.SECRET_KEY
    return md5(hash_this).hexdigest()
