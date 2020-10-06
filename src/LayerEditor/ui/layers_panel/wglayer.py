from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QSizePolicy


class WGLayer(QWidget):
    """Widget for Layers Panel which represents layer"""
    def __init__(self, parent, layer_name):
        super(WGLayer, self).__init__(parent)
        self.name = QLabel(layer_name)
        layout = QHBoxLayout()
        layout.addWidget(self.name, alignment=Qt.AlignCenter)
        self.setLayout(layout)
        layout.setContentsMargins(5, 3, 5, 3)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        super(WGLayer, self).paintEvent(a0)
        painter = QPainter(self)
        painter.setPen(self.parent().LINE_PEN)
        x = self.rect().left() + self.parent().LINE_WIDTH / 2
        painter.drawLine(x, self.rect().top(), x, self.rect().bottom())


