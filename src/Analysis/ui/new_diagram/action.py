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
from .graphics_data_model import ActionData


class Action(QtWidgets.QGraphicsPathItem):
    """Base class for all actions."""
    def __init__(self, graphics_data_item, parent=None):
        """Initializes action.
        :param parent: Action which holds this subaction: this action is inside parent action.
        :param position: Position of this action inside parent.
        """
        super(Action, self).__init__(parent)
        self._width = graphics_data_item.data(ActionData.WIDTH)
        self._height = graphics_data_item.data(ActionData.HEIGHT)
        self.in_ports = []
        self.out_ports = []

        self.resize_handle_width = 8

        self.setPos(QtCore.QPoint(graphics_data_item.data(ActionData.X), graphics_data_item.data(ActionData.Y)))
        self.handles = []

        self.setPen(QtGui.QPen(QtCore.Qt.black))
        self.setBrush(QtCore.Qt.darkGray)
        self.setAcceptHoverEvents(False)
        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemIsSelectable)
        self.setFlag(self.ItemSendsGeometryChanges)
        self.setZValue(0.0)
        self._name = EditableLabel(graphics_data_item.data(ActionData.NAME), self)

        self.resize_handles = RectResizeHandles(self, self.resize_handle_width,
                                                self.resize_handle_width * 2)

        self._add_ports()
        print(self.in_ports)
        self.in_ports[-1].appending_port = True


        self.setCacheMode(self.DeviceCoordinateCache)

        self.graphics_data_item = graphics_data_item

        self.level = 0

    def __repr__(self):
        return self.name + "\t" + str(self.level)

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

    def next_actions(self):
        ret = []
        for port in self.out_ports:
            for conn in port.connections:
                item = conn.port2.parentItem()
                if item not in ret:
                    ret.append(item)
        return ret

    def previous_actions(self):
        ret = []
        for port in self.in_ports:
            for conn in port.connections:
                item = conn.port1.parentItem()
                if item not in ret:
                    ret.append(item)
        return ret

    def name_change(self):
        self.scene().update()
        self.width = self.width

    def name_has_changed(self):
        if not self.scene().action_name_changed(self.graphics_data_item, self.name) or self.name == "":
            return False
        self.width = self.width
        self.scene().update()
        return True

    def width_has_changed(self):
        self.scene().action_model.width_changed(self.graphics_data_item, self.width)

    def height_has_changed(self):
        self.scene().action_model.height_changed(self.graphics_data_item, self.height)

    def get_port(self, input, index):
        if input:
            return self.in_ports[index]
        else:
            return self.out_ports[index]

    def _add_ports(self):
        for i in range(2):
            self.add_port(True, "Input Port" + str(i))
        for i in range(3):
            self.add_port(False, "Output Port" + str(i))



    def inner_area(self):
        """Returns rectangle of the inner area of action."""
        return QRectF(self.resize_handle_width, Port.SIZE / 2,
                      self.width - 2 * self.resize_handle_width, self.height - Port.SIZE)

    def moveBy(self, dx, dy):
        super(Action, self).moveBy(dx, dy)
        self.scene().move(self.graphics_data_item, self.x() + dx, self.y() + dy)

    def mousePressEvent(self, press_event):
        super(Action, self).mousePressEvent(press_event)
        if press_event.button() == Qt.RightButton:
            self.setSelected(True)

    def mouseReleaseEvent(self, release_event):
        super(Action, self).mouseReleaseEvent(release_event)
        if release_event.buttonDownScenePos(Qt.LeftButton) != release_event.pos():
            for item in self.scene().selectedItems():
                if self.scene().is_action(item):
                    self.scene().move(item.graphics_data_item, item.x(), item.y())

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

    def add_port(self, is_input, name=""):
        """Adds a port to this action.
        :param is_input: Decides if the new port will be input or output.
        """
        if is_input:
            self.in_ports.append(InputPort(len(self.in_ports), QtCore.QPoint(0, 0), name, self))
        else:
            self.out_ports.append(OutputPort(len(self.out_ports), QtCore.QPoint(0, 0), name, self))

        self.width = self.width

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


