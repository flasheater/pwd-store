#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 Juhamatti Niemelä <iiska@iki.fi>. All Rights Reserved.
# This file is licensed under the GPLv2+. Please see COPYING for more information.

import sys
import re

from subprocess import Popen, PIPE
from xml.etree import ElementTree

def space_to_camelcase(value):
    output = ""
    first_word_passed = False
    for word in value.split(" "):
        if not word:
            output += "_"
            continue
        if first_word_passed:
            output += word.capitalize()
        else:
            output += word.lower()
        first_word_passed = True
    return output

def cleanTitle(title):
    # make the title more command line friendly
    title = re.sub("(\\|\||\(|\))", "-", title)
    title = re.sub("-$", "", title)
    title = re.sub("\@", "At", title)
    title = re.sub("'", "", title)
    return title

def path_for(element, path=''):
    """ Generate path name from elements title and current path """
    title = cleanTitle(space_to_camelcase(element.find('title').text))
    return '/'.join([path, title])

def password_data(element):
    """ Return password data and additional info if available from
    password entry element. """
    passwd = element.find('password').text
    ret = passwd + "\n" if passwd else "\n"
    for field in ['username', 'url', 'comment']:
        fel = element.find(field)
        if fel.text is not None:
            ret = "%s%s: %s\n" % (ret, fel.tag, fel.text)
    return ret

def import_entry(element, path=''):
    """ Import new password entry to password-store using pass insert
    command """
    proc = Popen(['pass', 'insert', '--multiline', '--force',
                  path_for(element, path)],
              stdin=PIPE, stdout=PIPE)
    proc.communicate(password_data(element).encode('utf8'))
    proc.wait()

def import_group(element, path=''):
    """ Import all entries and sub-groups from given group """
    npath = path_for(element, path)
    for group in element.findall('group'):
        import_group(group, npath)
    for entry in element.findall('entry'):
        import_entry(entry, npath)


def main(xml_file):
    """ Parse given KeepassX XML file and import password groups from it """
    with open(xml_file) as xml:
        for group in ElementTree.XML(xml.read()).findall('group'):
            import_group(group)

if __name__ == '__main__':
    main(sys.argv[1])
