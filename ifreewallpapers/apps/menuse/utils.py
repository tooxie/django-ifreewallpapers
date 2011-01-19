# -*- coding: utf-8 -*-
def replace_link(url, request):
    from django.conf import settings
    from django.core.urlresolvers import reverse

    REPLACE_LINK = (
        ('{{ SELF }}', request.META.get('PATH_INFO')),
        ('{{ GET }}', '?%s' % request.META.get('QUERY_STRING')),
        ('{{ URL }}', request.META.get('HTTP_HOST')),
        ('{{ LOGIN }}', settings.LOGIN_URL),
        ('{{ LOGOUT }}', settings.LOGOUT_URL),
        ('{{ SIGNUP }}', settings.SIGNUP_URL))
    for rep in REPLACE_LINK:
        url = url.replace(rep[0], rep[1])
    reverse_keyword = 'reverse:'
    while reverse_keyword in url:
        position = url.find(reverse_keyword) + len(reverse_keyword)
        if url.find('&') > url.find('?'):
            char = '&'
        else:
            char = '?'
        name = url[position:].split(char)[0]
        url = url.replace(reverse_keyword + name, reverse(name), 1)
    return url

