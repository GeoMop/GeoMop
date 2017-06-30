"""CanvasWidget file"""
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
from leconfig import cfg
import PyQt5.QtCore as QtCore
from ui.data import FractureInterface

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

    def _paint_fracture(self, painter, y, x1, x2, dx, interface):
        """Paint layer with fracture name"""
        painter.drawLine(x1-2*dx, y, interface.fracture.rect.left()-dx, y)
        painter.drawText(interface.fracture.rect.bottomLeft(), interface.fracture.name)
        painter.drawLine(interface.fracture.rect.right()+dx, y, x2-2*dx, y)
        
    def _paint_checkbox(self, painter, rect, value):
        """Paint layer with fracture name"""
        painter.drawRect(rect)
        if value:
            painter.drawLine(rect.left(), rect.top()+rect.height()*2/3,rect.left()+rect.width()/3)
            painter.drawLine(rect.left()+rect.width()/3, rect.right(), rect.top()+rect.height()/3)
            
        

    def paintEvent(self, event=None):
        """Overloadet QWidget paint function"""
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        
        d = cfg.layers
        painter.setFont(d.font)
        painter.drawText(QtCore.QPointF(d.x_view, d.__dy_row__+d.y_font), "View")
        painter.drawText(QtCore.QPointF(d.x_edit, d.__dy_row__+d.y_font), "Edit")
        painter.drawText(QtCore.QPointF(d.x_label, d.__dy_row__+d.y_font), "Layer")
        painter.drawText(QtCore.QPointF(d.x_ilabel, d.__dy_row__+d.y_font), "Depth")
        
        for i in range(0, len(d.interfaces)):
            # interface            
            if d.interfaces[i].y_top is None:
                if d.interfaces[i].fracture is None:
                    painter.drawLine(d.x_label-2*d.__dx__, d.interfaces[i].y, d.x_ilabel-2*d.__dx__, d.interfaces[i].y)
                else:
                    self._paint_fracture(painter, d.interfaces[i].y, d.x_label, d.x_ilabel, d.__dx__,d.interfaces[i])
            else:
                if d.interfaces[i].fracture is None or d.interfaces[i].fracture.type != FractureInterface.top :
                    painter.drawLine(d.x_label-2*d.__dx__, d.interfaces[i].y_top, d.x_ilabel-2*d.__dx__, d.interfaces[i].y_top)
                else:    
                    self._paint_fracture(painter, d.interfaces[i].y_top, d.x_label, d.x_ilabel, d.__dx__,d.interfaces[i])
                painter.drawLine(d.x_ilabel-2*d.__dx__, d.interfaces[i].y_top, d.x_ilabel-d.__dx__, d.interfaces[i].y)
                if d.interfaces[i].fracture is not None and d.interfaces[i].fracture.type != FractureInterface.own :
                    self._paint_fracture(painter, d.interfaces[i].y, d.x_label, d.x_ilabel+d.__dx__, d.__dx__,d.interfaces[i])
                painter.drawLine(d.x_ilabel-d.__dx__, d.interfaces[i].y, d.x_ilabel-d.__dx__, d.interfaces[i].y_bottom)
                if d.interfaces[i].fracture is None or d.interfaces[i].fracture.type != FractureInterface.bottom :
                    painter.drawLine(d.x_label-2*d.__dx__, d.interfaces[i].y_bottom, d.x_ilabel-2*d.__dx__, d.interfaces[i].y_bottom)
                else:    
                    self._paint_fracture(painter, d.interfaces[i].y_bottom, d.x_label, d.x_ilabel, d.__dx__,d.interfaces[i])                
                if self.view_rect1 is not None:
                    self._paint_checkbox(self, painter, d.interfaces[i].view_rect1, d.interfaces[i].self.viewed1)
                if self.view_rect2 is not None:
                    self._paint_checkbox(self, painter, d.interfaces[i].view_rect2, d.interfaces[i].self.viewed2)
                if self.edit_rect1 is not None:
                    self._paint_checkbox(self, painter, d.interfaces[i].edit_rect1, d.interfaces[i].self.edited1)
                if self.edit_rect2 is not None:
                    self._paint_checkbox(self, painter, d.interfaces[i].edit_rect2, d.interfaces[i].self.edited2)
            painter.drawText(d.interfaces[i].rect.bottomLeft(), d.interfaces[i].depth)        
            #layers
            if i<len(d.layers):
                painter.drawText(d.layers[i].rect, d.layers[i].name)
                if i+1<len(d.interfaces):
                    top = d.interfaces[i].y
                    bottom = d.interfaces[i-1].y
                    if d.interfaces[i].y_bottom is not None:
                        top = d.interfaces[i].y_bottom
                    if d.interfaces[i+1].y_top is not None:
                        bottom = d.interfaces[i-1].y_top
                    painter.drawLine(d.x_label-2*d.__dx__, top, d.x_label-2*d.__dx__, bottom)
            
