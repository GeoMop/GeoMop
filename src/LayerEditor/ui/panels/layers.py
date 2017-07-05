"""CanvasWidget file"""
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
from leconfig import cfg
import PyQt5.QtCore as QtCore
from ui.data import FractureInterface, ClickedControlType
from ui.menus.layers import LayersLayerMenu, LayersInterfaceMenu, LayersFractuceMenu

class Layers(QtWidgets.QWidget):
    """
    GeoMop Layer editor layers panel
    
    pyqtSignals:
        * :py:attr:`viewInterfacesChanged() <viewInterfacesChanged>`
        * :py:attr:`editInterfaceChanged() <editInterfaceChanged>`
    """
    
    viewInterfacesChanged = QtCore.pyqtSignal()
    """Signal is sent when one or more interfaces is set or unset as viwed."""
    editInterfaceChanged = QtCore.pyqtSignal()
    """Signal is sent when edited interface is changed."""

    def __init__(self, parent=None):
        """
        Inicialize window

        Args:
            parent (QWidget): parent window ( empty is None)
        """
        super(Layers, self).__init__(parent)
        self.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        """standart mouse move widget event"""
        if cfg.layers.get_clickable_type(event.pos().x(), event.pos().y()) is not ClickedControlType.none :
            self.setCursor(QtCore.Qt.PointingHandCursor)
        else:
            self.setCursor(QtCore.Qt.ArrowCursor)
        
    def mousePressEvent(self, event):
        type = cfg.layers.get_clickable_type(event.pos().x(), event.pos().y())
        if type is ClickedControlType.none :
            return
        i = cfg.layers.get_clickable_idx(event.pos().x(), event.pos().y(), type) 
        if type is ClickedControlType.view or type is ClickedControlType.view2 or \
            type is ClickedControlType.fracture_view:
            self.change_viewed(i, type)
        elif type is ClickedControlType.edit or type is ClickedControlType.edit2 or \
            type is ClickedControlType.fracture_edit:
            self.change_edited(i, type)
        elif type is ClickedControlType.layer:
            menu = LayersLayerMenu(self, i)
            menu.exec_(self.mapToGlobal(event.pos()))
        elif type is ClickedControlType.interface:
            menu = LayersInterfaceMenu(self, i)
            menu.exec_(self.mapToGlobal(event.pos()))
        elif type is ClickedControlType.fracture:
            menu = LayersFractuceMenu(self, i)
            menu.exec_(self.mapToGlobal(event.pos()))

  #  def keyPressEvent(self, event):

    def _paint_fracture(self, painter, y, x1, x2, dx, interface):
        """Paint layer with fracture name"""
        painter.drawLine(x1-2*dx, y, interface.fracture.rect.left()-dx, y)
        painter.drawText(interface.fracture.rect.bottomLeft(), interface.fracture.name)
        painter.drawLine(interface.fracture.rect.right()+dx, y, x2-2*dx, y)
        
    def _paint_checkbox(self, painter, rect, value):
        """Paint view checkbox"""
        painter.drawRect(rect)        
        if value:
            painter.drawLine(rect.left(), rect.top()+rect.height()*2/3,rect.left()+rect.width()/3)
            painter.drawLine(rect.left()+rect.width()/3, rect.right(), rect.top()+rect.height()/3)

    def _paint_radiobutton(self, painter, rect, value, x2):
        """Paint edit radio button width line to x2"""
        painter.drawEllipse(rect)
        line_y =  rect.top()+rect.height()/2
        painter.drawLine(rect.right(), line_y, x2, line_y)
        if value:
            d=1+rect.width()/4
            rect2 = QtCore.QRectF(rect.left()+d,  rect.top()+d, rect.width()-2*d, rect.height()-2*d)
            painter.drawEllipse(rect2)

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
            if d.interfaces[i].view_rect1 is not None:
                self._paint_checkbox( painter, d.interfaces[i].view_rect1, d.interfaces[i].viewed1)
            if d.interfaces[i].view_rect2 is not None:
                self._paint_checkbox(painter, d.interfaces[i].view_rect2, d.interfaces[i].viewed2)
            if d.interfaces[i].edit_rect1 is not None:
                self._paint_radiobutton(painter, d.interfaces[i].edit_rect1, d.interfaces[i].edited1, d.x_label-2*d.__dx__)
            if d.interfaces[i].edit_rect2 is not None:
                self._paint_radiobutton(painter, d.interfaces[i].edit_rect2, d.interfaces[i].edited2, d.x_label-2*d.__dx__)
            if d.interfaces[i].fracture is not None:
                if d.interfaces[i].fracture.view_rect is not None:
                    self._paint_checkbox(painter, d.interfaces[i].fracture.view_rect, d.interfaces[i].fracture.viewed)
                if d.interfaces[i].fracture.edit_rect is not None:
                    self._paint_radiobutton(painter, d.interfaces[i].fracture.edit_rect, d.interfaces[i].fracture.editedd.x_label-2*d.__dx__)                
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
            
    # data functions    
    def change_viewed(self, i, type):
        """Change viewed interface"""
        pass
        
    def change_edited(self, i, type):
        """Changeedited interface"""
        pass
    
    def add_interface(self, i):
        """Split layer by new interface"""
        pass

    def rename_layer(self, i):
        """Rename layer"""
        pass

    def remove_layer(self, i):
        """Remove layer and add shadow block instead"""
        pass
        
    def add_fracture(self, i):
        """Add fracture to interface"""
        pass
        
    def change_interface_type(self, i):
        """Change interface type"""
        pass
        
    def set_interface_depth(self, i):
        """Set interface depth"""
        pass
        
    def remove_interface(self, i):
        """Remove interface"""
        pass
        
    def remove_fracture(self, i):
        """Remove fracture from interface"""
        pass
        
    def rename_fracture(self, i):
        """Rename fracture"""
        pass
