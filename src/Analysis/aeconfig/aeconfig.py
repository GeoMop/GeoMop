"""Analyzis Editor static parameters

.. codeauthor:: Pavel Richter <pavel.richter@tul.cz>
"""

import logging
import os
import config as cfg
from geomop_util.logging import LOGGER_PREFIX

class _Config:
    """Class for Analyzis serialization"""

    DEBUG_MODE = False
    """debug mode changes the behaviour"""

    SERIAL_FILE = "AnalyzisEditorData"
    """Serialize class file"""
    
    CONTEXT_NAME = 'AnalyzisEditor'
    
    CONFIG_DIR = os.path.join(cfg.__config_dir__, 'AnalyzisEditor')

    def __init__(self, readfromconfig=True):

        self._analysis = None
        self._workspace = None

        if readfromconfig:
            data = cfg.get_config_file(self.__class__.SERIAL_FILE, self.CONFIG_DIR)
            self.workspace = getattr(data, '_workspace', self._workspace)
            self.analysis = getattr(data, '_analysis', self._analysis)
 
    def save(self):
        """Save config data"""
        cfg.save_config_file(self.__class__.SERIAL_FILE, self, self.CONFIG_DIR)
        
class AEConfig:
    """Static data class"""
    config = _Config()
    """Serialized variables"""
    logger = logging.getLogger(LOGGER_PREFIX +  config.CONTEXT_NAME)
    """root context logger"""
    
    @classmethod
    def init(cls):
        """Init class wit static method"""
        pass
     
    @classmethod
    def save(cls):
        """save persistent data"""
        cls.config.save()
        
