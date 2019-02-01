"""
Main window.
@author: Tomáš Blažek
@contact: tomas.blazek@tul.cz
"""
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from PyQt5 import QtWidgets, QtCore, QtGui
from .workspace import Workspace
from .action_editor_menu import ActionEditorMenu

class MainWidget(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWidget, self).__init__(parent)
        self.menu = self.menuBar()
        self.edit_menu = ActionEditorMenu(self)
        self.menu.addMenu(self.edit_menu)

        #self.dock = QtWidgets.QDockWidget("Diagram", self)
        #self.dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)

        #self.placeholder_view = QtWidgets.QGraphicsView(self.dock)
        #self.placeholder_view.resize(40,-1)
        #self.dock.setWidget(self.placeholder_view)
        #self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.dock)


        self.w = Workspace(self)
        self.setCentralWidget(self.w)
