"""
Graphical object representing an action in pipeline.
@author: Tomáš Blažek
@contact: tomas.blazek@tul.cz
"""

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtWidgets import QGraphicsSimpleTextItem, QStyleOptionGraphicsItem, QGraphicsItem

from .g_action_background import GActionBackground, ActionStatus
from .g_port import GPort, GInputPort, GOutputPort
from frontend.analysis.util.editable_text import EditableLabel
from frontend.analysis.data.g_action_data_model import GActionData


class GAction(QtWidgets.QGraphicsPathItem):
    """Base class for all graphical actions."""
    def __init__(self, g_data_item, w_data_item, parent=None):
        """Initializes GAction.
        :param g_data_item: Object which holds data describing graphical properties of this GAction.
        :param w_data_item: Object which holds data about action in workflow.
        :param parent: Action which holds this subaction: this GAction is inside parent GAction.
        """
        super(GAction, self).__init__(parent)
        self._width = g_data_item.data(GActionData.WIDTH)
        self._height = g_data_item.data(GActionData.HEIGHT)
        self.in_ports = []
        self.out_ports = []

        self.setPos(QtCore.QPoint(g_data_item.data(GActionData.X), g_data_item.data(GActionData.Y)))

        self.setPen(QtGui.QPen(QtCore.Qt.black))
        self.setBrush(QtCore.Qt.darkGray)
        self.setAcceptHoverEvents(False)
        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemIsSelectable)
        self.setFlag(self.ItemSendsGeometryChanges)
        self.setZValue(0.0)

        self.resize_handle_width = 6

        self.type_name = QGraphicsSimpleTextItem(w_data_item.action_name, self)
        self.type_name.setPos(QtCore.QPoint(self.resize_handle_width, GPort.SIZE / 2))
        self.type_name.setBrush(QtCore.Qt.white)

        self._name = EditableLabel(g_data_item.data(GActionData.NAME), self)

        self.background = GActionBackground(self)
        self.background.setZValue(1.0)

        self.setCacheMode(self.DeviceCoordinateCache)

        self.g_data_item = g_data_item
        self.w_data_item = w_data_item

        if len(w_data_item.parameters.parameters) > 0:
            self._add_ports(len(w_data_item.arguments), w_data_item.parameters.parameters[-1].name is None)
        else:
            self._add_ports(len(w_data_item.arguments))


        self.level = 0
        self.height = self.height
        self.width = self.width

        self.progress = 0

        self.status = ActionStatus.IDLE

    def __repr__(self):
        return self.name + "\t" + str(self.level)

    @property
    def status(self):
        return self.background.status

    @status.setter
    def status(self, status):
        self.background.status = status
        self.setBrush(self.background.COLOR_PALETTE[self.status])
        self.update()

    @property
    def progress(self):
        return self.background.progress

    @progress.setter
    def progress(self, percent):
        self.background.update_gfx()
        self.background.progress = percent

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
        self._width = max(value, self.width_of_ports(),
                          self._name.boundingRect().width() + 2 * self.resize_handle_width,
                          self.type_name.boundingRect().width() + 2 * self.resize_handle_width)
        self.position_ports()
        self.update_gfx()
        # self.resize_handles.update_handles()

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._height = max(value, self._name.boundingRect().height() + GPort.SIZE +
                           self.type_name.boundingRect().height() + GPort.SIZE)
        self.position_ports()
        self.update_gfx()
        #self.resize_handles.update_handles()

    def boundingRect(self):
        return super(GAction, self).boundingRect().united(self.childrenBoundingRect())

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
        if not self.scene().action_name_changed(self.g_data_item, self.name) or self.name == "":
            return False
        self.width = self.width
        self.w_data_item.name(self.name)
        self.scene().update()
        return True

    def width_has_changed(self):
        self.scene().action_model.width_changed(self.g_data_item, self.width)

    def height_has_changed(self):
        self.scene().action_model.height_changed(self.g_data_item, self.height)

    def get_port(self, input, index):
        if input:
            return self.in_ports[index]
        else:
            return self.out_ports[index]

    def _add_ports(self, n_ports, appending=False):
        for i in range(n_ports):
            self.add_g_port(True, "Input Port" + str(i))
        if appending:
            self.add_g_port(True, "Input Port" + str(0))
            self.in_ports[-1].appending_port = True

        self.add_g_port(False, "Output Port")

    def inner_area(self):
        """Returns rectangle of the inner area of GAction."""
        return QRectF(self.resize_handle_width, GPort.SIZE / 2 + self.type_name.boundingRect().height() + 4,
                      self.width - 2 * self.resize_handle_width,
                      self.height - GPort.SIZE - self.type_name.boundingRect().height() - 4)

    def moveBy(self, dx, dy):
        super(GAction, self).moveBy(dx, dy)
        self.scene().move(self.g_data_item, self.x() + dx, self.y() + dy)

    def mousePressEvent(self, press_event):
        super(GAction, self).mousePressEvent(press_event)
        if press_event.button() == Qt.RightButton:
            self.setSelected(True)

    def mouseReleaseEvent(self, release_event):
        super(GAction, self).mouseReleaseEvent(release_event)
        temp = release_event.buttonDownScenePos(Qt.LeftButton)
        temp2 = release_event.pos()
        if release_event.buttonDownScenePos(Qt.LeftButton) != self.mapToScene(release_event.pos()):
            for item in self.scene().selectedItems():
                if self.scene().is_action(item):
                    self.scene().move(item.g_data_item, item.x(), item.y())

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
        return super(GAction, self).itemChange(change_type, value)

    def paint(self, paint, item, widget=None):
        """Update model of this GAction if necessary."""
        #self.setBrush(self.background.COLOR_PALETTE[self.status])
        super(GAction, self).paint(paint, item, widget)

    def paint_pixmap(self):
        progress = self.progress
        status = self.status
        self.progress = 0
        self.status = ActionStatus.IDLE
        rect = self.boundingRect()
        pixmap = QPixmap(rect.size().toSize())
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.translate(-rect.topLeft())

        for child in self.childItems():
            if child.flags() & QGraphicsItem.ItemStacksBehindParent:
                painter.save()
                painter.translate(child.mapToParent(self.pos()))
                child.paint(painter, QStyleOptionGraphicsItem(), None)
                painter.restore()

        self.paint(painter, QStyleOptionGraphicsItem())
        for child in self.childItems():
            if not child.flags() & QGraphicsItem.ItemStacksBehindParent:
                painter.save()
                painter.translate(child.mapToParent(self.pos()))
                child.paint(painter, QStyleOptionGraphicsItem(), None)
                painter.restore()

        painter.end()
        self.progress = progress
        self.status = status
        return pixmap

    def update_gfx(self):
        """Updates model of the GAction."""
        self.prepareGeometryChange()
        p = QtGui.QPainterPath()
        p.addRoundedRect(QtCore.QRectF(0, 0, self.width, self.height), 6, 6)
        p.addRoundedRect(self.inner_area(), 4, 4)
        self.setPath(p)
        self.update()
        self.background.update_gfx()

    def add_g_port(self, is_input, name=""):
        """Adds a port to this GAction.
        :param is_input: Decides if the new port will be input or output.
        """
        if is_input:
            self.in_ports.append(GInputPort(len(self.in_ports), QtCore.QPoint(0, 0), name, self))
        else:
            self.out_ports.append(GOutputPort(len(self.out_ports), QtCore.QPoint(0, 0), name, self))

        self.width = self.width

    def position_ports(self):
        if len(self.in_ports):
            space = self.width / (len(self.in_ports))
            for i in range(len(self.in_ports)):
                self.in_ports[i].setPos(QtCore.QPoint((i + 0.5) * space - GPort.RADIUS, -GPort.RADIUS))

        if len(self.out_ports):
            space = self.width / (len(self.out_ports))
            for i in range(len(self.out_ports)):
                self.out_ports[i].setPos(QtCore.QPoint((i + 0.5) * space - GPort.RADIUS, self.height - GPort.RADIUS))

    def width_of_ports(self):
        return max(len(self.in_ports) * GPort.SIZE, len(self.out_ports) * GPort.SIZE)

    def ports(self):
        """Returns input and output ports."""
        return self.in_ports + self.out_ports


