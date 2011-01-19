# coding=UTF-8
from sendmail import send

from django.conf import settings
from django.template import loader, Context
from django.utils.translation import ugettext as _

from datetime import datetime
from random import random
import cPickle as pickle
import md5

def keygen(user):
    data = [settings.SECRET_KEY, random(), str(user), str(datetime.now())]
    pickled = pickle.dumps(data, pickle.HIGHEST_PROTOCOL)
    return md5.new(pickled).hexdigest()

def send_registration_key(request, user, password, registration=None):
    if not registration:
        registration = user.get_registration()
    subject = _(u"iFreeWallpapers.com registration")
    site = 'http://%s' % request.META.get('HTTP_HOST')
    body = loader.get_template('profile/signup_key.txt').render(
        Context(
            {'registration': registration, 'name': user.get_full_name(),
             'email': user.email, 'site_url': site, 'password': password}))
    send(sender=(settings.DEFAULT_FROM_NAME,
                 settings.DEFAULT_FROM_EMAIL),
         recipient=(user.get_full_name(), user.email),
         subject=subject, body=body)
    # return email.send_registration_key(user, user.registration.get().get_key())
    return True
