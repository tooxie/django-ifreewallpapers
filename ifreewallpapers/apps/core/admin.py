from django.contrib import admin

from core.models import Wallpaper, Waiting, Resolution

try:
    admin.site.register(Wallpaper)
    admin.site.register(Waiting)
    admin.site.register(Resolution)
except Exception, e:
    print e
