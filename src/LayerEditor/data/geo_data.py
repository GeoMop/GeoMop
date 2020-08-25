"""Analyzis Editor static parameters

.. codeauthor:: Pavel Richter <pavel.richter@tul.cz>
"""

import logging
import os
from copy import deepcopy

from PyQt5.QtCore import QObject

import gm_base.config as cfg
from gm_base.geomop_shortcuts import shortcuts
from LayerEditor.helpers import keyboard_shortcuts_definition as shortcuts_definition
from gm_base.geomop_util.logging import LOGGER_PREFIX
from gm_base.geomop_util import Serializable
from gm_base.geomop_dialogs import GMErrorDialog
from gm_base.geomop_analysis import Analysis, InvalidAnalysis
from LayerEditor.data.le_serializer import LESerializer



class GeometryData(QObject):
    """Main data class representing geometry data file"""
    diagrams = []
    """List of diagram data"""
    history = None
    """History for current geometry data"""
    layers = None
    """Layers structure"""
    curr_diagram =  None
    """Current diagram data"""
    le_serializer = None
    """Data from geometry file"""
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

    def __init__(self):
        self.init()

    def init(self):
        """Init class with static method"""
        #cls.history = le_data.GlobalHistory(cls)
        #cls.layers = le_data.Layers(cls.history)
        #cls.reinit()
        self.le_serializer = LESerializer(self)

    def reset_data(self):
        #self.reinit()
        self.diagrams = []
        #self.layers.delete()
        self.diagram = None

    # def reinit(self):
    #     """Release all diagram data"""
    #     self.layer_heads = regions.LayerHeads(self)
    #     le_data.Diagram.reinit(self.layer_heads, self.history)

    def confront_file_timestamp(self):
        """
        Compare file timestamp with file time and if is diferent
        show dialog, and reload file content.
        :return: if file is reloaded
        """
        if self.curr_file_timestamp is not None and \
            self.curr_file is not None:
            try:
                timestamp = os.path.getmtime(self.curr_file)
                if timestamp!=self.curr_file_timestamp:
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
                        with open(self.curr_file, 'r') as file_d:
                            self.document = file_d.read()
                        self.curr_file_timestamp = timestamp
                        return True
            except OSError:
                pass
        return False

    # @classmethod
    # def reload_surfaces(cls, id=None):
    #     """Reload surface panel"""
    #     if cls.main_window is not None:
    #         cls.main_window.wg_surface_panel.change_surface(id)
    #
    # @classmethod
    # def get_curr_surfaces(cls):
    #     """Get current surface id from surface panel"""
    #     return  cls.main_window.wg_surface_panel.get_surface_id()
    #
    #
    # @classmethod
    # def changed(cls):
    #     """is file changed"""
    #     return cls.history.is_changes()
    #
    # @classmethod
    # def add_region(cls, color, name, dim, step,  boundary, not_used):
    #     """Add region"""
    #     le_data.Diagram.add_region(color, name, dim, step,  boundary, not_used)
    #
    # @classmethod
    # def add_shapes_to_region(cls, is_fracture, layer_id, layer_name, topology_idx, regions):
    #     """Add shape to region"""
    #     le_data.Diagram.add_shapes_to_region(is_fracture, layer_id, layer_name, topology_idx, regions)
    #
    # @classmethod
    # def get_shapes_from_region(cls, is_fracture, layer_id):
    #     """Get shapes from region"""
    #     return le_data.Diagram.get_shapes_from_region(is_fracture, layer_id)
    #
    # @classmethod
    # def set_curr_diagram(cls, i):
    #     """Set i diagram as edited. Return old diagram id"""
    #     ret = cls.diagram_id()
    #     cls.diagram = cls.diagrams[i]
    #     return ret
    #
    # @classmethod
    # def diagram_id(cls):
    #     """Return current diagram id"""
    #     if not cls.diagram in cls.diagrams:
    #         return None
    #     return cls.diagrams.index(cls.diagram)
    #
    # @classmethod
    # def get_curr_diagram(cls):
    #     """Get id of diagram that is edited."""
    #     return cls.diagrams.index(cls.diagram)
    #
    # @classmethod
    # def insert_diagrams_copies(cls, dup, oper):
    #     """Insert diagrams after set diagram and
    #     move topologies accoding oper"""
    #     for i in range(0, dup.count):
    #         if dup.copy:
    #             cls.diagrams.insert(dup.insert_id, cls.diagrams[dup.insert_id-1].dcopy())
    #         else:
    #             cls.diagrams.insert(dup.insert_id, cls.make_middle_diagram(dup))
    #     if oper is le_data.TopologyOperations.insert:
    #         cls.diagrams[dup.insert_id].move_diagram_topologies(dup.insert_id, cls.diagrams)
    #     elif oper is le_data.TopologyOperations.insert_next:
    #         cls.diagrams[dup.insert_id].move_diagram_topologies(dup.insert_id+1, cls.diagrams)
    #
    # @classmethod
    # def insert_diagrams(cls, diagrams, id, oper):
    #     """Insert diagrams after set diagram and
    #     move topologies accoding oper"""
    #     for i in range(0, len(diagrams)):
    #         cls.diagrams.insert(id+i, diagrams[i])
    #         cls.diagrams[id+i].join()
    #     if oper is le_data.TopologyOperations.insert or \
    #         oper is le_data.TopologyOperations.insert_next:
    #         cls.diagrams[id].move_diagram_topologies(id+len(diagrams), cls.diagrams)
    #
    # @classmethod
    # def remove_and_save_diagram(cls, idx):
    #     """Remove diagram from list and save it in history variable"""
    #     cls.diagrams[idx].release()
    #     cls.history.removed_diagrams.append(cls.diagrams[idx])
    #     curr_id = cls.diagram_id()
    #     del cls.diagrams[idx]
    #     le_data.Diagram.fix_topologies(cls.diagrams)
    #     return curr_id == idx
    #
    # @classmethod
    # def make_middle_diagram(cls, dup):
    #     """return interpolated new diagram in set elevation"""
    #     # TODO: instead copy compute middle diagram
    #     return cls.diagrams[dup.dup1_id].dcopy()
    #
    #
    #
    # @staticmethod
    # def get_current_view(location):
    #     """Return current view"""
    #     return CurrentView(location)
    #
    # @classmethod
    # def set_main(cls, main_window):
    #     """Init class wit static method"""
    #     cls.main_window = main_window
    #     CurrentView.set_cfg(cls)
    #
    # @classmethod
    # def open_shape_file(cls, file):
    #     """Open and add shape file"""
    #     if cls.diagram is not None:
    #         if not cls.diagram.shp.is_file_open(file):
    #             try:
    #                 disp = cls.diagram.add_file(file)
    #                 if len(disp.errors)>0:
    #                     err_dialog = GMErrorDialog(cls.main_window)
    #                     err_dialog.open_error_report_dialog(disp.errors, msg="Shape file parsing errors:" ,  title=file)
    #                 return True
    #             except Exception as err:
    #                 err_dialog = GMErrorDialog(cls.main_window)
    #                 err_dialog.open_error_dialog("Can't open shapefile", err)
    #     return False

    def save_file(self, file=None):
        """save to json file"""
        if file is None:
            file = self.curr_file
        self.le_serializer.save(self, file)
        self.history.saved()

        self.curr_file = file
        try:
            self.curr_file_timestamp = os.path.getmtime(file)
        except OSError:
            self.curr_file_timestamp = None

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


    # @classmethod
    # def open_recent_file(cls, file_name):
    #     """
    #     read file from recent files
    #
    #     return: if file have good format (boolean)
    #     """
    #     try:
    #         cls.open_file(file_name)
    #         cls.config.update_current_workdir(file_name)
    #         cls.config.add_recent_file(file_name)
    #         return True
    #     except (RuntimeError, IOError) as err:
    #         if cls.main_window is not None:
    #             err_dialog = GMErrorDialog(cls.main_window)
    #             err_dialog.open_error_dialog("Can't open file", err)
    #         else:
    #             raise err
    #     return False
    #
    # @classmethod
    # def get_shortcut(cls, name):
    #     """Locate a keyboard shortcut by its action name.
    #
    #     :param str name: name of the shortcut
    #     :return: the assigned shortcut
    #     :rtype: :py:class:`helpers.keyboard_shortcuts.KeyboardShortcut` or ``None``
    #     """
    #     shortcut = None
    #     if name in shortcuts_definition.SYSTEM_SHORTCUTS:
    #         shortcut = shortcuts_definition.SYSTEM_SHORTCUTS[name]
    #     elif name in shortcuts_definition.DEFAULT_USER_SHORTCUTS:
    #         shortcut = shortcuts_definition.DEFAULT_USER_SHORTCUTS[name]
    #     if shortcut:
    #         return shortcuts.get_shortcut(shortcut)
    #     return None

    def load(self, filename):
        self.le_serializer.load(self, filename)
