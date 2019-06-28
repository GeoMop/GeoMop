"""
Main window.
@author: Tomáš Blažek
@contact: tomas.blazek@tul.cz
"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QToolBox

from frontend.analysis.menu.file_menu import FileMenu
from frontend.analysis.widgets.composite_type_view import CompositeTypeView
from common.analysis.action_workflow import SlotInstance

from .tab_widget import TabWidget
from .toolbox_view import ToolboxView

import common.analysis.action_instance as instance
import common.analysis.action_base as base


from PyQt5 import QtWidgets
from frontend.analysis.menu.edit_menu import EditMenu
from frontend.analysis.graphical_items.g_action import GAction
from frontend.analysis.data.tree_item import TreeItem
from frontend.analysis.widgets.action_category import ActionCategory
from frontend.analysis.graphical_items.g_input_action import GInputAction


class MainWidget(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWidget, self).__init__(parent)
        self._init_menu()
        self._init_docks()

        self.tab_widget = TabWidget(self, self.edit_menu)
        self.setCentralWidget(self.tab_widget)

        #self.tab_widget.open_module("C:\\Users\\samot\\PycharmProjects\\GeoMop\\testing\\common\\analysis\\analysis_in.py")   # for testing purposes

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
        self.data_dock.hide()

    def _init_toolbox(self):
        toolbox_layout = ActionCategory()
        toolbox_layout2 = ActionCategory()
        ToolboxView(GInputAction(TreeItem(["Input", 0, 0, 50, 50]), SlotInstance("a")), toolbox_layout)
        ToolboxView(GAction(TreeItem(["List", 0, 0, 50, 50]), instance.ActionInstance.create( base.List())), toolbox_layout2)

        self.toolBox = QToolBox()

        self.toolBox.addItem(toolbox_layout, "Input/Output")
        self.toolBox.addItem(toolbox_layout2, "Data manipulation")
        self.toolbox_dock.setWidget(self.toolBox)

