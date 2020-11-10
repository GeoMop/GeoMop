from PyQt5 import QtGui
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QPainter, QPalette
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QSizePolicy

class InterfaceType:
    BOTH = 0
    BOTTOM = 1
    TOP = 2
    NONE = 3

class WGInterface(QWidget):
    """Widget for Layers Panel which represents an interface or fracture layer"""
    def __init__(self, parent, fracture_name=None, top_bot=InterfaceType.BOTH):
        """top_bot hold placement of this interface. top = True, bot = False, None otherwise"""
        super(WGInterface, self).__init__()
        self._parent = parent
        self.top_bot = top_bot
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        if fracture_name is not None:
            self.name = QLabel(" " + fracture_name + " ")
            self.name.setCursor(Qt.PointingHandCursor)
            font = self.name.font()
            self.name.setFont(font)
            self.name.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            self.name.setMargin(0)
            palette = self.name.palette()
            color = palette.color(QPalette.Window)
            self.name.setStyleSheet(f"QLabel {{background: {color.name()}}};")
            layout = QHBoxLayout()
            layout.addWidget(self.name, alignment=Qt.AlignCenter)
            self.setLayout(layout)
            layout.setContentsMargins(15, 0, 15, 0)
        else:
            #self.setMinimumHeight(self._parent.LINE_WIDTH+1)
            self.setMinimumHeight(QLabel().sizeHint().height())


    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        super(WGInterface, self).paintEvent(a0)
        painter = QPainter(self)
        painter.setPen(self._parent.LINE_PEN)
        center = self.rect().center()
        start = QPoint(self.rect().left() + self._parent.LINE_WIDTH * 0.5, center.y())

        painter.drawLine(start, QPoint(self.rect().right(), center.y()))

        if self.top_bot == InterfaceType.NONE:
            return

        if self.top_bot in [InterfaceType.TOP, InterfaceType.BOTH]:
            painter.drawLine(start,
                             self.rect().bottomLeft() + QPoint(self._parent.LINE_WIDTH * 0.5, 0))
        if self.top_bot in [InterfaceType.BOTTOM, InterfaceType.BOTH]:
            painter.drawLine(start,
                             self.rect().topLeft() + QPoint(self._parent.LINE_WIDTH * 0.5, 0))

