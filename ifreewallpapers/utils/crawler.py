#!/usr/bin/python2.5
# coding=UTF-8
from crawlersettings import *

from sys import argv
from os import listdir
from os.path import exists, join, isfile, isdir
from mimetypes import guess_type
from PIL import Image

def crawl(dir):
    for file in listdir(dir):
        if file[0] != '.':
            path = join(dir, file)
            if isfile(path) and guess_type(path)[0] in SUPPORTED_TYPES:
                is_good = size_greater_than(path, MINIMUM_SIZE)
                if is_good:
                    save_it(path, SAVE_TO)
                elif is_good is None:
                    exclude(path)
            elif isdir(path):
                crawl(path)

def size_greater_than(filename, size):
    try:
        file = Image.open(filename)
    except:
        return None
    if file.size[0] < size[0] or file.size[1] < size[1]:
        return False
    return True

def save_it(filename, save_to):
    file = open('crawler.log', 'a')
    file.write(filename + '\n')
    if save_to:
        try:
            name = filename[filename.rfind('/')+1:]
        except:
            name = filename
        file = open(join(save_to, name), 'w')
        file.write(open(filename).read())
    print filename
    return True

def exclude(filename):
    file = open('crawler.error.log', 'a')
    file.write(filename + '\n')
    return True

if __name__ == "__main__":
    crawl(argv[1])
