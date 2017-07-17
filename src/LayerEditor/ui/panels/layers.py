"""CanvasWidget file"""
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
from leconfig import cfg
import PyQt5.QtCore as QtCore
from ui.data import FractureInterface, ClickedControlType, ChangeInterfaceActions, LayerSplitType
from ui.menus.layers import LayersLayerMenu, LayersInterfaceMenu, LayersFractuceMenu
from ui.dialogs.layers import AppendLayerDlg, SetNameDlg, SetDepthDlg, SplitLayerDlg, AddFractureDlg, ReportOperationsDlg

class Layers(QtWidgets.QWidget):
    """
    GeoMop Layer editor layers panel
    
    pyqtSignals:
        * :py:attr:`viewInterfacesChanged(int) <viewInterfacesChanged>`
        * :py:attr:`editInterfaceChanged(int) <editInterfaceChanged>`
    """
    
    viewInterfacesChanged = QtCore.pyqtSignal(int)
    """Signal is sent when one or more interfaces is set or unset as viwed.
    
    :param int idx: changed diagram index"""
    editInterfaceChanged = QtCore.pyqtSignal(int)
    """Signal is sent when edited interface is changed.
    
    :param int idx: new edited diagram index"""

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

    def _paint_fracture(self, painter, y, x1, x2, dx, interface, font_dist):
        """Paint layer with fracture name"""
        painter.drawLine(x1-2*dx, y, interface.fracture.rect.left()-dx, y)
        old_pen = painter.pen()
        pen = QtGui.QPen(QtGui.QColor("#802020"))
        painter.setPen(pen)
        painter.drawText(interface.fracture.rect.left(), interface.fracture.rect.bottom()-font_dist, 
            interface.fracture.name)
        painter.setPen(old_pen)
        painter.drawLine(interface.fracture.rect.right()+dx, y, x2-2*dx, y)
        
    def _paint_checkbox(self, painter, rect, value):
        """Paint view checkbox"""
        painter.drawRect(rect)        
        if value:
            painter.drawLine(rect.left()+1, rect.top()+rect.height()*2/3-1,rect.left()+rect.width()/3, rect.bottom()-1)
            painter.drawLine(rect.left()+rect.width()/3+1, rect.bottom()-1, rect.right()-1, rect.top()+rect.height()/3)

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
                    self._paint_fracture(painter, d.interfaces[i].y, d.x_label, 
                        d.x_ilabel, d.__dx__,d.interfaces[i], d.y_font/4)               
            else:
                if d.interfaces[i].fracture is None or d.interfaces[i].fracture.type != FractureInterface.top :
                    painter.drawLine(d.x_label-2*d.__dx__, d.interfaces[i].y_top, d.x_ilabel-2*d.__dx__, d.interfaces[i].y_top)
                else:    
                    self._paint_fracture(painter, d.interfaces[i].y_top, d.x_label, 
                        d.x_ilabel, d.__dx__,d.interfaces[i], d.y_font/4)
                painter.drawLine(d.x_ilabel-2*d.__dx__, d.interfaces[i].y_top, d.x_ilabel-d.__dx__, d.interfaces[i].y)
                if d.interfaces[i].fracture is not None and d.interfaces[i].fracture.type == FractureInterface.own :
                    self._paint_fracture(painter, d.interfaces[i].y, d.x_label, 
                        d.x_ilabel+d.__dx__, d.__dx__,d.interfaces[i], d.y_font/4)
                painter.drawLine(d.x_ilabel-d.__dx__, d.interfaces[i].y, d.x_ilabel-2*d.__dx__, d.interfaces[i].y_bottom)
                if d.interfaces[i].fracture is None or d.interfaces[i].fracture.type != FractureInterface.bottom :
                    painter.drawLine(d.x_label-2*d.__dx__, d.interfaces[i].y_bottom, d.x_ilabel-2*d.__dx__, d.interfaces[i].y_bottom)
                else:    
                    self._paint_fracture(painter, d.interfaces[i].y_bottom, d.x_label,
                        d.x_ilabel, d.__dx__,d.interfaces[i], d.y_font/4)                            
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
                    self._paint_radiobutton(painter, d.interfaces[i].fracture.edit_rect, 
                        d.interfaces[i].fracture.edited, d.x_label-2*d.__dx__)                
            painter.drawText(d.interfaces[i].rect.left(), d.interfaces[i].rect.bottom()-d.y_font/4, 
                d.interfaces[i].str_depth)        
            #layers
            if i<len(d.layers):
                painter.drawText(d.layers[i].rect.left(), d.layers[i].rect.bottom()-d.y_font/4
                    , d.layers[i].name)
                if i+1<len(d.interfaces):
                    top = d.interfaces[i].y
                    bottom = d.interfaces[i+1].y
                    if d.interfaces[i].y_bottom is not None:
                        top = d.interfaces[i].y_bottom
                    if d.interfaces[i+1].y_top is not None:
                        bottom = d.interfaces[i+1].y_top
                    painter.drawLine(d.x_label-2*d.__dx__, top, d.x_label-2*d.__dx__, bottom)
            
    # data functions

    def append_layer(self):
        """Append layer to the end"""
        dlg = AppendLayerDlg(cfg.layers.interfaces[-1].depth, cfg.main_window)
        ret = dlg.exec_()
        if ret==QtWidgets.QDialog.Accepted:
            name = dlg.layer_name.text()
            depth = dlg.depth.text()
            cfg.layers.append_layer(name, depth)
            cfg.layers.compute_composition()
            self.update()
    
    def change_viewed(self, i, type):
        """Change viewed interface"""
        fracture = False
        second = False        
        if type is ClickedControlType.fracture_view:
            fracture = True
        elif type is ClickedControlType.view2:
            second = True
        else:
            assert(type is ClickedControlType.view)
        cfg.layers.set_viewed_interface(i, second, fracture)
        diagram_idx =  cfg.layers.get_diagram_idx(i, second, fracture)
        self.update()
        self.viewInterfacesChanged.emit(diagram_idx)
        
    def change_edited(self, i, type):
        """Change edited interface"""
        fracture = False
        second = False        
        if type is ClickedControlType.fracture_edit:
            fracture = True
        elif type is ClickedControlType.edit2:
            second = True
        else:
            assert(type is ClickedControlType.edit)
        cfg.layers.set_edited_interface(i, second, fracture)
        diagram_idx =  cfg.layers.get_diagram_idx(i, second, fracture)
        self.update()
        self. editInterfaceChanged.emit(diagram_idx)
    
    def add_interface(self, i):
        """Split layer by new interface"""
        min = cfg.layers.interfaces[i].depth
        max = None
        if i<len(cfg.layers.interfaces)-1:
            max = cfg.layers.interfaces[i+1].depth
            
        dlg = SplitLayerDlg(min, max, cfg.main_window)
        ret = dlg.exec_()
        if ret==QtWidgets.QDialog.Accepted:
            name = dlg.layer_name.text()
            depth = dlg.depth.text()
            split_type = dlg.split_type.currentData()
            dup = None
            
            if split_type is LayerSplitType.editable or \
                split_type is LayerSplitType.split:
                dup = cfg.layers.get_diagram_dup(i)
                if split_type is LayerSplitType.split:
                    dup.count = 2
                cfg.insert_diagrams_copies(dup)
            cfg.layers.split_layer(i, name, depth, split_type, dup)       
            cfg.layers.compute_composition()
            self.update()

    def rename_layer(self, i):
        """Rename layer"""
        dlg = SetNameDlg(cfg.layers.layers[i].name, "Layer", cfg.main_window)
        ret = dlg.exec_()
        if ret==QtWidgets.QDialog.Accepted:
            name = dlg.name.text()
            cfg.layers.layers[i].name = name
            cfg.layers.compute_composition()
            self.update()

    def remove_layer(self, i):
        """Remove layer and add shadow block instead"""
        pass
        
    def add_fracture(self, i):
        """Add fracture to interface"""
        dlg = AddFractureDlg(cfg.layers.interfaces[i].get_fracture_position(), cfg.main_window)
        ret = dlg.exec_()
        if ret==QtWidgets.QDialog.Accepted:
            name = dlg.fracture_name.text()
            position = None
            dup = None
            if dlg.fracture_position is not None:
                position = dlg.fracture_position.currentData()
            if position is FractureInterface.own:
                dup = cfg.layers.get_diagram_dup(i)
                cfg.insert_diagrams_copies(dup)
            cfg.layers.add_fracture(i, name, position, dup)
            cfg.layers.compute_composition()
            self.update()    
        
    def change_interface_type(self, i, to_type):
        """Change interface type"""
        if type is ChangeInterfaceActions.interpolated or \
            type is ChangeInterfaceActions.bottom_interpolated or \
            type is ChangeInterfaceActions.top_interpolated:
            dlg = ReportOperationsDlg("Change to interpolated", 
                ["One surface will be removed from structure and save as removed"], 
                cfg.main_window)
            ret = dlg.exec_()
            if ret!=QtWidgets.QDialog.Ok:                
                return
        if type is ChangeInterfaceActions.split:
            new_diagrams_count = cfg.layers.split_interface(i)
            if new_diagrams_count>0:
                depth = cfg.layers.interfaces[i].depth
                cfg. insert_diagrams_copies(cfg.layers.get_last_diagram_id(i), new_diagrams_count, depth)
        elif type is ChangeInterfaceActions.interpolated or \
            type is ChangeInterfaceActions.bottom_interpolated or \
            type is ChangeInterfaceActions.top_interpolated:
            diagram = cfg.layers.change_to_interpolated(i,type)
            if diagram is not None:
                cfg.remove_and_save_surface(diagram)
        else: 
            diagram_id = cfg.layers.change_to_editable(i,type)
            depth = cfg.layers.interfaces[i].depth
            cfg. insert_diagrams_copies(diagram_id, 1, depth)
        cfg.layers.compute_composition()
        self.update()
        
    def set_interface_depth(self, i):
        """Set interface depth"""
        min = None
        max = None
        if i>0:
            min = cfg.layers.interfaces[i-1].depth
        if i<len(cfg.layers.interfaces)-1:
            max = cfg.layers.interfaces[i+1].depth

        dlg = SetDepthDlg(cfg.layers.interfaces[i].depth,  cfg.main_window, min, max)
        ret = dlg.exec_()
        if ret==QtWidgets.QDialog.Accepted:
            depth = dlg.depth.text()
            cfg.layers.interfaces[i].set_depth(depth)
            cfg.layers.compute_composition()
            self.update()
        
    def remove_interface(self, i):
        """Remove interface"""
        pass
        
    def remove_block(self, i):
        """Remove all block"""
        pass

    def save_surface(self, i, type):
        """Remove all block"""
        pass

    def load_surface(self, i, type):
        """Remove all block"""
        pass
        
    def remove_fracture(self, i):
        """Remove fracture from interface"""
        if cfg.layers.interfaces[i].fracture.type==FractureInterface.own:
            dlg = ReportOperationsDlg("Remove Fracture", 
                ["One surface will be removed from structure and save as removed"], 
                cfg.main_window)
            ret = dlg.exec_()
            if ret!=QtWidgets.QDialog.Ok:                
                return            
        diagram = cfg.layers.remove_fracture(i)
        if diagram is not None:
            cfg.remove_and_save_surface(diagram)
        cfg.layers.compute_composition()
        self.update()     
        
    def rename_fracture(self, i):
        """Rename fracture"""
        dlg = SetNameDlg(cfg.layers.interfaces[i].fracture.name, "Fracture", cfg.main_window)
        ret = dlg.exec_()
        if ret==QtWidgets.QDialog.Accepted:
            name = dlg.name.text()
            cfg.layers.interfaces[i].fracture.name = name
            cfg.layers.compute_composition()
            self.update()
