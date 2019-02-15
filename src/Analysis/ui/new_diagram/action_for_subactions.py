"""
Special action which can contain subactions for repeating processes.
@author: Tomáš Blažek
@contact: tomas.blazek@tul.cz
"""
from .action import Action
from .port import Port
from PyQt5 import QtGui, QtCore, QtWidgets


class ActionForSubactions(Action):
    """Base class for actions which contain subactions."""
    def __init__(self, parent=None, position=QtCore.QPoint(0, 0)):
        """
        :param parent: Action which holds this subaction: this action is inside parent action.
        :param position: Position of this action.
        """
        super(ActionForSubactions, self).__init__(parent, position)
        self.name = "While loop"
        self.width = 200
        self.height = 200

