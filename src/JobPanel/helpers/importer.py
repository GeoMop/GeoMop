# -*- coding: utf-8 -*-
"""
Loader and importer for available dialects.
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

import os
import pkgutil
import importlib

'''
Import of PBS dialects: 
'''


class DialectImporter:
    @staticmethod
    def get_available_dialects():
        """
        Fetch all available dialects parsed from class files.
        :return: List of dialects names
        """

        # Cannot achieve cleaner way with inspect module (problem with path)
        # ToDo: Remake mod_names to be independent of path
        path = os.path.join("helpers", "dialect")
        mod_names = [name for _, name, _ in pkgutil.iter_modules([path])]

        names = dict()

        for mod in mod_names:
            dialect = importlib.import_module("helpers.dialect.%s" % mod)
            names[mod] = dialect.__dialect_name__
        return names

    @staticmethod
    def get_dialect_by_name(dialect_key):
        """
        Returns dialect by its module name
        :param dialect_key:
        :return:
        """
        dialect = importlib.import_module("helpers.dialect.%s" % dialect_key)
        return dialect

