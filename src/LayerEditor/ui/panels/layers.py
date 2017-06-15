"""CanvasWidget file"""
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui

class Layers(QtWidgets.QWidget):
    """GeoMop design area"""

    def __init__(self, parent=None):
        """
        Inicialize window

        Args:
            parent (QWidget): parent window ( empty is None)
        """
        super(Layers, self).__init__(parent)
        
 #   def mousePressEvent(self, event):

  #  def keyPressEvent(self, event):

    def paintEvent(self, event=None):
        """Overloadet QWidget paint function"""
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
