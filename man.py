#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
man.alfredworkflow, v2.2
Robin Breathe, 2013-2022
"""

import json
import os
import re
import subprocess
import sys

from fnmatch import fnmatch
from time import time

import alfred

DEFAULT_MAX_RESULTS = 36
DEFAULT_CACHE_TTL = 604800

WHATIS_COMMAND = '/usr/libexec/makewhatis -o /dev/fd/1 `/usr/bin/manpath`'


def cache_file(filename, volatile=True):
    parent = os.path.expanduser(
        (
            os.getenv('alfred_workflow_data'),
            os.getenv('alfred_workflow_cache')
        )[bool(volatile)] or os.getenv('TMPDIR')
    )
    if not os.path.isdir(parent):
        os.mkdir(parent)
    if not os.access(parent, os.W_OK):
        raise IOError('No write access: %s' % parent)
    return os.path.join(parent, filename)


def fetch_whatis(max_age=DEFAULT_CACHE_TTL):
    cache = cache_file('whatis.1.json')
    if os.path.isfile(cache) and (time() - os.path.getmtime(cache) < max_age):
        return json.load(open(cache, 'r'))
    raw_pages = subprocess.check_output(WHATIS_COMMAND, shell=True).decode('utf-8')
    pagelist = map(
        lambda x: map(
            lambda y: y.strip(),
            x.split(' - ', 1)
        ),
        raw_pages.splitlines()
    )
    whatis = {}
    for (pages, description) in pagelist:
        for page in pages.split(', '):
            whatis[page] = description
    json.dump(whatis, open(cache, 'w'))
    return whatis


def fetch_sections(whatis, max_age=DEFAULT_CACHE_TTL):
    cache = cache_file('sections.1.json')
    if os.path.isfile(cache) and (time() - os.path.getmtime(cache) < max_age):
        return set(json.load(open(cache, 'r')))
    sections = set([])
    pattern = re.compile(r'\(([^()]+)\)$')
    for page in whatis.keys():
        sre = pattern.search(page)
        if sre:
            sections.add(sre.group(1))
    json.dump(list(sections), open(cache, 'w'))
    return sections


def man_arg(manpage):
    pattern = re.compile(r'(.*)\((.+)\)')
    sre = pattern.match(manpage)
    (title, section) = (sre.group(1), sre.group(2))
    return '%s/%s' % (section, title)


def man_uri(manpage, protocol='x-man-page'):
    return '%s://%s' % (protocol, man_arg(manpage))


def filter_whatis_name(_filter, whatis):
    return {k: v for (k, v) in whatis.items() if _filter(k)}


def filter_whatis_description(_filter, whatis):
    return {k: v for (k, v) in whatis.items() if _filter(v)}


def result_list(query, whatis):
    return {
        alfred.Item(attributes={'uid': man_uri(page), 'arg': man_arg(page)},
                    title=page, subtitle=description, icon='icon.png')
        for (page, description) in whatis.items()
        if fnmatch(page, '%s*' % query)
    }


def complete():
    query = sys.argv[1].strip()
    maxresults = int(os.getenv('alfredman_max_results', DEFAULT_MAX_RESULTS))
    cache_ttl = int(os.getenv('alfredman_cache_ttl', DEFAULT_CACHE_TTL))

    whatis = fetch_whatis(cache_ttl)
    sections = fetch_sections(whatis, cache_ttl)

    results = []

    if ' ' in query:
        # section page
        (_section, _title) = query.split()
        pattern = re.compile(r'^.+\(%s\)$' % _section)
        _whatis = filter_whatis_name(pattern.match, whatis)
        results.extend(result_list(_title, _whatis))
    else:
        # section filtering
        if query in sections:
            _uri = man_uri('(%s)' % query)
            results.append(alfred.Item(
                attributes={'uid': _uri, 'arg': _uri, 'valid': 'no'},
                title='Open man page',
                subtitle='Scope restricted to section %s' % query,
                icon='icon.png'
            ))
        # direct hit
        if query in whatis:
            _arg = man_arg(query)
            _uri = man_uri(query)
            results.append(alfred.Item(
                attributes={'uid': _uri, 'arg': _arg},
                title=query,
                subtitle=whatis[query],
                icon='icon.png'
            ))
        # standard filtering
        results.extend(result_list(query, whatis))

    # no matches
    if not results:
        results.append(alfred.Item(
            attributes={'uid': 'x-man-page://404', 'valid': 'no'},
            title='404 Page Not Found',
            subtitle='',
            icon='icon.png'
        ))

    return alfred.xml(results, maxresults=maxresults)


if __name__ == '__main__':
    print(complete())
