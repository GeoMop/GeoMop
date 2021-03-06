"""Analyzis Editor static parameters

.. codeauthor:: Pavel Richter <pavel.richter@tul.cz>
"""

import logging
import os
from copy import deepcopy
import gm_base.config as cfg
from gm_base.geomop_shortcuts import shortcuts
from LayerEditor.helpers import keyboard_shortcuts_definition as shortcuts_definition
from gm_base.geomop_util.logging import LOGGER_PREFIX
from gm_base.geomop_util import Serializable
from gm_base.geomop_dialogs import GMErrorDialog
from gm_base.geomop_analysis import Analysis, InvalidAnalysis
from LayerEditor.ui import data as le_data
from LayerEditor.ui.helpers import CurrentView
from LayerEditor.ui.panels import regions

class _Config:
    """Class for Analyzis serialization"""

    __serializable__ = Serializable(
        excluded=['observers']
    )

    DEBUG_MODE = False
    """debug mode changes the behaviour"""

    SERIAL_FILE = "LayerEditorData"
    """Serialize class file"""
    
    COUNT_RECENT_FILES = 5
    """Count of recent files"""
    
    CONTEXT_NAME = 'LayerEditor'
    
    CONFIG_DIR = os.path.join(cfg.__config_dir__, 'LayerEditor')

    def __init__(self, **kwargs):
        

        self.observers = []
        """objects to be notified of changes"""
        self._analysis = None
        self._workspace = None

        self._analysis = kwargs.get('_analysis', None)
        self._workspace = kwargs.get('_workspace', None)
        self.show_init_area = kwargs.get('show_init_area', True)
            
        self.current_workdir = os.getcwd()
        """directory of the most recently opened data file"""
        self.recent_files = kwargs.get('recent_files', [])
        """a list of recently opened files"""

        self.shortcuts = kwargs.get('shortcuts',
                                   deepcopy(shortcuts_definition.DEFAULT_USER_SHORTCUTS))
        """user customizable keyboard shortcuts"""

    def save(self):
        """Save config data"""
        cfg.save_config_file(self.__class__.SERIAL_FILE, self, self.CONFIG_DIR)
        
    @staticmethod
    def open():
        """Open config from saved file (if exists)."""
        config = cfg.get_config_file(_Config.SERIAL_FILE,
                                     _Config.CONFIG_DIR, cls=_Config)
        if config is None:
            config = _Config()
        return config
        
    def add_recent_file(self, file_name):
        """
        If file is in array, move it top, else add file to top and delete last
        file if is needed. Relevant format files is keep
        """
        # 0 files
        if len(self.recent_files) == 0:
            self.recent_files.append(file_name)
            self.save()
            return
        # init for
        if self.recent_files[0] == file_name:
            self.save()
            return        
        last_file = self.recent_files[0]
        self.recent_files[0] = file_name

        for i in range(1, len(self.recent_files)):
            if file_name == self.recent_files[i]:
                # added file is in list
                self.recent_files[i] = last_file
                self.save()
                return
            last_file_pom = self.recent_files[i]
            self.recent_files[i] = last_file
            last_file = last_file_pom
            # recent files is max+1, but first is not displayed
            if self.__class__.COUNT_RECENT_FILES < i+1:
                self.save()
                return
        # add last file
        self.recent_files.append(last_file)
        self.save()

    @property
    def data_dir(self):
        """Data directory - either an analysis dir or the last used dir."""
        if self.workspace and self.analysis:
            return os.path.join(self.workspace, self.analysis)
        else:
            return self.current_workdir
            
    def update_current_workdir(self, file_name):
        """Save dir from last used file"""
        analysis_directory = None
        directory = os.path.dirname(os.path.realpath(file_name))
        if self.workspace is not None and self.analysis is not None:
            analysis_dir = os.path.join(self.workspace, self.analysis)
        if analysis_directory is None or directory != analysis_dir:
            self.current_workdir = directory

    @property
    def workspace(self):
        """path to workspace"""
        return self._workspace

    @workspace.setter
    def workspace(self, value):
        if value == '' or value is None:
            self._workspace = None
        if value != self._workspace:
            # close analysis if workspace is changed
            self.analysis = None
        self._workspace = value

    @property
    def analysis(self):
        """name of the analysis in the workspace"""
        return self._analysis

    @analysis.setter
    def analysis(self, value):
        if value == '' or value is None:
            self._analysis = None
            Analysis.current = None
        else:
            self._analysis = value
            try:
                analysis = Analysis.open(self._workspace, self._analysis)
            except InvalidAnalysis:
                self._analysis = None
            else:
                Analysis.current = analysis
        self.notify_all()
    
    def notify_all(self):
        """Notify all observers about changes."""
        for observer in self.observers:
            observer.config_changed()


