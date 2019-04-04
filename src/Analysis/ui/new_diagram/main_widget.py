"""
Main window.
@author: Tomáš Blažek
@contact: tomas.blazek@tul.cz
"""
import os, sys

from PyQt5.QtWidgets import QToolBox, QSizePolicy, QVBoxLayout, QWidget

from .toolbox_view import ToolboxView

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from PyQt5 import QtWidgets, QtCore, QtGui
from .workspace import Workspace
from .action_editor_menu import ActionEditorMenu
from .action import Action
from .tree_item import TreeItem
from .action_category import ActionCategory
from .input_action import InputAction
from .output_action import OutputAction


class MainWidget(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWidget, self).__init__(parent)
        self.menu = self.menuBar()
        self.edit_menu = ActionEditorMenu(self)
        self.menu.addMenu(self.edit_menu)

        self.dock = QtWidgets.QDockWidget("Diagram", self)
        self.dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        self.dock2 = QtWidgets.QDockWidget("Toolbox", self)
        self.dock2.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)

        self.w = Workspace(self)

        self.toolbox_layout = ActionCategory()
        self.toolbox_layout2 = ActionCategory()
        self.item1 = ToolboxView(InputAction(TreeItem(["Input", 0,0,50,50])), self.toolbox_layout)
        self.item2 = ToolboxView(OutputAction(TreeItem(["Output", 0, 0, 50, 50])), self.toolbox_layout)
        self.item3 = ToolboxView(Action(TreeItem(["calibration", 0, 0, 50, 50])), self.toolbox_layout)
        self.item4 = ToolboxView(Action(TreeItem(["action", 0, 0, 50, 50])), self.toolbox_layout)
        self.item5 = ToolboxView(Action(TreeItem(["for loop", 0, 0, 50, 50])), self.toolbox_layout)
        self.item6 = ToolboxView(Action(TreeItem(["calibration", 0, 0, 50, 50])), self.toolbox_layout)
        self.item11 = ToolboxView(Action(TreeItem(["action", 0, 0, 50, 50])), self.toolbox_layout2)
        self.item21 = ToolboxView(Action(TreeItem(["for loop", 0, 0, 50, 50])), self.toolbox_layout2)
        self.item31 = ToolboxView(Action(TreeItem(["calibration", 0, 0, 50, 50])), self.toolbox_layout2)
        self.item41 = ToolboxView(Action(TreeItem(["action", 0, 0, 50, 50])), self.toolbox_layout2)
        self.item51 = ToolboxView(Action(TreeItem(["for loop", 0, 0, 50, 50])), self.toolbox_layout2)
        self.item61 = ToolboxView(Action(TreeItem(["calibration", 0, 0, 50, 50])), self.toolbox_layout2)

        self.toolBox = QToolBox()


        self.toolBox.addItem(self.toolbox_layout, "First Category")
        self.toolBox.addItem(self.toolbox_layout2, "Second Category")

        self.dock2.setWidget(self.toolBox)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.dock2)

        self.view = QtWidgets.QTreeView()
        self.view.setModel(self.w.scene.action_model)

        self.dock.setWidget(self.view)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock)

        self.resize(1000, 500)
        self.setCentralWidget(self.w)

    def eventFilter(self, QObject, QEvent):
        print("hi")
        return True
