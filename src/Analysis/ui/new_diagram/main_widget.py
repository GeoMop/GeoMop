"""
Main window.
@author: Tomáš Blažek
@contact: tomas.blazek@tul.cz
"""
import os, sys

from PyQt5.QtWidgets import QToolBox, QSizePolicy, QVBoxLayout, QWidget, QTabWidget, QApplication, QMenuBar

from .file_menu import FileMenu
from .module_view import ModuleView
from .composite_type_view import CompositeTypeView
from src.common.analysis.actions import tuple
from src.common.analysis.base import _Slot
from .tab_widget import TabWidget
from .toolbox_view import ToolboxView

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from PyQt5 import QtWidgets, QtCore, QtGui
from .workspace import Workspace
from .action_editor_menu import ActionEditorMenu
from .g_action import GAction
from .tree_item import TreeItem
from .action_category import ActionCategory
from .g_input_action import GInputAction
from .output_action import OutputGAction
from src.common.analysis import actions
from .workflow_interface import WorkflowInterface
from src.common.analysis import base as wf


class MainWidget(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        self.module = wf._Module.create_from_file("test_module.py")

        super(MainWidget, self).__init__(parent)
        self._init_menu()
        self._init_docks()

        self.tab_widget = TabWidget(self, self.edit_menu)
        self.setCentralWidget(self.tab_widget)
        self.tab_widget.open_module("test_module.py")

        self.toolbox_layout = ActionCategory()
        self.toolbox_layout2 = ActionCategory()
        self.item1 = ToolboxView(GInputAction(TreeItem(["Input", 0, 0, 50, 50]), _Slot(0)), self.toolbox_layout)
        self.item11 = ToolboxView(GAction(TreeItem(["Tuple", 0, 0, 50, 50]), tuple()), self.toolbox_layout2)

        self.toolBox = QToolBox()


        self.toolBox.addItem(self.toolbox_layout, "Input/Output")
        self.toolBox.addItem(self.toolbox_layout2, "Data manipulation")

        self.dock2.setWidget(self.toolBox)


        self.data_view = CompositeTypeView()
        temp = self.data_view.model()
        self.dock3.setWidget(self.data_view)

        self.resize(1000, 500)

        self.file_menu.open.triggered.connect(self.tab_widget.open_module)

    def _init_menu(self):
        self.menu_bar = self.menuBar()
        self.file_menu = FileMenu()
        self.menu_bar.addMenu(self.file_menu)
        self.edit_menu = ActionEditorMenu(self)
        self.menu_bar.addMenu(self.edit_menu)

    def _init_docks(self):
        self.module_dock = QtWidgets.QDockWidget("Module", self)
        self.module_dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.module_dock)

        self.dock2 = QtWidgets.QDockWidget("Toolbox", self)
        self.dock2.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock2)

        self.dock3 = QtWidgets.QDockWidget("Data/Config", self)
        self.dock3.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock3)

    def eventFilter(self, QObject, QEvent):
        return True

