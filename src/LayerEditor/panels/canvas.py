# pylint: disable=E1002
"""CanvasWidget file"""

import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui

class CanvasWidget(QtWidgets.QWidget):
    """GeoMop design area"""

    def __init__(self, parent=None):
        """
        Inicialize window

        Args:
            parent (QWidget): parent window ( empty is None)
        """
        super(CanvasWidget, self).__init__(parent)
        self.setSizePolicy(
            QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding))
        self.setMinimumSize(QtCore.QSize(500, 500))
        self._pictures = None

 #   def mousePressEvent(self, event):

  #  def keyPressEvent(self, event):

    def paintEvent(self, event=None):
        """Overloadet QWidget paint function"""
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        if self._pictures:
            for picture in self._pictures:
                target = painter.window()
                pixmap = picture
                if pixmap:
                    source = pixmap.rect()
                    painter.drawPixmap(target, pixmap, source)

    def set_undercoat(self, pictures):
        """Set undercoat picture after change and redraw canvas"""
        self._pictures = pictures
        self.repaint(0, 0, -1, -1)
