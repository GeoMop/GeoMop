from .action import Action
from .port import Port
from PyQt5 import QtGui, QtCore


class ActionForSubactions(Action):
    def __init__(self, parent=None, position=QtCore.QPoint(0, 0)):
        super(ActionForSubactions, self).__init__(parent, position)
        self.width = 200
        self.height = 200

    def _update_gfx(self):
        self.prepareGeometryChange()
        p = QtGui.QPainterPath()
        p.addRoundedRect(QtCore.QRectF(0, 0, self.width, self.height), 6, 6)
        p.addRoundedRect(QtCore.QRectF(5, 5, self.width - 10, self.height - 10), 5, 5)
        #p.moveTo(0, Port.SIZE / 2)
        #p.lineTo(self.width, Port.SIZE / 2)
        #p.moveTo(0, self.height - Port.SIZE / 2)
        #p.lineTo(self.width, self.height - Port.SIZE / 2)
        self.setPath(p)

