from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QRadioButton, QWidget, QHBoxLayout


class RadioButton(QWidget):
    """Acts as QRadioButton, but has a line going from the edge of radio button to the right side of this widget."""
    def __init__(self, parent, block, view_button):
        super(RadioButton, self).__init__()
        self.view_button = view_button
        self._parent = parent
        self.block = block
        self.radio_button = QRadioButton(self)
        self.radio_button.setCursor(Qt.PointingHandCursor)
        layout = QHBoxLayout()
        layout.addWidget(self.radio_button, alignment=Qt.AlignCenter)
        layout.setContentsMargins(5, 0, 5, 0)
        self.setLayout(layout)

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setPen(self._parent.LINE_PEN)
        rb_rect = self.radio_button.rect()
        rect = self.rect()
        center = rect.center()
        painter.drawLine(center.x() + rb_rect.width() / 2, center.y(), rect.right(), center.y())
        super(RadioButton, self).paintEvent(event)
