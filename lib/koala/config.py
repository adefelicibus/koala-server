#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Koala configuration builder.
"""

import ConfigParser
import os

from .version import VERSION_MAJOR

KOALA_ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
if os.path.islink(KOALA_ROOT_DIR):
    KOALA_ROOT_DIR = os.path.abspath(
        os.path.join(os.readlink(KOALA_ROOT_DIR), os.pardir, os.pardir))
KOALA_LIB_DIR = os.path.join(KOALA_ROOT_DIR, "lib")
DEFAULT_INI = ["config/koala.ini"]


def resolve_path(path, root):
    """If 'path' is relative make absolute by prepending 'root'"""
    if not os.path.isabs(path):
        path = os.path.join(root, path)
    return path


class Configuration(object):

    def __init__(self, **kwargs):
        # kwargs: config_file {'config_file:__file__'}
        # root_dir {'root_dir: __path__'} pegar o caminho abstrato da lib koala

        # TODO: create exceptions about the files

        self.config_file = kwargs.get('config_file', resolve_path(DEFAULT_INI[0], KOALA_ROOT_DIR))
        self.root = kwargs.get('root_dir', KOALA_ROOT_DIR)
        self.config_dict = {}

        self.version_major = VERSION_MAJOR

        self.__parse_config_file(self.config_file)

    def __parse_config_file(self, config):
        conf_parser = ConfigParser.ConfigParser()
        self.conf_parser = conf_parser

        conf_parser.read(self.config_file)

        for section in conf_parser.sections():
            params = {}
            params = conf_parser.items(section)
            for k, v in params:
                self.config_dict[k] = v

    def get(self, key, default):
        return self.config_dict.get(key, default)
