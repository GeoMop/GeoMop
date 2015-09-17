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
    SSH_DIR = "ssh"
    PBS_DIR = "pbs"
    RESOURCE_DIR = "resource"

    def __init__(self, cfg):
        self.cfg = cfg
        self.multijobs = self.cfg.get_config_file("mj.yaml", self.MJ_DIR)
        if not self.multijobs:
            self.multijobs = dict()
        self.shh_presets = self.cfg.get_config_file("ssh.yaml", self.SSH_DIR)
        if not self.shh_presets:
            self.shh_presets = dict()
        self.pbs_presets = self.cfg.get_config_file("pbs.yaml", self.PBS_DIR)
        if not self.pbs_presets:
            self.pbs_presets = dict()
        self.resources_presets = self.cfg.get_config_file("resources.yaml",
                                                          self.RESOURCE_DIR)
        if not self.resources_presets:
            self.resources_presets = dict()

    @staticmethod
    def uuid():
        """
        Generate ID so that all data structures have same implementation.
        """
        return str(uuid.uuid4())

    def save_mj(self):
        self.cfg.save_config_file("list", self.multijobs, self.MJ_DIR)
        logging.info('Mj saved successfully!')

    def save_ssh(self):
        print("Ssh saved")
        self.cfg.save_config_file("list", self.shh_presets, self.SSH_DIR)

    def save_pbs(self):
        print("Pbs saved")
        self.cfg.save_config_file("list", self.pbs_presets, self.PBS_DIR)

    def save_resources(self):
        print("Resource saved")
        self.cfg.save_config_file("list", self.resources_presets,
                              self.RESOURCE_DIR)

    def save_all(self, mj, ssh, pbs, resource):
        print("All saved")
        pass
