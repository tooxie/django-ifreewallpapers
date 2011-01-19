# coding=UTF-8
# from django.core.mail import mail_admins
from sendmail import mail_admins

from django.utils.translation import ugettext as _

"""
class MissingWallpaperError(Exception):
    def __init__(self, wallpaper):
        body = _(u'')
        mail_admins(subject)
"""


class MissingImageError(Exception):
    def __init__(self, path):
        self.path = path
        subject = _(u'Missing image')
        message = _(u"""The following image is missing:
    %s""") % path
        mail_admins(subject, message)

    def __unicode__(self):
        return _(u'File not found: %s') % self.path
