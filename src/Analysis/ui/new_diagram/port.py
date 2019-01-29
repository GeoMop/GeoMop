"""
Representation of ports to which a connection can be attached
@author: Tomáš Blažek
@contact: tomas.blazek@tul.cz
"""
from PyQt5 import QtWidgets, QtCore, QtGui


class Port(QtWidgets.QGraphicsPathItem):
    """Base class for ports"""
    RADIUS = 6
    BORDER = 3
    SIZE = RADIUS * 2 + BORDER * 2

    def __init__(self, pos, name="", parent=None):
        """Initializes class
        :param pos: Position of this action inside parent action
        :param parent: This port will be part of parent action
        """
        super(Port, self).__init__(parent)
        self.name = name
        if pos is not None:
            self.setPos(pos)
        p = QtGui.QPainterPath()
        p.addEllipse(QtCore.QRectF(0, 0, self.RADIUS * 2, self.RADIUS * 2))
        p.moveTo(self.RADIUS, self.RADIUS)
        self.setPath(p)
        self.setPen(QtCore.Qt.black)
        self.setBrush(QtCore.Qt.white)
        self.connections = []

    def __repr__(self):
        return "Action: '" + self.parentItem().name + "' Port: '" + self.name + "'"

    def mousePressEvent(self, event):
        """If the port is pressed create a connection"""
        self.scene().parent().add_connection(self)

    def get_connection_point(self):
        """Return scene coordinates to draw connection"""
        return self.mapToScene(QtCore.QPoint(self.RADIUS, self.RADIUS))

class InputPort(Port):
    """Class for input data"""
    def __init__(self, pos, name="", parent=None):
        """Initializes class
        :param pos: Position of this action inside parent action
        :param parent: This port will be part of parent action
        """
        super(InputPort, self).__init__(pos, name, parent)


class OutputPort(Port):
    """Class for output data"""
    def __init__(self, pos, name="", parent=None):
        """Initializes class
        :param pos: Position of this action inside parent action
        :param parent: This port will be part of parent action
        """
        super(OutputPort, self).__init__(pos, name, parent)
