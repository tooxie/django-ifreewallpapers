# coding=UTF-8
from django.contrib.contenttypes.models import ContentType
from favs.models import Favourite

def get_ctype(object):
    ctype = ContentType.objects.get_for_model(object)
    return [ctype.id, object._get_pk_val()]

def is_this_fav(object, user, **kwargs):
    if not user.is_authenticated():
        return None

    if 'bool' in kwargs and kwargs.get('bool'):
        return _bool_is_this_fav(object, user)
    else:
        return _object_is_this_fav(object, user)

def _bool_is_this_fav(object, user):
    ctype = ContentType.objects.get_for_model(object)
    try:
        fav = Favourite.objects.get(
            content_type=ctype, object_id=object.id, user=user)
        return True
    except Exception, e:
        print '_bool: %s' % e
        return False

def _object_is_this_fav(object, user):
    ctype = ContentType.objects.get_for_model(object)
    try:
        fav = Favourite.objects.get(
            content_type=ctype, object_id=object.id, user=user)
    except Exception, e:
        print '_obj: %s' % e
        fav = Favourite(object=object, user=user)
    return fav

