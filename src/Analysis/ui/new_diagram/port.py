"""
Start script that initializes main window and runs APP
@author: Tomáš Blažek
@contact: tomas.blazek@tul.cz
"""

from PyQt5 import QtWidgets, QtCore, QtGui


class Port(QtWidgets.QGraphicsPathItem):
    RADIUS = 6
    BORDER = 3
    SIZE = RADIUS * 2 + BORDER * 2

    def __init__(self, pos, parent=None):
        super(Port, self).__init__(parent)
        if pos is not None:
            self.setPos(pos)
        p = QtGui.QPainterPath()
        p.addEllipse(QtCore.QRectF(0, 0, self.RADIUS * 2, self.RADIUS * 2))
        p.moveTo(self.RADIUS, self.RADIUS)
        self.setPath(p)
        self.setPen(QtCore.Qt.black)
        self.setBrush(QtCore.Qt.white)
        self.setFlag(self.ItemIsSelectable)
        self.up_dir = None

    def __repr__(self):
        return "Port: " + str(self.mapToScene(self.pos()))

    def mousePressEvent(self, event):
        self.scene().parent().add_connection(self)
        super(Port, self).mousePressEvent(event)

    def get_connection_point(self):
        return self.mapToScene(QtCore.QPoint(self.RADIUS, self.RADIUS))

    def shape(self):
        p = QtGui.QPainterPath()
        p.addRect(self.path().boundingRect())
        return p


class InputPort(Port):
    def __init__(self, pos, parent=None):
        super(InputPort, self).__init__(pos, parent)
        self.up_dir = True


class OutputPort(Port):
    def __init__(self, pos, parent=None):
        super(OutputPort, self).__init__(pos, parent)
        self.up_dir = False
