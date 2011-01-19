from django.contrib import admin

from sendmail.models import Message

try:
    admin.site.register(Message)
except Exception, e:
    print e