class LEConfig:
    """Static data class"""
    config = _Config.open()
    """Serialized variables"""
    logger = logging.getLogger(LOGGER_PREFIX +  config.CONTEXT_NAME)
    """root context logger"""    
    diagrams = []
    """List of diagram data"""
    history = None
    """History for current geometry data"""
    layers = None
    """Layers structure"""
    diagram =  None
    """Current diagram data"""
    le_serializer = None
    """Data from geometry file"""    
    main_window = None    
    """parent of dialogs"""
    curr_file = None
    """Name of open file"""
    curr_file_timestamp = None
    """    
    Timestamp of opened file, if editor text is 
    imported or new timestamp is None
    """
    #path = None
    """Current geometry data file path"""
    geomop_root = os.path.dirname(os.path.dirname(
                  os.path.dirname(os.path.realpath(__file__))))
    """Path to the root directory of the GeoMop installation."""
    layer_heads = None
    # Data model for Regions panel.


    @classmethod
    def reload_surfaces(cls, id=None):
        """Reload surface panel"""
        if cls.main_window is not None:
            cls.main_window.wg_surface_panel.change_surface(id)
        
    @classmethod
    def get_curr_surfaces(cls):
        """Get current surface id from surface panel"""
        return  cls.main_window.wg_surface_panel.get_surface_id()
        

    @classmethod
    def changed(cls):
        """is file changed"""
        return cls.history.is_changes()
    
    @classmethod
    def add_region(cls, color, name, dim, step,  boundary, not_used):
        """Add region"""
        le_data.Diagram.add_region(color, name, dim, step,  boundary, not_used)
        
    @classmethod
    def add_shapes_to_region(cls, is_fracture, layer_id, layer_name, topology_idx, regions):
        """Add shape to region"""
        le_data.Diagram.add_shapes_to_region(is_fracture, layer_id, layer_name, topology_idx, regions)
    
    @classmethod
    def get_shapes_from_region(cls, is_fracture, layer_id):
        """Get shapes from region""" 
        return le_data.Diagram.get_shapes_from_region(is_fracture, layer_id)
        
    @classmethod
    def set_curr_diagram(cls, i):
        """Set i diagram as edited. Return old diagram id"""
        ret = cls.diagram_id()
        cls.diagram = cls.diagrams[i]
        return ret
    
    @classmethod
    def diagram_id(cls):
        """Return current diagram id"""
        if not cls.diagram in cls.diagrams:
            return None
        return cls.diagrams.index(cls.diagram)
    
    @classmethod
    def get_curr_diagram(cls):
        """Get id of diagram that is edited."""
        return cls.diagrams.index(cls.diagram)        

    @classmethod
    def insert_diagrams_copies(cls, dup, oper):
        """Insert diagrams after set diagram and
        move topologies accoding oper"""
        for i in range(0, dup.count):
            if dup.copy:
                cls.diagrams.insert(dup.insert_id, cls.diagrams[dup.insert_id-1].dcopy())
            else:
                cls.diagrams.insert(dup.insert_id, cls.make_middle_diagram(dup))
        if oper is le_data.TopologyOperations.insert:
            cls.diagrams[dup.insert_id].move_diagram_topologies(dup.insert_id, cls.diagrams)
        elif oper is le_data.TopologyOperations.insert_next:
            cls.diagrams[dup.insert_id].move_diagram_topologies(dup.insert_id+1, cls.diagrams)
            
    @classmethod
    def insert_diagrams(cls, diagrams, id, oper):
        """Insert diagrams after set diagram and
        move topologies accoding oper"""
        for i in range(0, len(diagrams)):
            cls.diagrams.insert(id+i, diagrams[i])
            cls.diagrams[id+i].join()
        if oper is le_data.TopologyOperations.insert or \
            oper is le_data.TopologyOperations.insert_next:
            cls.diagrams[id].move_diagram_topologies(id+len(diagrams), cls.diagrams)
            
    @classmethod
    def remove_and_save_diagram(cls, idx): 
        """Remove diagram from list and save it in history variable"""
        cls.diagrams[idx].release()
        cls.history.removed_diagrams.append(cls.diagrams[idx])
        curr_id = cls.diagram_id()
        del cls.diagrams[idx]
        le_data.Diagram.fix_topologies(cls.diagrams)
        return curr_id == idx
        
    @classmethod
    def make_middle_diagram(cls, dup):
        """return interpolated new diagram in set elevation"""
        # TODO: instead copy compute middle diagram
        return cls.diagrams[dup.dup1_id].dcopy()
        
    @classmethod
    def reinit(cls):
        """Release all diagram data"""
        cls.layer_heads = regions.LayerHeads(cls)
        le_data.Diagram.reinit(cls.layer_heads, cls.history)
    
    @classmethod
    def init(cls):
        """Init class with static method"""
        cls.history = le_data.GlobalHistory(cls)
        cls.layers = le_data.Layers(cls.history)
        cls.reinit()
        cls.le_serializer = le_data.LESerializer(cls)
        
    @staticmethod
    def get_current_view(location):
        """Return current view"""
        return CurrentView(location)
        
    @classmethod
    def set_main(cls, main_window):
        """Init class wit static method"""
        cls.main_window = main_window
        CurrentView.set_cfg(cls)
     
    @classmethod
    def open_shape_file(cls, file):
        """Open and add shape file"""
        if cls.diagram is not None:
            if not cls.diagram.shp.is_file_open(file):
                try:
                    disp = cls.diagram.add_file(file)
                    if len(disp.errors)>0:
                        err_dialog = GMErrorDialog(cls.main_window)
                        err_dialog.open_error_report_dialog(disp.errors, msg="Shape file parsing errors:" ,  title=file)
                    return True
                except Exception as err:
                    err_dialog = GMErrorDialog(cls.main_window)
                    err_dialog.open_error_dialog("Can't open shapefile", err)
        return False
        
    @classmethod
    def new_file(cls):
        """Open new empty file"""
        if cls.main_window is None:
            return
        cls.main_window.release_data(cls.diagram_id())
        cls.init()
        cls.le_serializer.set_new(cls)
        cls.curr_file = None
        cls.curr_file_timestamp = None
        
    @classmethod
    def save_file(cls, file=None):
        """save to json file"""
        if file is None:
            file = cls.curr_file
        cls.le_serializer.save(cls, file)
        cls.history.saved()
        cls.config.update_current_workdir(file)
        cls.config.add_recent_file(file)
        cls.curr_file = file
        try:
            cls.curr_file_timestamp = os.path.getmtime(file)
        except OSError:
            cls.curr_file_timestamp = None

    @classmethod
    def open_file(cls, file):
        """
        save file name and timestamp
        """        
        cls.main_window.release_data(cls.diagram_id())
        cls.curr_file = file
        cls.config.update_current_workdir(file)
        if file is None:
            cls.curr_file_timestamp = None
        else:
            try:
                cls.curr_file_timestamp = os.path.getmtime(file)
            except OSError:
                cls.curr_file_timestamp = None
        cls.history.remove_all()        
        cls.le_serializer.load(cls, file)
        cls.main_window.refresh_all()
        cls.config.add_recent_file(file)
        
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
                        return True
            except OSError:
                pass
        return False
        
    @classmethod
    def open_recent_file(cls, file_name):
        """
        read file from recent files

        return: if file have good format (boolean)
        """
        try:
            cls.open_file(file_name)
            cls.config.update_current_workdir(file_name)
            cls.config.add_recent_file(file_name)
            return True
        except (RuntimeError, IOError) as err:
            if cls.main_window is not None:
                err_dialog = GMErrorDialog(cls.main_window)
                err_dialog.open_error_dialog("Can't open file", err)
            else:
                raise err
        return False

    @classmethod
    def get_shortcut(cls, name):
        """Locate a keyboard shortcut by its action name.

        :param str name: name of the shortcut
        :return: the assigned shortcut
        :rtype: :py:class:`helpers.keyboard_shortcuts.KeyboardShortcut` or ``None``
        """
        shortcut = None
        if name in shortcuts_definition.SYSTEM_SHORTCUTS:
            shortcut = shortcuts_definition.SYSTEM_SHORTCUTS[name]
        elif name in shortcuts_definition.DEFAULT_USER_SHORTCUTS:
            shortcut = shortcuts_definition.DEFAULT_USER_SHORTCUTS[name]
        if shortcut:
            return shortcuts.get_shortcut(shortcut)
        return None


