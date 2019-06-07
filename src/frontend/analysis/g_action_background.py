from PyQt5.QtCore import Qt, QRect, QPoint
from PyQt5.QtWidgets import QGraphicsRectItem


class ActionStatus:
    ERROR = 0
    OK = 1
    PAUSED = 2
    IDLE = 3


class GActionBackground(QGraphicsRectItem):
    COLOR_PALETTE = {
        ActionStatus.ERROR: Qt.darkRed,
        ActionStatus.OK: Qt.darkGreen,
        ActionStatus.PAUSED: Qt.darkYellow,
        ActionStatus.IDLE: Qt.darkGray
    }
    def __init__(self, parent):
        super(GActionBackground, self).__init__(parent)
        self.parent = parent
        self.setBrush(Qt.white)
        self.setPen(Qt.transparent)
        self.setFlag(self.ItemStacksBehindParent, True)
        self.progress = 0
        self.status = ActionStatus.IDLE

    def update_gfx(self):
        self.prepareGeometryChange()
        self.setRect(self.parent.inner_area())

    def paint(self, painter, style, widget=None):
        super(GActionBackground, self).paint(painter, style, widget)
        if self.progress > 0 and self.progress < 100:
            painter.fillRect(QRect(self.rect().topLeft().toPoint(),
                                   QPoint(self.rect().left() + (self.progress/100)*self.rect().width(),
                                          self.rect().bottom())), self.COLOR_PALETTE[self.status])


