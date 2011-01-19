# -*- coding: utf-8 -*-
from __future__ import with_statement as with

import csv
import os
import sys
import urllib2
import codecs
import unicodedata

for i in (-6, -22):
    PROJECT_ABSOLUTE_DIR = os.path.dirname(os.path.abspath(__file__))[:i]
    sys.path.insert(0, PROJECT_ABSOLUTE_DIR)

from django.core.management import setup_environ
from ifreewallpapers import settings

setup_environ(settings)

from core.models import Wallpaper
from django.conf import settings

def wpexists(fname):
    fname = fname[fname.rfind('/') + 1:]
    print fname
    return os.path.exists(os.path.join(settings.ORPHANS_DIR, fname))

def get_data(line):
    line = line.strip()
    first = line.find('"')
    second = line.find('"', first + 1)
    third = line.find('"', second + 1)
    url = line[:line.find(',')]
    fname = os.path.join(settings.ORPHANS_DIR, url[url.rfind('/') + 1:])
    name = line[first + 1:second]
    tags = line[third + 1:-1]
    wp = open(fname, 'w')
    wp.write(urllib2.urlopen(url).read())
    wp.close()
    return (fname, name, tags)

def fetch(csv_file):
    with codecs.open(csv_file, 'r', encoding='utf-8') as csvf:
        for line in csvf:
            if not wpexists(line[:line.find(',')]):
                line = unicodedata.normalize('NFKD', unicode(line, 'latin1'))
                wp, name, tags = get_data(line)
                w = Wallpaper()
                w.file = wp
                w.title = name
                w.save()
                w.tags = tags
                w.save()

def test(csv_file):
    i = 0
    files = []
    with open(csv_file, 'r') as csvf:
        for line in csvf:
            url = line[:line.find(',')]
            fname = url[url.rfind('/')+1:]
            if fname in files:
                print fname
            else:
                files.append(fname)
            x = 0
            for char in line:
                if char == ',':
                    x += 1
            if x > 4:
                pass
                # print '%i) %s' % (x, line)
            i += 1
        print '%s: %i' % (csv_file, i)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print 'No files given for fetching.'
        sys.exit(1)
    if sys.argv[1] == '--test':
        files = []
        for arg in sys.argv[2:]:
            if os.path.exists(arg):
                print arg
                # test(arg)
                with open(arg, 'r') as csvf:
                    for line in csvf:
                        url = line[:line.find(',')]
                        fname = url[url.rfind('/')+1:]
                        if fname in files:
                            print fname
                        else:
                            files.append(fname)
            else:
                print "File '%s' does not exist." % arg
        sys.exit()
    for arg in sys.argv[1:]:
        if os.path.exists(arg):
            fetch(arg)
        else:
            print "File '%s' does not exist." % arg
