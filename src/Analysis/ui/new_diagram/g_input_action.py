from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QPainterPath

from .gport import GPort
from .g_action import GAction


class GInputAction(GAction):
    def __init__(self, g_data_item, w_data_item, parent=None):
        super(GInputAction, self).__init__(g_data_item, w_data_item, parent)


    def update_gfx(self):
        super(GInputAction, self).update_gfx()
        self.prepareGeometryChange()
        p = self.path()
        rect = self.boundingRect()
        p.moveTo(rect.topLeft() + QPoint(rect.width() / 2 - 15, 0))
        p.lineTo(rect.topLeft() + QPoint(rect.width() / 2 - 15, GPort.RADIUS*2))
        p.lineTo(rect.topLeft() + QPoint(rect.width() / 2 + 15, GPort.RADIUS*2))
        p.lineTo(rect.topLeft() + QPoint(rect.width() / 2 + 15, 0))
        p.lineTo(rect.topLeft() + QPoint(rect.width() / 2 + 15, GPort.RADIUS * 2))
        p.lineTo(rect.topLeft() + QPoint(rect.width() / 2 - 15, GPort.RADIUS * 2))
        p.moveTo(rect.topLeft() + QPoint(rect.width() / 2, -20))
        p.lineTo(rect.topLeft() + QPoint(rect.width() / 2, GPort.RADIUS * 2))
        p.lineTo(rect.topLeft() + QPoint(rect.width() / 2 + GPort.RADIUS, 0))
        p.lineTo(rect.topLeft() + QPoint(rect.width() / 2, GPort.RADIUS * 2))
        p.lineTo(rect.topLeft() + QPoint(rect.width() / 2 - GPort.RADIUS, 0))
        p.lineTo(rect.topLeft() + QPoint(rect.width() / 2, GPort.RADIUS * 2))
        self.setPath(p)

