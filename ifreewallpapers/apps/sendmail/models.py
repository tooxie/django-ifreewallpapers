# coding=UTF-8
from django.db.models import Model, CharField, EmailField, DateTimeField, \
                             BooleanField, TextField
from django.core.mail import mail_admins, EmailMessage
from django.template import Context, Template
from django.conf import settings

from datetime import datetime
from os.path import join

class Message(Model):
    sender_name = CharField(max_length=75)
    sender_email = EmailField()
    recipient_name = CharField(max_length=75)
    recipient_email = EmailField()
    subject = CharField(max_length=75)
    message = TextField()
    success = BooleanField(default=False)
    exception = CharField(max_length=255, blank=True, null=True)
    date = DateTimeField(auto_now_add=True)

    def save(self):
        if not self.sender_email:
            sender = settings.DEFAULT_FROM_EMAIL
        else:
            sender = u"%(name)s <%(email)s>" % \
                {'name': unicode(self.sender_name), 'email': self.sender_email}
        if not self.recipient_email:
            recipient = settings.ADMINS
        else:
            recipient = u"%(name)s <%(email)s>" % \
                {'name': unicode(self.recipient_name),
                 'email': self.recipient_email}
        email = EmailMessage(subject=self.subject, body=self.message,
                             from_email=(sender), to=(recipient,))
        super(Message, self).save()
        try:
            email.send()
            self.success = True
        except Exception, e:
            self.success = False
            self.exception = e
        super(Message, self).save()
        return self.success

    def mkbody(self):
        body_signature = ''
        for dir in settings.TEMPLATE_DIRS:
            try:
                body_signature = '\n' + open(join(dir, settings.EMAIL_SIGNATURE_TEMPLATE), 'r').read()
                body_signature = Template(body_signature)
            except Exception, e:
                print e
        return self.message + body_signature.render(Context({}))

    def __unicode__(self):
        if self.success:
            ok = '(Y)'
        else:
            ok = '(N)'
        return "%s %s" % (self.subject, ok)
