from PyQt5 import QtWidgets, QtCore, QtGui
from workspace import Workspace

class MainWidget(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWidget, self).__init__(parent)
        self.dock = QtWidgets.QDockWidget("Nodes", self)
        self.dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)

        w = Workspace(self.dock)

        self.dock.setWidget(w)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.dock)
