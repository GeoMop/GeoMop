"""CanvasWidget file"""
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
from leconfig import cfg
import PyQt5.QtCore as QtCore

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
        
        d = cfg.layers
        painter.drawText(QtCore.QPointF(d.x_view, d.__dy_row__), "Wiev")
        painter.drawText(QtCore.QPointF(d.x_edit, d.__dy_row__), "Edit")
        painter.drawText(QtCore.QPointF(d.x_label, d.__dy_row__), "Layer")
        painter.drawText(QtCore.QPointF(d.x_ilabel, d.__dy_row__), "Depth")
