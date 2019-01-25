"""
Start script that initializes main window and runs APP
@author: Tomáš Blažek
@contact: tomas.blazek@tul.cz
"""

from PyQt5 import QtWidgets, QtCore, QtGui
from .port import Port, InputPort, OutputPort


class Action(QtWidgets.QGraphicsPathItem):
    def __init__(self, parent=None, position=QtCore.QPoint(0, 0)):
        super(Action, self).__init__(parent)
        self.in_ports = []
        self.out_ports = []
        self.redraw = False
        self.width = 100
        self.height = 60
        self.setPos(position)
        self._update_gfx()

        for i in range(2):
            self.add_port(True)
        for i in range(3):
            self.add_port(False)

        self.text = QtWidgets.QGraphicsSimpleTextItem("Testing", self)
        self.text.setPos(QtCore.QPoint(0, 20))
        self.text.setBrush(QtCore.Qt.white)
        self.setPen(QtGui.QPen(QtCore.Qt.black))
        self.setBrush(QtCore.Qt.darkGray)
        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemIsSelectable)
        self.setFlag(self.ItemSendsGeometryChanges)

    @staticmethod
    def is_action():
        return True

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self._width = value
        self.redraw = True

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._height = value
        self.redraw = True

    def itemChange(self, change_type, value):
        for port in self.ports():
            for conn in port.connections:
                conn.update_gfx()
        return super(Action, self).itemChange(change_type, value)

    def paint(self, paint, item, widget=None):
        if self.redraw:
            self.redraw = False
            self._update_gfx()
        super(Action, self).paint(paint, item, widget)

    def _update_gfx(self):
        self.prepareGeometryChange()
        p = QtGui.QPainterPath()
        p.addRoundedRect(QtCore.QRectF(0, 0, self.width, self.height), 6, 6)
        p.moveTo(0, Port.SIZE/2)
        p.lineTo(self.width, Port.SIZE/2)
        p.moveTo(0, self.height - Port.SIZE/2)
        p.lineTo(self.width, self.height - Port.SIZE/2)
        self.setPath(p)

    def add_port(self, is_input):
        if (len(self.in_ports) + 1) * Port.SIZE > self.boundingRect().width():
            self.width = (len(self.in_ports) + 1) * Port.SIZE
        if is_input:
            space = self.width / (len(self.in_ports) + 1)
            for i in range(len(self.in_ports)):
                self.in_ports[i].setPos(QtCore.QPoint((i + 0.5) * space - Port.RADIUS, -Port.RADIUS))

            self.in_ports.append(InputPort(QtCore.QPoint((len(self.in_ports) + 0.5) * space - Port.RADIUS,
                                                         -Port.RADIUS), self))
        else:
            space = self.width / (len(self.out_ports) + 1)
            for i in range(len(self.out_ports)):
                self.out_ports[i].setPos(QtCore.QPoint((i + 0.5) * space - Port.RADIUS, self.height - Port.RADIUS))

            self.out_ports.append(OutputPort(QtCore.QPoint((len(self.out_ports) + 0.5) * space - Port.RADIUS,
                                                           self.height - Port.RADIUS), self))

    def ports(self):
        return self.in_ports + self.out_ports


