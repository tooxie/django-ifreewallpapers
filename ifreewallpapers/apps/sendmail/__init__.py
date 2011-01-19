# coding=UTF-8
from sendmail.models import Message

from django.conf import settings
from django.core import mail
from django.template import loader
from django.utils.translation import ugettext as _

from os import path

def send(**kwargs):
    mail = Message(sender_name=kwargs.get('sender')[0],
                   sender_email=kwargs.get('sender')[1],
                   recipient_name=kwargs.get('recipient')[0],
                   recipient_email=kwargs.get('recipient')[1],
                   subject=kwargs.get('subject'),
                   message=kwargs.get('body'))
    return mail.save()

def report_exception(request, exception):
    for admin in settings.ADMINS:
        send(subject='Exception: %s' % exception.__str__(),
             body=exception.__str__() + '\n' + request.__str__(),
             recipient=admin)
    print exception
    return True

def mkbody(msg):
    if hasattr(settings, 'EMAIL_SIGNATURE_TEMPLATE'):
        if path.exists(settings.EMAIL_SIGNATURE_TEMPLATE):
            template = open(settings.EMAIL_SIGNATURE_TEMPLATE, 'r')
            msg += template.read() 
            template.close()
    return msg

def mail_admins(subject, message, fail_silently=False):
    sender = (_(u'Ifreewallpapers Admin'), settings.DEFAULT_FROM_EMAIL)
    if isinstance(settings.ADMINS[0], tuple):
        for recipient in settings.ADMINS:
            send(sender=sender, recipient=recipient, subject=subject,
                 body=mkbody(message))
    else:
        send(sender=sender, recipient=recipient, subject=subject,
             body=mkbody(message))
    return None

def send_mail(*args, **kwargs):
    if 'message' in kwargs:
        kwargs['message'] = mkbody(kwargs.get('message', ''))
    return mail.send_mail(*args, **kwargs)
