# coding=UTF-8
from django.conf import settings

def is_allowed(object):
    content_type = None
    if type(object).__name__ == 'unicode':
        content_type = object
    elif type(object).__name__ == 'tuple':
        content_type = object[0]
    elif type(object).__name__ == 'InMemoryUploadedFile':
        content_type = object.content_type
    try:
        if object.__module__ == 'urllib':
            content_type = object.info().type
    except:
        pass
    for allowed in settings.ALLOWED_CONTENT_TYPES:
        if allowed[0] == content_type:
            return True
    print 'content_type', content_type, 'for', object, 'not allowed'
    return False

def get_ext(string, url=False):
    from mimetypes import guess_type

    if url:
        content_type = guess_type(string)[0]
    else:
        content_type = string
    for allowed in settings.ALLOWED_CONTENT_TYPES:
        if allowed[0] == content_type:
            return allowed[1]
    return None
