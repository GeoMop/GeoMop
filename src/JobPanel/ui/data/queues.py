# -*- coding: utf-8 -*-
"""
Module for fatching queues from different systems.
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""
import os

from helpers.importer import DialectImporter


class PbsQueues:
    @staticmethod
    def get_system_queues(dialect_key):
        if 'APPDATA' in os.environ:
            __queues_dir__ = os.path.join(os.environ['APPDATA'], 'GeoMop',
                                          'JobPanel', 'queues')
        else:
            __queues_dir__ = os.path.join(os.environ['HOME'], '.geomop',
                                          'JobPanel', 'queues')
        dl = DialectImporter.get_dialect_by_name(dialect_key)
        file_name = os.path.join(__queues_dir__, dl.__queue_file__)
        try:
            with open(file_name, "r") as file:
                queues = []
                for line in file.readlines():
                    if line.startswith("Queue:"):
                        queues.append(line[7:-1])
                return queues
        except (FileNotFoundError, IOError):
            return []
