"""Analyzis Editor static parameters

.. codeauthor:: Pavel Richter <pavel.richter@tul.cz>
"""

import logging
import os
import config as cfg
from geomop_util.logging import LOGGER_PREFIX
from geomop_dialogs import GMErrorDialog
import ui.data as data

class _Config:
    """Class for Analyzis serialization"""

    DEBUG_MODE = False
    """debug mode changes the behaviour"""

    SERIAL_FILE = "LayerEditorData"
    """Serialize class file"""
    
    CONTEXT_NAME = 'LayerEditor'
    
    CONFIG_DIR = os.path.join(cfg.__config_dir__, 'LayerEditor')

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
        
    @property
    def data_dir(self):
        """Data directory - either an analysis dir or the last used dir."""
        return os.getcwd()
#        if self.workspace and self.analysis:
#            return os.path.join(self.workspace, self.analysis)
#        else:
#            return self.last_data_dir
        
class LEConfig:
    """Static data class"""
    config = _Config()
    """Serialized variables"""
    logger = logging.getLogger(LOGGER_PREFIX +  config.CONTEXT_NAME)
    """root context logger"""
    diagram = data.Diagram()
    """Current diagram data"""
    main_window = None
    """parent of dialogs"""
    
    @classmethod
    def init(cls, main_window):
        """Init class wit static method"""
        cls.main_window = main_window        
     
    @classmethod
    def save(cls):
        """save persistent data"""
        cls.config.save()
        
    @classmethod
    def open_shape_file(cls, file):
        """Open and add shape file"""
        if cls.diagram is not None:
            if not cls.diagram.shp.is_file_open(file):
                try:
                    cls.diagram.shp.add_file(file)
                    return True
                except Exception as err:
                    err_dialog = GMErrorDialog(cls.main_window)
                    err_dialog.open_error_dialog("Can't open shapefile", err)
        return False
        
