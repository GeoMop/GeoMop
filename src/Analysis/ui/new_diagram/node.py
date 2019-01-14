"""
Start script that initializes main window and runs APP
@author: Tomáš Blažek
@contact: tomas.blazek@tul.cz
"""

from PyQt5 import QtWidgets, QtCore, QtGui
from .port import Port

class Node(QtWidgets.QGraphicsPathItem):
    WIDTH = 100
    HEIGHT = 60

    def __init__(self, parent=None, position=QtCore.QPoint(0, 0)):
        super(Node, self).__init__(parent)
        self.setPos(position)
        position2 = QtCore.QPoint(self.WIDTH, self.HEIGHT)
        p = QtGui.QPainterPath()
        p.addRoundedRect(QtCore.QRectF(0, 0, self.WIDTH, self.HEIGHT), 5, 5)
        p.moveTo(0, 16)
        p.lineTo(self.WIDTH, 16)
        p.moveTo(0, self.HEIGHT - 16)
        p.lineTo(self.WIDTH, self.HEIGHT - 16)
        self.port = Port(QtCore.QPoint(self.WIDTH / 2 - Port.RADIUS, 3), self)
        self.in_ports = []
        self.out_ports = []

        self.text = QtWidgets.QGraphicsSimpleTextItem("Testing", self)
        self.text.setPos(QtCore.QPoint(0, 20))
        self.text.setBrush(QtCore.Qt.white)
        self.setPath(p)
        self.setPen(QtGui.QPen(QtCore.Qt.black))
        self.setBrush(QtCore.Qt.darkGray)
        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemIsSelectable)

    def paint(self, QPainter, QStyleOptionGraphicsItem, widget=None):
        super(Node, self).paint(QPainter, QStyleOptionGraphicsItem, widget)

    def add_port(self, in_port):
        i=1
        #self.in_ports.append(Port(QtCore.QPoint(position.x() + self.WIDTH / 2 - Port.RADIUS, position.y() + 3), self))


