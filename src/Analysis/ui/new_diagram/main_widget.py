"""
Main window.
@author: Tomáš Blažek
@contact: tomas.blazek@tul.cz
"""
import os, sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QToolBox

from .menu.file_menu import FileMenu
from .composite_type_view import CompositeTypeView
from src.common.analysis.actions import tuple
from src.common.analysis.base import _Slot
from .tab_widget import TabWidget
from .toolbox_view import ToolboxView

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from PyQt5 import QtWidgets, QtCore
from .menu.edit_menu import EditMenu
from .g_action import GAction
from .tree_item import TreeItem
from .action_category import ActionCategory
from .g_input_action import GInputAction


class MainWidget(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWidget, self).__init__(parent)
        self._init_menu()
        self._init_docks()

        self.tab_widget = TabWidget(self, self.edit_menu)
        self.setCentralWidget(self.tab_widget)

        self.tab_widget.open_module("test_module.py")   # for testing purposes

        self._init_toolbox()

        self.data_view = CompositeTypeView()
        self.data_view.model()
        self.data_dock.setWidget(self.data_view)

        self.resize(1000, 500)

        self.file_menu.open.triggered.connect(self.tab_widget.open_module)

    def _init_menu(self):
        """Initializes menus"""
        self.menu_bar = self.menuBar()
        self.file_menu = FileMenu()
        self.menu_bar.addMenu(self.file_menu)
        self.edit_menu = EditMenu(self)
        self.menu_bar.addMenu(self.edit_menu)

    def _init_docks(self):
        """Initializes docks"""
        self.module_dock = QtWidgets.QDockWidget("Module", self)
        self.module_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, self.module_dock)

        self.toolbox_dock = QtWidgets.QDockWidget("Toolbox", self)
        self.toolbox_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.toolbox_dock)

        self.data_dock = QtWidgets.QDockWidget("Data/Config", self)
        self.data_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, self.data_dock)

    def _init_toolbox(self):
        toolbox_layout = ActionCategory()
        toolbox_layout2 = ActionCategory()
        ToolboxView(GInputAction(TreeItem(["Input", 0, 0, 50, 50]), _Slot(0)), toolbox_layout)
        ToolboxView(GAction(TreeItem(["Tuple", 0, 0, 50, 50]), tuple()), toolbox_layout2)

        self.toolBox = QToolBox()

        self.toolBox.addItem(toolbox_layout, "Input/Output")
        self.toolBox.addItem(toolbox_layout2, "Data manipulation")
        self.toolbox_dock.setWidget(self.toolBox)

