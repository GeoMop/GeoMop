"""
Action representing a task in pipeline
@author: Tomáš Blažek
@contact: tomas.blazek@tul.cz
"""

from PyQt5 import QtWidgets, QtCore, QtGui
from .port import Port, InputPort, OutputPort
from .editable_text import EditableLabel


class Action(QtWidgets.QGraphicsPathItem):
    """Base class for all actions"""
    def __init__(self, parent=None, position=QtCore.QPoint(0, 0)):
        """Initializes action
        :param parent: Action which holds this subaction: this action is inside parent action
        :param position: Position of this action inside parent
        """
        super(Action, self).__init__(parent)
        self.in_ports = []
        self.out_ports = []
        self.redraw = False
        self.width = 100
        self.height = 60
        self.setPos(position)
        self.update_gfx()

        self.setPen(QtGui.QPen(QtCore.Qt.black))
        self.setBrush(QtCore.Qt.darkGray)
        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemIsSelectable)
        self.setFlag(self.ItemSendsGeometryChanges)

        # testing purposes
        for i in range(2):
            self.add_port(True, "Input Port" + str(i))
        for i in range(3):
            self.add_port(False, "Output Port" + str(i))

        self._name = EditableLabel("Testing", self)

    def mouseDoubleClickEvent(self, event):
        if self._name.contains(self.mapToItem(self._name, event.pos())):
            self._name.mouseDoubleClickEvent(event)

    @property
    def name(self):
        return self._name.toPlainText()

    @name.setter
    def name(self, name):
        self._name.setPlainText(name)

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
        """Update all connections which are attached to this action"""
        for port in self.ports():
            for conn in port.connections:
                conn.update_gfx()
        return super(Action, self).itemChange(change_type, value)

    def paint(self, paint, item, widget=None):
        """Update model of this action if necessary"""
        if self.redraw:
            self.redraw = False
            self.update_gfx()
        super(Action, self).paint(paint, item, widget)

    def update_gfx(self):
        """Updates model of the action"""
        self.prepareGeometryChange()
        p = QtGui.QPainterPath()
        p.addRoundedRect(QtCore.QRectF(0, 0, self.width, self.height), 6, 6)
        p.moveTo(0, Port.SIZE/2)
        p.lineTo(self.width, Port.SIZE/2)
        p.moveTo(0, self.height - Port.SIZE/2)
        p.lineTo(self.width, self.height - Port.SIZE/2)
        self.setPath(p)

    def add_port(self, is_input, name=""):
        """Adds a port to this action
        :param is_input: Decides if the new port will be input or output
        """
        if (len(self.in_ports) + 1) * Port.SIZE > self.boundingRect().width():
            self.width = (len(self.in_ports) + 1) * Port.SIZE
        if is_input:
            space = self.width / (len(self.in_ports) + 1)
            for i in range(len(self.in_ports)):
                self.in_ports[i].setPos(QtCore.QPoint((i + 0.5) * space - Port.RADIUS, -Port.RADIUS))

            self.in_ports.append(InputPort(QtCore.QPoint((len(self.in_ports) + 0.5) * space - Port.RADIUS,
                                                         -Port.RADIUS), name, self))
        else:
            space = self.width / (len(self.out_ports) + 1)
            for i in range(len(self.out_ports)):
                self.out_ports[i].setPos(QtCore.QPoint((i + 0.5) * space - Port.RADIUS, self.height - Port.RADIUS))

            self.out_ports.append(OutputPort(QtCore.QPoint((len(self.out_ports) + 0.5) * space - Port.RADIUS,
                                                           self.height - Port.RADIUS), name, self))

    def ports(self):
        """Returns input and output ports"""
        return self.in_ports + self.out_ports


