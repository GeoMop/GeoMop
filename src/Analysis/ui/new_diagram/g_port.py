"""
Representation of ports to which a connection can be attached.
@author: Tomáš Blažek
@contact: tomas.blazek@tul.cz
"""
from PyQt5 import QtWidgets, QtCore, QtGui
# todo: Add port which will have plus inside and when clicked will create new port.
# todo: If it will be clicked with new connection, new port is created and connection is connected to the new port
from PyQt5.QtCore import QPoint


class GPort(QtWidgets.QGraphicsPathItem):
    """Base class for ports."""
    RADIUS = 6
    BORDER = 2
    SIZE = RADIUS * 2 + BORDER * 2

    def __init__(self, index, pos=QPoint(0,0), name="", parent=None):
        """Initializes class.
        :param pos: Position of this action inside parent action.
        :param parent: This port will be part of parent action.
        """
        super(GPort, self).__init__(parent)
        self.name = name
        if pos is not None:
            self.setPos(pos)

        self._appending_port = False
        self.setPath(self.draw_port_path())
        self.setPen(QtCore.Qt.black)
        self.setBrush(QtCore.Qt.white)
        self.connections = []
        self.setAcceptHoverEvents(True)
        self.setZValue(1.0)
        self.setFlag(self.ItemSendsGeometryChanges)

        self.setToolTip("Type")

        self.index = index

    @property
    def appending_port(self):
        return self._appending_port

    @appending_port.setter
    def appending_port(self, value):
        if value != self._appending_port:
            self._appending_port = value
            self.setPath(self.draw_port_path())

    def draw_port_path(self):
        if self.appending_port:
            p = QtGui.QPainterPath()
            p.addEllipse(QtCore.QRectF(0, 0, self.RADIUS * 2, self.RADIUS * 2))
            p.moveTo(self.RADIUS - 3, self.RADIUS)
            p.lineTo(self.RADIUS + 3, self.RADIUS)
            p.moveTo(self.RADIUS, self.RADIUS - 3)
            p.lineTo(self.RADIUS, self.RADIUS + 3)
        else:
            p = QtGui.QPainterPath()
            p.addEllipse(QtCore.QRectF(0, 0, self.RADIUS * 2, self.RADIUS * 2))
        return p

    def __repr__(self):
        return "Action: '" + self.parentItem().name + "' Port: '" + self.name + "'"

    def itemChange(self, change_type, value):
        if change_type == QtWidgets.QGraphicsItem.ItemPositionHasChanged:
            for conn in self.connections:
                conn.update_gfx()
        return super(GPort, self).itemChange(change_type, value)

    def setEnabled(self, bool):
        super(GPort, self).setEnabled(bool)
        self.setBrush(QtCore.Qt.white if bool else QtCore.Qt.gray)

    def mousePressEvent(self, event):
        """If the port is pressed create a connection."""
        if event.button() == QtCore.Qt.LeftButton:
            self.scene().add_connection(self)

    def get_connection_point(self):
        """Return scene coordinates to draw connection."""
        return self.mapToScene(QtCore.QPoint(self.RADIUS, self.RADIUS))


class GInputPort(GPort):
    """Class for input data."""
    def __init__(self, index, pos=QPoint(0,0), name="", parent=None):
        """Initializes class.
        :param pos: Position of this action inside parent action.
        :param parent: This port will be part of parent action.
        """
        super(GInputPort, self).__init__(index, pos, name, parent)


class GOutputPort(GPort):
    """Class for output data."""
    def __init__(self, index, pos=QPoint(0,0), name="", parent=None):
        """Initializes class.
        :param pos: Position of this action inside parent action.
        :param parent: This port will be part of parent action.
        """
        super(GOutputPort, self).__init__(index, pos, name, parent)
