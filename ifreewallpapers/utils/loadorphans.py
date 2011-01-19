# coding=UTF-8
from os.path import abspath, basename, dirname, join
from sys import path, argv

PROJECT_ABSOLUTE_DIR = dirname(abspath(__file__))[:-22]
path.insert(0, PROJECT_ABSOLUTE_DIR)
PROJECT_ABSOLUTE_DIR = dirname(abspath(__file__))[:-6]
path.insert(0, PROJECT_ABSOLUTE_DIR)
# PROJECT_NAME = basename(PROJECT_ABSOLUTE_DIR)

from django.core.management import setup_environ
from ifreewallpapers import settings

setup_environ(settings)

from crawlersettings import *
from django.conf import settings
from django.template.defaultfilters import slugify

from core.models import Wallpaper

from os import listdir
from os.path import exists, join, isfile, isdir
from mimetypes import guess_type
from PIL import Image

# TODO: Agregar un parámetro que sea una lista de directorios y/o archivos a
# TODO: excluir del crawleado.
def crawl_orphans(dirname):
    print 'Entrando...', dirname
    for file in listdir(dirname):
        print 'file', file
        if file[0] != '.':
            path = join(dirname, file)
            if isfile(path) and guess_type(path)[0] in SUPPORTED_TYPES:
                is_good = size_greater_than(path, MINIMUM_SIZE)
                if is_good:
                    _orphan(path)
                elif is_good is None:
                    # exclude(path)
                    pass
            elif isdir(path):
                print file, 'es un directorio'
                crawl_orphans(path)
    print 'Saliendo...', dirname

def size_greater_than(filename, size):
    try:
        file = Image.open(filename)
    except:
        return None
    if file.size[0] < size[0] or file.size[1] < size[1]:
        return False
    return True

def _orphan(filepath):
    try:
        file = open(filepath, 'r')
        print 'Abriendo archivo origen', file
    except Exception, e:
        print e
        return None
    try:
        filename = file.name[file.name.rindex('/') + 1:-4]
        ext = file.name[-4:]
    except Exception, e:
        print e
        filename = file.name
    destpath = join(settings.ORPHANS_DIR, slugify(filename) + ext)
    if not exists(destpath):
        try:
            dest = open(destpath, 'w')
        except Exception, e:
            print e
            return None
        dest.write(file.read())
        dest.close()
        print 'Copiando contenido a destino...', destpath
    file.close()
    if Wallpaper.objects.filter(file=destpath).count():
        print 'El wallpaper ya existía, no se hace nada.'
    else:
        wallpaper = Wallpaper()
        wallpaper.file = destpath
        wallpaper.save()
        # wallpaper, created = Wallpaper.objects.get_or_create(file=destpath)

if __name__ == "__main__":
    for arg in argv[1:]:
        crawl_orphans(arg)
