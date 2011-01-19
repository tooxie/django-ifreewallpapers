from django.contrib import admin

from profile.models import Profile, Avatar, FieldGroup, Field, FieldData, \
                           FieldChoice, CharData, TextData

try:
    admin.site.register(Profile)
    admin.site.register(Avatar)
    admin.site.register(FieldGroup)
    admin.site.register(Field)
    admin.site.register(FieldData)
    admin.site.register(FieldChoice)
    admin.site.register(CharData)
    admin.site.register(TextData)
except Exception, e:
    print e
