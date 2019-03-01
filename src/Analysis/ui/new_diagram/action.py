"""
Action representing a task in pipeline.
@author: Tomáš Blažek
@contact: tomas.blazek@tul.cz
"""

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt, QRectF
from .port import Port, InputPort, OutputPort
from .editable_text import EditableLabel
from .rect_resize_handles import RectResizeHandles


class Action(QtWidgets.QGraphicsPathItem):
    """Base class for all actions."""
    def __init__(self, index, data_item, parent=None, position=QtCore.QPoint(0, 0), width=50, height=50):
        """Initializes action.
        :param parent: Action which holds this subaction: this action is inside parent action.
        :param position: Position of this action inside parent.
        """
        super(Action, self).__init__(parent)
        self._width = width
        self._height = height
        self.in_ports = []
        self.out_ports = []

        self.resize_handle_width = 8

        self.setPos(position)
        self.handles = []

        self.setPen(QtGui.QPen(QtCore.Qt.black))
        self.setBrush(QtCore.Qt.darkGray)
        self.setAcceptHoverEvents(False)
        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemIsSelectable)
        self.setFlag(self.ItemSendsGeometryChanges)
        self.setZValue(0.0)
        self._name = EditableLabel("Testing", self)

        self.resize_handles = RectResizeHandles(self, self.resize_handle_width,
                                                self.resize_handle_width * 2)

        self.add_ports()

        self.setCacheMode(self.DeviceCoordinateCache)

        self.index = index
        self.data_item = data_item

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
        self._width = max(value, self.width_of_ports(), self._name.boundingRect().width() + 2 * self.resize_handle_width)
        self.position_ports()
        self.update_gfx()
        self.resize_handles.update_handles()

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._height = max(value, self._name.boundingRect().height() + Port.SIZE)
        self.position_ports()
        self.update_gfx()
        self.resize_handles.update_handles()

    def get_port(self, input, index):
        if input:
            return self.in_ports[index]
        else:
            return self.out_ports[index]

    def add_ports(self):
        for i in range(2):
            self._add_port(True, "Input Port" + str(i))
        for i in range(3):
            self._add_port(False, "Output Port" + str(i))

        self.width = self.width

    def inner_area(self):
        """Returns rectangle of the inner area of action."""
        return QRectF(self.resize_handle_width, Port.SIZE / 2,
                      self.width - 2 * self.resize_handle_width, self.height - Port.SIZE)

    def mouseReleaseEvent(self, release_event):
        super(Action, self).mouseReleaseEvent(release_event)
        if release_event.buttonDownScenePos(Qt.LeftButton) != release_event.pos():
            for item in self.scene().selectedItems():
                if self.scene().is_action(item):
                    self.scene().move(item.data_item, item.pos())

    def mouseMoveEvent(self, move_event):
        super(Action, self).mouseMoveEvent(move_event)

    def mouseDoubleClickEvent(self, event):
        if self._name.contains(self.mapToItem(self._name, event.pos())):
            self._name.mouseDoubleClickEvent(event)

    def itemChange(self, change_type, value):
        """Update all connections which are attached to this action."""
        if change_type == self.ItemPositionHasChanged:
            for port in self.ports():
                for conn in port.connections:
                    conn.update_gfx()

        '''
        elif change_type == self.ItemParentChange:
            self.setPos(self.mapToItem(value, self.mapToScene(self.pos())))
        '''
        return super(Action, self).itemChange(change_type, value)

    def paint(self, paint, item, widget=None):
        """Update model of this action if necessary."""
        super(Action, self).paint(paint, item, widget)

    def update_gfx(self):
        """Updates model of the action."""
        self.prepareGeometryChange()
        p = QtGui.QPainterPath()
        p.addRoundedRect(QtCore.QRectF(0, 0, self.width, self.height), 6, 6)
        p.addRoundedRect(self.inner_area(), 4, 4)
        self.setPath(p)
        self.update()

    def _add_port(self, is_input, name=""):
        """Adds a port to this action.
        :param is_input: Decides if the new port will be input or output.
        """
        if is_input:
            self.in_ports.append(InputPort(len(self.in_ports), QtCore.QPoint(0, 0), name, self))
        else:
            self.out_ports.append(OutputPort(len(self.out_ports), QtCore.QPoint(0, 0), name, self))

    def position_ports(self):
        if len(self.in_ports):
            space = self.width / (len(self.in_ports))
            for i in range(len(self.in_ports)):
                self.in_ports[i].setPos(QtCore.QPoint((i + 0.5) * space - Port.RADIUS, -Port.RADIUS))

        if len(self.out_ports):
            space = self.width / (len(self.out_ports))
            for i in range(len(self.out_ports)):
                self.out_ports[i].setPos(QtCore.QPoint((i + 0.5) * space - Port.RADIUS, self.height - Port.RADIUS))

    def width_of_ports(self):
        return max(len(self.in_ports) * Port.SIZE, len(self.out_ports) * Port.SIZE)

    def ports(self):
        """Returns input and output ports."""
        return self.in_ports + self.out_ports


