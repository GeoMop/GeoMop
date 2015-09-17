# -*- coding: utf-8 -*-
"""
Main window module
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

import logging
import uuid


class DataContainer(object):
    MJ_DIR = "mj"
    MJ_FILENAME = "mj"
    SSH_DIR = "ssh"
    SSH_FILENAME = "ssh"
    PBS_DIR = "pbs"
    PBS_FILENAME = "pbs"
    RESOURCE_DIR = "resource"
    RESOURCE_FILENAME = "resource"

    def __init__(self, cfg):
        self.cfg = cfg
        self.multijobs = self.cfg\
            .get_config_file(self.MJ_FILENAME, self.MJ_DIR)
        if not self.multijobs:
            self.multijobs = dict()
        self.shh_presets = self\
            .cfg.get_config_file(self.SSH_FILENAME, self.SSH_DIR)
        if not self.shh_presets:
            self.shh_presets = dict()
        self.pbs_presets = self\
            .cfg.get_config_file(self.PBS_FILENAME, self.PBS_DIR)
        if not self.pbs_presets:
            self.pbs_presets = dict()
        self.resources_presets = self\
            .cfg.get_config_file(self.RESOURCE_FILENAME, self.RESOURCE_DIR)
        if not self.resources_presets:
            self.resources_presets = dict()

    @staticmethod
    def uuid():
        """
        Generate ID so that all data structures have same implementation.
        """
        return str(uuid.uuid4())

    def save_mj(self):
        self.cfg.save_config_file(self.MJ_FILENAME,
                                  self.multijobs,
                                  self.MJ_DIR)
        logging.info('mj saved successfully!')

    def save_ssh(self):
        self.cfg.save_config_file(self.SSH_FILENAME,
                                  self.shh_presets,
                                  self.SSH_DIR)
        logging.info('ssh saved successfully!')

    def save_pbs(self):
        self.cfg.save_config_file(self.PBS_FILENAME,
                                  self.pbs_presets,
                                  self.PBS_DIR)
        logging.info('pbs saved successfully!')

    def save_resources(self):
        self.cfg.save_config_file(self.RESOURCE_FILENAME,
                                  self.resources_presets,
                                  self.RESOURCE_DIR)
        logging.info('resource saved successfully!')

    def save_all(self):
        self.save_mj()
        self.save_ssh()
        self.save_pbs()
        self.save_resources()
        logging.info('all saved successfully!')
