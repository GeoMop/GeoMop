from PyQt5 import QtGui
from PyQt5.QtCore import QPoint, Qt, QRect
from PyQt5.QtGui import QPainter, QPen, QFont
from PyQt5.QtWidgets import QWidget, QApplication


class Joiner(QWidget):
    """Widget for Layers Panel which connects two or three interfaces"""
    def __init__(self, parent, top, bottom, middle=None):
        super(Joiner, self).__init__(parent)
        self.top = top
        self.bottom = bottom
        self.middle = middle
        dpi = QApplication.primaryScreen().physicalDotsPerInch()
        if self.font().pixelSize() == -1:
            self.setFixedWidth(self.font().pointSize() / 72 * dpi)
        else:
            self.setFixedWidth(self.font().pixelSize())
        self.pen = QPen(self.parent().LINE_PEN)
        self.pen.setCapStyle(Qt.RoundCap)

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        half_line_width = self.parent().LINE_WIDTH / 2
        painter = QPainter(self)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)
        painter.setPen(self.pen)

        painter.setClipRect(QRect(QPoint(self.rect().left(),
                                         self.top.rect().center().y() - half_line_width),
                                  QPoint(self.rect().right(),
                                         half_line_width + self.rect().bottom() - (self.bottom.rect().height() - self.bottom.rect().center().y()))))
        if self.middle is not None:
            middle_right = QPoint(self.rect().right() - half_line_width,
                                  self.middle.rect().center().y() + self.top.rect().height())
            painter.drawLine(QPoint(self.rect().left(), middle_right.y()), middle_right)
        else:
            middle_right = QPoint(self.rect().right() - half_line_width,
                                  self.rect().center().y)

        painter.drawLine(QPoint(self.rect().left() + half_line_width - 1,
                                self.top.rect().center().y()),
                         middle_right)
        painter.drawLine(middle_right,
                         QPoint(self.rect().left() + half_line_width - 1,
                                self.rect().bottom() + 1 - (self.bottom.rect().height() - self.bottom.rect().center().y())))



