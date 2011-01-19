# coding=UTF-8
"""
export DJANGO_SETTINGS_MODULE=ifreewallpapers.settings
export PYTHONPATH=/usr/lib/python2.5:/usr/local/lib/python2.5/site-packages:/usr/lib/python2.5/site-packages:/usr/lib/python2.5/site-packages/PIL:/home/alvaro/svn/django_src/projects:/home/alvaro/svn/django_src/projects/ifreewallpapers
"""
from django.core.management import setup_environ
from ifreewallpapers import settings

setup_environ(settings)

from core.models import Wallpaper
from django.conf import settings

def watermark_and_comment(wallpaper):
    if wallpaper.annotate(settings.COMMENT):
        if wallpaper.watermark(settings.WATERMARK_FILE):
            wallpaper.save()

#TODO: Chequear que exista el directorio backups/usuario/ o crearlo de ser
#TODO: necesario.
#TODO: Chequear que no exista el archivo en cuestión, no hacer nada de lo
#TODO: contrario.
#TODO: Chequear la existencia de thumbnails creados a partir de la imagen
#TODO: virgen y eliminarlos para que sean recreados.
def backup(wallpaper):
    file = wallpaper.file
    source = open(file, 'r')
    filename = file[file.rfind('/')+1:]
    dest_file = settings.BACKUP_DIR + filename
    destination = open(dest_file, 'w')
    if destination.write(source.read()):
        return True

for wallpaper in Wallpaper.objects.filter(watermarked=False):
    watermark_and_comment(wallpaper)
    # backup(wallpaper)
