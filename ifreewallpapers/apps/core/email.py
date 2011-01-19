# coding=UTF-8
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.template import Context, Template, loader
from django.conf import settings

from sendmail import send

def tell_a_friend(**kwargs):
    subject = _(settings.EMAIL_TELL_A_FRIEND_SUBJECT)
    body = loader.get_template(settings.EMAIL_TELL_A_FRIEND_TEMPLATE)
    if not kwargs.get('recipient')[0]:
        recipient_name = _(u"A friend")
    else:
        recipient_name = kwargs.get('recipient')[0]
    wallpaper_url = settings.PROJECT_URL + reverse('view_wallpaper',
        kwargs={'slug': kwargs.get('about').slug})
    # FIXME:
    # FIXME: Averiguar como mierda hacer la asignación con unicode.
    context = Context(
        {'myname': kwargs.get('sender')[0], 'yourname': recipient_name,
         'wallpaper_url': wallpaper_url})
    return send(subject=subject, body=body.render(context).rstrip(), **kwargs)

def send_contact_email(post):
    """
    if send_contact_email(sender_name=post.get('name'),
                          sender_email=post.get('email'),
                          body=post.get('body')):
    """
    pass
