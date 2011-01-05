#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  pkgbuild.py
# 
# Copyright (c) 2008-2010 Piotr Husiatyński <phusiatynski@gmail.com>
# 
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.


import re
import os

__author__ = 'Piotr Husiatynski <phusiatynski@gmail.com>'
__all__ = ['Pkgbuild', ]


'''
PKGBUILD parser

Simple usage:
>>> from pkgbuild import Pkgbuild

>>> pkg = Pkgbuild('gajim-hg/PKGBUILD')

>>> pkg.parse_pkgname()
'gajim-hg'

>>> pkg.parse_arch()
['i686', 'x86_64']

'''


class Pkgbuild(object):
    _rx_pkgname = re.compile(r'pkgname=([\-\w]+)')
    _rx_pkgver = re.compile(r'pkgver=([\.\-\d]+)')
    _rx_pkgrel = re.compile(r'pkgrel=([\.\d]+)')
    _rx_pkgdesc = re.compile(r'pkgdesc=(?:"|\')(.*?)(?:"|\')', re.DOTALL)
    _rx_arch = re.compile(r'arch=\((.*?)\)', re.DOTALL)
    _rx_license = re.compile(r'license=\((?:\'|")(.*?)(?:\'|")\)', re.DOTALL)
    _rx_depends = re.compile(r'depends=\((.*?)\)', re.DOTALL)
    _rx_makedepends = re.compile(r'makedepends=\((.*?)\)', re.DOTALL)
    _rx_source = re.compile(r'source=\((.*?)\)', re.DOTALL)
    _rx_md5sum = re.compile(r'md5sums=\((.*?)\)', re.DOTALL)
    _rx_provides = re.compile(r'provides=\((.*?)\)', re.DOTALL)
    _rx_conflicts = re.compile(r'conflicts=\((.*?)\)', re.DOTALL)
    _rx_replaces = re.compile(r'replaces=\((.*?)\)', re.DOTALL)
    _rx_install = re.compile(r'install=(.*\.install)', re.DOTALL)
    _rx_build = re.compile(r'build\(\)\s*{.*}', re.DOTALL)
    _rx_contributor = re.compile(r'#\s*Contributor\:(.*)')
    _rx_maintrainer = re.compile(r'#\s*Maintrainer\:(.*)')
    _rx_flags = re.compile(r'''
            (?:
                \./autogen\.sh   |
                \./configure
            )\s*
            ((?:(?:--\S+)[\\\s]+)*)
                ''', re.VERBOSE)


    def __init__(self, pkgbuild_file=None, pkgbuild_text=None):
        if not (pkgbuild_text or pkgbuild_file):
            raise RuntimeError('PKGBUILD constructor takes one agrument.')
        if pkgbuild_file:
            if not os.path.isfile(pkgbuild_file):
                raise IOError(pkgbuild_file + ' does not exist.')
            self._text = open(pkgbuild_file).read()
        else:
            self._text = pkgbuild_text

    def _parse_simple(self, rx, text=None):
        text = text or self.get_text()
        f = re.findall(rx, text)
        f = f[0] if f else ""
        return self._replace_variables(f)

    def _parse_table(self, rx, text=None):
        sr = self._parse_simple(rx, text)
        sr = re.sub(r'\'|"|\\', '', ''.join(sr))
        return sr.split()

    def _replace_variables(self, text):
        "replace bash variables with it's values"
        # create parse_XXX dict
        bash_rx = r"\$[\w_]+"
        if not hasattr(self, "__bash_variables"):
            self.__bash_variables = {}
            for a in dir(self):
                if a.startswith("parse_"):
                    self.__bash_variables[a[len("parse_"):]] = getattr(self, a)
        def change(match):
            "bash variable replace function"
            match = match.group()[1:]
            return self.__bash_variables[match]()
        return re.sub(bash_rx, change, text)

    def get_text(self):
        return self._text

    def parse_pkgname(self, text=None):
        return self._parse_simple(self._rx_pkgname, text)

    def parse_pkgver(self, text=None):
        return self._parse_simple(self._rx_pkgver, text)

    def parse_pkgrel(self, text=None):
        return self._parse_simple(self._rx_pkgrel, text)

    def parse_pkgdesc(self, text=None):
        return self._parse_simple(self._rx_pkgdesc, text)

    def parse_arch(self, text=None):
        return self._parse_table(self._rx_arch, text)

    def parse_license(self, text=None):
        return self._parse_table(self._rx_license, text)

    def parse_depends(self, text=None):
        return self._parse_table(self._rx_depends, text)

    def parse_makedepends(self, text=None):
        return self._parse_table(self._rx_makedepends, text)

    def parse_source(self, text=None):
        return self._parse_table(self._rx_source, text)

    def parse_md5sums(self, text=None):
        return self._parse_table(self._rx_md5sum, text)

    def parse_provides(self, text=None):
        return self._parse_table(self._rx_provides, text)

    def parse_conflicts(self, text=None):
        return self._parse_table(self._rx_conflicts, text)

    def parse_replaces(self, text=None):
        return self._parse_table(self._rx_replaces, text)

    def parse_install(self, text=None):
        return self._parse_table(self._rx_install, text)

    def parse_flags(self, text=None):
        text = text or self.get_text()
        sr = re.findall(self._rx_flags, text)
        sr = re.sub(r'\'|"|\n|\\', '', ' '.join(sr))
        return sr.split()

    def parse_build(self, text=None):
        text = text or self.get_text()
        return re.findall(self._rx_build, text)

    def parse_contributor(self, text=None):
        return self._parse_simple(self._rx_contributor, text)

    def parse_maintrainer(self, text=None):
        return self._parse_simple(self._rx_maintrainer, text)

    def parseall(self, text=None):
        if not hasattr(self, '_parseall'):
            if not text:
                text = self.get_text()
            parsers = {}
            # get all parsers methods
            for attr_name in dir(self):
                if not attr_name.startswith('parse_'):
                    continue
                name = attr_name.split('_', 1)[1]
                parsers[name] = getattr(self, attr_name)
            for parser in parsers:
                parsers[parser] = parsers[parser](text) or []
            self._parseall = parsers
        return self._parseall

