#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Koala configuration builder.
"""

import ConfigParser
import os


def resolve_path(path, root):
    """If 'path' is relative make absolute by prepending 'root'"""
    if not os.path.isabs(path):
        path = os.path.join(root, path)
    return path


class Configuration(object):

    def __init__(self, **kwargs):

        self.config_dict = kwargs
        self.root = kwargs.get('root_dir', '.')

    def __parse_config_file(config):
        pass

    def get_value(key):
        pass
