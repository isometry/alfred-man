# -*- coding: utf-8 -*-
import itertools
import os
import sys

from xml.etree.ElementTree import Element, SubElement, tostring

_MAX_RESULTS_DEFAULT = 9
UNESCAPE_CHARACTERS = u"""\\ ()[]{};`'"$"""


class Item(object):
    def __init__(self, attributes, title, subtitle, icon=None):
        self.attributes = attributes
        self.title = title
        self.subtitle = subtitle
        self.icon = icon

    def __str__(self):
        return tostring(self.xml(), encoding='unicode')

    def xml(self):
        item = Element(u'item', self.attributes)
        for attribute in (u'title', u'subtitle', u'icon'):
            value = getattr(self, attribute)
            if value is None:
                continue
            try:
                (value, attributes) = value
            except:
                attributes = {}
            SubElement(item, attribute, attributes).text = value
        return item


def args(characters=None):
    return tuple(unescape(arg, characters) for arg in sys.argv[1:])


def config():
    return _create('config')


def unescape(query, characters=None):
    for character in (UNESCAPE_CHARACTERS if (characters is None) else characters):
        query = query.replace('\\%s' % character, character)
    return query


def work(volatile):
    path = {
        True: os.getenv('alfred_workflow_cache', os.getenv('TMPDIR', '/tmp')),
        False: os.getenv('alfred_workflow_data', os.getenv('HOME', '/tmp'))
    }[bool(volatile)]
    return _create(os.path.expanduser(path))


def write(text):
    sys.stdout.write(text)


def xml(items, maxresults=_MAX_RESULTS_DEFAULT):
    root = Element('items')
    for item in itertools.islice(items, maxresults):
        root.append(item.xml())
    return tostring(root, encoding='unicode')


def _create(path):
    if not os.path.isdir(path):
        os.mkdir(path)
    if not os.access(path, os.W_OK):
        raise IOError('No write access: %s' % path)
    return path
