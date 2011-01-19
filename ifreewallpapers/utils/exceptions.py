# coding=UTF-8
from sendmail import mail_admins

from django.utils.translation import ugettext as _

class NotImplementedError(Exception):
    def __init__(self, feature):
        self.feature = feature
        subject = _(u'Not implemented feature requested')
        message = _(u"""The following feature is not yet implemented, however, was requested:
    %s""") % feature
        mail_admins(subject, message)

    def __unicode__(self):
        return _(u'Feature not implemented yet')
