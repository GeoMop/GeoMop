"""Analyzis Editor static parameters

.. codeauthor:: Pavel Richter <pavel.richter@tul.cz>
"""

import logging
import os
import config as cfg
from geomop_util.logging import LOGGER_PREFIX
from geomop_dialogs import GMErrorDialog
import ui.data as data
import copy

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
    history = data.GlobalHistory()
    """History for current geometry data"""
    diagrams = [data.Diagram(history)]
    """List of diagram data"""
    layers = data.Layers()
    """Lauers structure"""
    diagram = diagrams[0]
    """Current diagram data"""
    data = None    
    """Data from geometry file"""    
    main_window = None
    """parent of dialogs"""
    curr_file_timestamp = None
    """    
    Timestamp of opened file, if editor text is 
    imported or new timestamp is None
    """
    path = None
    """Current geometry data file path"""
    node_set_idx = None
    """Current editing node set, if is node, new node set is edited"""

    @classmethod
    def insert_diagrams_copies(cls, dup):
        """Insert diagrams after set diagram"""
        for i in range(0, dup.count):
            if dup.copy:
                cls.diagrams.insert(dup.insert_id, copy.deepcopy(cls.diagrams[dup.insert_id-1]))
            else:
                cls.diagrams.insert(dup.insert_id, cls.make_middle_diagram(dup))        
        
    @classmethod
    def make_middle_diagram(cls, dup):
        """return interpolated new diagram in set depth"""
        # TODO: instead copy compute middle diagram
        return copy.deepcopy(cls.diagrams[dup.dup1_id])
    
    @classmethod
    def init(cls, main_window):
        """Init class wit static method"""
        cls.main_window = main_window
        cls.data = data.DiagramSerializer(cls)
     
    @classmethod
    def save(cls):
        """save persistent data"""
        cls.config.save()
    
    @classmethod
    def remove_and_save_slice(cls, idx): 
        """Remove diagram from list and save it in file"""         
        del cls.diagrams[idx]
        
    @classmethod
    def open_shape_file(cls, file):
        """Open and add shape file"""
        if cls.diagram is not None:
            if not cls.diagram.shp.is_file_open(file):
                try:
                    disp = cls.diagram.shp.add_file(file)
                    if len(disp.errors)>0:
                        err_dialog = GMErrorDialog(cls.main_window)
                        err_dialog.open_error_report_dialog(disp.errors, msg="Shape file parsing errors:" ,  title=file)
                    return True
                except Exception as err:
                    err_dialog = GMErrorDialog(cls.main_window)
                    err_dialog.open_error_dialog("Can't open shapefile", err)
        return False
        
    @classmethod
    def open_file(cls, file):
        """
        save file name and timestamp
        """        
        cls.curr_file = file
        if file is None:
            cls.curr_file_timestamp = None
        else:
            try:
                cls.curr_file_timestamp = os.path.getmtime(file)
            except OSError:
                cls.curr_file_timestamp = None
        
    @classmethod
    def confront_file_timestamp(cls):
        """
        Compare file timestamp with file time and if is diferent
        show dialog, and reload file content.
        :return: if file is reloaded 
        """
        if cls.curr_file_timestamp is not None and \
            cls.curr_file is not None:
            try:
                timestamp = os.path.getmtime(cls.curr_file)
                if timestamp!=cls.curr_file_timestamp:
                    from PyQt5 import QtWidgets
                    msg = QtWidgets.QMessageBox()
                    msg.setText(
                        "File has been modified outside of Layer editor. Do you want to reload it?")
                    msg.setStandardButtons( QtWidgets.QMessageBox.Ignore | \
                        QtWidgets.QMessageBox.Reset)
                    msg.button(QtWidgets.QMessageBox.Reset).setText("Reload")
                    msg.setDefaultButton(QtWidgets.QMessageBox.Ignore);
                    ret = msg.exec_()
                    if ret==QtWidgets.QMessageBox.Reset: 
                        with open(cls.curr_file, 'r') as file_d:
                            cls.document = file_d.read()
                        cls.curr_file_timestamp = timestamp
                        cls.update()                        
                        return True
            except OSError:
                pass
        return False
        
