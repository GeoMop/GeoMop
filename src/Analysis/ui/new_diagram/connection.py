"""
Representation of connection between two ports
@author: Tomáš Blažek
@contact: tomas.blazek@tul.cz
"""
from PyQt5 import QtWidgets, QtCore, QtGui
from .port import Port


class Connection(QtWidgets.QGraphicsPathItem):
    """Representation of connection between two ports"""
    def __init__(self, port1, port2=None, parent=None):
        super(Connection, self).__init__(parent)
        self.connection_set = False if port2 is None else True
        self.port1 = port1
        self.port2 = port2 if self.connection_set else Port(self.port1.get_connection_point())
        self.full_pen = QtGui.QPen(QtCore.Qt.black, 2)
        self.dash_pen = QtGui.QPen(QtCore.Qt.black, 2, QtCore.Qt.DashLine)
        self.setPen(self.full_pen)
        self.setZValue(1)

    @staticmethod
    def is_node():
        return False

    def is_connected(self, port):
        if port == self.port1:
            return True
        if port == self.port2:
            return True
        return False

    def __repr__(self):
        return "Connection from: " + str(self.port1) + " to: " + str(self.port2)

    def paint(self, painter, style, widget=None):
        style.state &= ~QtWidgets.QStyle.State_Selected
        self.update_gfx()
        super(Connection, self).paint(painter, style, widget)

    def update_gfx(self):
        #todo: draw short line from the port
        if self.isSelected():
            self.setPen(self.dash_pen)
        else:
            self.setPen(self.full_pen)
        self.prepareGeometryChange()
        path = QtGui.QPainterPath()
        p1 = self.port1.get_connection_point()
        p2 = self.port2.get_connection_point()
        c1 = QtCore.QPointF(p1.x(), (p2.y() + p1.y()) / 2)
        c2 = QtCore.QPointF(p2.x(), (p2.y() + p1.y()) / 2)
        path.moveTo(p1)
        path.cubicTo(c1, c2, p2)
        self.setPath(path)

    def set_port2_pos(self, pos):
        self.port2.setPos(self.mapFromScene(pos))
        self.update_gfx()

    def set_port2(self, port):
        self.port2 = port
        self.update_gfx()
