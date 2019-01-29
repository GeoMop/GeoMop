"""
Special action which can contain subactions for repeating processes
@author: Tomáš Blažek
@contact: tomas.blazek@tul.cz
"""
from .action import Action
from .port import Port
from PyQt5 import QtGui, QtCore


class ActionForSubactions(Action):
    """Base class for actions which contain subactions"""
    def __init__(self, parent=None, position=QtCore.QPoint(0, 0)):
        """
        :param parent: Action which holds this subaction: this action is inside parent action
        :param position: Position of this action
        """
        super(ActionForSubactions, self).__init__(parent, position)
        self.width = 200
        self.height = 200

    def update_gfx(self):
        """Updates model of the action"""
        self.prepareGeometryChange()
        p = QtGui.QPainterPath()
        p.addRoundedRect(QtCore.QRectF(0, 0, self.width, self.height), 6, 6)
        p.addRoundedRect(QtCore.QRectF(5, 5, self.width - 10, self.height - 10), 5, 5)
        #p.moveTo(0, Port.SIZE / 2)
        #p.lineTo(self.width, Port.SIZE / 2)
        #p.moveTo(0, self.height - Port.SIZE / 2)
        #p.lineTo(self.width, self.height - Port.SIZE / 2)
        self.setPath(p)

