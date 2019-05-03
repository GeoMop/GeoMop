"""
Main window.
@author: Tomáš Blažek
@contact: tomas.blazek@tul.cz
"""
import os, sys

from PyQt5.QtWidgets import QToolBox, QSizePolicy, QVBoxLayout, QWidget, QTabWidget, QApplication

from .composite_type_view import CompositeTypeView
from src.common.analysis.actions import Tuple
from src.common.analysis.workflow import _Slot
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
from src.common.analysis import workflow as wf


class MainWidget(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        @wf.workflow
        def test_workflow(a, b):
            c = actions.Tuple(a).name("c")
            d = actions.Tuple(a, b)
            e = actions.Tuple(c, d)
            return e


        super(MainWidget, self).__init__(parent)
        self.menu = self.menuBar()
        self.edit_menu = ActionEditorMenu(self)
        self.menu.addMenu(self.edit_menu)

        self.dock = QtWidgets.QDockWidget("Graphical data", self)
        self.dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        self.dock2 = QtWidgets.QDockWidget("Toolbox", self)
        self.dock2.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        self.dock3 = QtWidgets.QDockWidget("Data/Config", self)
        self.dock3.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)

        self.w = Workspace(WorkflowInterface(test_workflow), self)
        self.w2 = Workspace(WorkflowInterface(test_workflow), self)

        self.toolbox_layout = ActionCategory()
        self.toolbox_layout2 = ActionCategory()
        self.item1 = ToolboxView(GInputAction(TreeItem(["Input", 0, 0, 50, 50]), _Slot(0)), self.toolbox_layout)
        self.item11 = ToolboxView(GAction(TreeItem(["Tuple", 0, 0, 50, 50]), Tuple()), self.toolbox_layout2)

        self.toolBox = QToolBox()


        self.toolBox.addItem(self.toolbox_layout, "Input/Output")
        self.toolBox.addItem(self.toolbox_layout2, "Data manipulation")

        self.dock2.setWidget(self.toolBox)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.dock2)

        self.view = QtWidgets.QTreeView()
        self.view.setModel(self.w.scene.action_model)

        self.dock.setWidget(self.view)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock)

        self.data_view = CompositeTypeView()
        temp = self.data_view.model()
        self.dock3.setWidget(self.data_view)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock3)

        self.resize(1000, 500)
        self.tab_widget = TabWidget(self.edit_menu)
        self.setCentralWidget(self.tab_widget)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setTabShape(1)
        self.tab_widget.addTab(self.w, "first_file.file")
        self.tab_widget.addTab(self.w2, "second_file.file")


    def eventFilter(self, QObject, QEvent):
        return True
