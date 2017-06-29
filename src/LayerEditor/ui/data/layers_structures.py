import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
from enum import IntEnum

class Layer():
    """One layer in panel"""
    
    def __init__(self, name):
        self.name = name
        """Layer name"""
        self.rect = QtCore.QRectF(0, 0, 0, 0)
        """Clicable name area"""
        self.y = 0
        """Middle coordinate"""


class FractureInterface(IntEnum):
    """Fracture interface type"""
    none = 0
    bottom = 1
    top = 2
    own = 3
       
class Fracture():
    """One fracture in panel"""
    
    def __init__(self, name, type, fracture_diagram_id):
        self.name = name
        """Fracture name"""
        self.type = type
        """fracture Interface type"""
        self.rect = QtCore.QRectF(0, 0, 0, 0)
        """Clicable name area"""
        self.y = 0
        """Middle coordinate"""
        self.fracture_diagram_id = fracture_diagram_id
        """Fracture param set id"""
        self.view_rect = None
        """Clicable view check box area (Only or own fracture interface type)"""
        self.edit_rect = None
        """Clicable edit check box area (Only or own fracture interface type)"""

class Interface():
    """One interface in panel. Diagram 1 is top and 2 is bottom. If diagram 2
    is None"""

    def __init__(self, depth, fracture_name=None, diagram_id1=None, diagram_id2=None, fracture_diagram_id=None):
        self.depth = depth
        """String depth description"""
        self.fracture = None
        """Fracture object or None if fracture is not on interface"""
        if fracture_name is not None:
            if fracture_diagram_id is not None:
                if fracture_diagram_id==diagram_id1:
                    self.fracture = Fracture( fracture_name, FractureInterface.top, fracture_diagram_id)
                elif fracture_diagram_id==diagram_id2:
                    self.fracture = Fracture( fracture_name, FractureInterface.bottom, fracture_diagram_id)
                else:
                    self.fracture = Fracture( fracture_name, FractureInterface.own, fracture_diagram_id)
            else: 
                self.fracture = Fracture(fracture_name, FractureInterface.none)
        """Fracture object or None if fracture is not on interface"""
        self.diagram_id1 = diagram_id1
        """First diagram id (top). None if interface is interpolated"""
        self.diagram_id2 = diagram_id2
        """Second diagram id (bottom). None if interface has not two independent Note Sets"""
        self.edited1 = False
        """is first diagram edited (grafic control is set)"""
        self.viewed1 = False
        """is second  diagram viwed (grafic control is set)"""
        self.edited2 = False
        """is first diagram edited (grafic control is set)"""
        self.viewed2 = False
        """is second  diagram viwed (grafic control is set)"""
        self.rect = QtCore.QRectF(0, 0, 0, 0)
        """Clicable name area"""
        self.y_top = None
        """Top line coordinate"""
        self.y = 0
        """Middle coordinate"""
        self.y_bottom = None
        """Bottom line coordinate"""        
        self.view_rect1 = None
        """Clicable view check box area"""
        self.edit_rect1 = None
        """Clicable edit check box area"""
        self.view_rect2 = None
        """Clicable view check box area"""
        self.edit_rect2 = None
        """Clicable edit check box area"""

class Layers():
    """Layers data"""
    
    __x_view__ = 10
    __x_edit__ = 30
    __dx__ = 10
    __dx_controls__ = 10
    __dy_row__ = 5
    """Pinted metrict"""
    
    @property
    def x_ilabel(self):
        """depth label x left coordinate"""
        return self.x_label +self.__dx__*3+self.x_label_width
        
    @property
    def x_label(self):
        """layer label x left coordinate"""
        return self.__dx__*4+self.__dx_controls__*2 +self.__dx__*3
        
    @property
    def x_view(self):
        """view button x left coordinate"""
        return self.__dx__
    
    @property
    def x_edit(self):
        """edit button x left coordinate"""
        return self.__dx__*4+self.__dx_controls__
    
    
    def __init__(self):
        self.font = QtGui.QFont("times", 12)
        """Layer diagram font"""
        self.layers = []
        """List of layers"""
        self.interfaces = []
        """List of interfaces"""
        self.x_label_width = 0
        """Coordinate of the longest name end"""
        self.y_font = 0
        """Font height"""        
        
    def add_interface(self, depth, fracture_name=None, diagram_id1=None, diagram_id2=None, fracture_id=None):
        """add new interface"""
        self.interfaces.append(Interface(depth, fracture_name, diagram_id1, diagram_id2, fracture_id))
        return len(self.interfaces)-1
        
    def add_layer(self, name):
        """add new layer"""
        self.layers.append(Layer(name))
        return len(self.layers)-1
        
    def compute_composition(self):
        """Compute coordinates for layers elements"""
        fm = QtGui.QFontMetrics(self.font)
        fontHeight = fm.height()
        self.y_font = fontHeight
        y_pos = fontHeight*1.5+self.__dy_row__ # after label
        for i in range(0, len(self.interfaces)):
            #interface
            if self.interfaces[i].diagram_id2 is None:
                # interpolated
                self.interfaces[i].y_top = None
                self.interfaces[i].y_bottom = None
                if self.interfaces[i].fracture is None: 
                    #without fracture
                    self.interfaces[i].y = y_pos                    
                else:
                    width = fm.width(self.interfaces[i].fracture.name)
                    if  width>self.x_label_width:
                        self.x_label_width = width
                    self.interfaces[i].y = (fontHeight+self.__dy_row__)/2+y_pos 
                    #fracture                   
                    self.interfaces[i].fracture.rect = QtCore.QRectF(
                        self.x_label-self.__dx__/2, self.__dy_row__/2+y_pos, width+self.__dx__, fontHeight) 
                    self.interfaces[i].fracture.view_rect = None
                    self.interfaces[i].fracture.edit_rect = None
                    y_pos += fontHeight+self.__dy_row__
            else:
                # given
                if self.interfaces[i].fracture is None:   
                    #without fracture
                    self.interfaces[i].y_top = y_pos
                    self.interfaces[i].y = y_pos+self.__dy_row__                    
                    self.interfaces[i].y_bottom = 2*self.__dy_row__
                    y_pos += 3*self.__dy_row__                    
                else:
                    width = fm.width(self.interfaces[i].fracture.name)
                    if  width>self.x_label_width:
                        self.x_label_width = width
                    if self.interfaces[i].fracture.type==FractureInterface.top:
                        self.interfaces[i].y_top = (fontHeight+self.__dy_row__)/2+y_pos
                        self.interfaces[i].y = fontHeight+ 2*self.__dy_row__+y_pos
                        self.interfaces[i].y_bottom = fontHeight+3*self.__dy_row__+y_pos
                        #fracture
                        self.interfaces[i].fracture.rect = QtCore.QRectF(
                            self.x_label-self.__dx__/2, self.__dy_row__/2+y_pos, width+self.__dx__, fontHeight) 
                        self.interfaces[i].fracture.view_rect = None
                        self.interfaces[i].fracture.edit_rect = None
                    elif self.interfaces[i].fracture.type==FractureInterface.own:
                        x_mid = (fontHeight+self.__dy_row__)/2+y_pos+self.__dy_row__
                        self.interfaces[i].y_top = y_pos
                        self.interfaces[i].y = x_mid
                        self.interfaces[i].y_bottom = fontHeight+3*self.__dy_row__+y_pos
                        #fracture
                        self.interfaces[i].fracture.rect = QtCore.QRectF(
                            self.x_label-self.__dx__/2, 3*self.__dy_row__/2+y_pos, width+self.__dx__, fontHeight) 
                        self.interfaces[i].fracture.view_rect = QtCore.QRectF(
                            self.x_view, x_mid-self.__dx_controls__/2, self.__dx_controls__, self.__dx_controls__)
                        self.interfaces[i].fracture.edit_rect = QtCore.QRectF(
                            self.x_edit, x_mid-self.__dx_controls__/2, self.__dx_controls__, self.__dx_controls__)
                    else:
                        self.interfaces[i].y_top = y_pos
                        self.interfaces[i].y = y_pos+self.__dy_row__                    
                        self.interfaces[i].y_bottom = (fontHeight+self.__dy_row__)/2+y_pos+2*self.__dy_row__ 
                        #fracture
                        self.interfaces[i].fracture.rect = QtCore.QRectF(
                            self.x_label-self.__dx__/2, 5*self.__dy_row__/2+y_pos, width+self.__dx__, fontHeight) 
                        self.interfaces[i].fracture.view_rect = None
                        self.interfaces[i].fracture.edit_rect = None                       
                    y_pos += fontHeight+4*self.__dy_row__
            #layers
            if i<len(self.layers):
                width = fm.width(self.layers[i].name)
                if  width>self.x_label_width:
                    self.x_label_width = width
                self.layers[i].y =  y_pos+self.__dy_row__
                self.layers[i].rect = QtCore.QRectF(
                    self.x_label-self.__dx__/2, self.__dy_row__/2+y_pos, width+self.__dx__, fontHeight)
                y_pos += fontHeight+self.__dy_row__
            
            # interface label
            for i in range(0, len(self.interfaces)):
                width = fm.width(self.interfaces[i].depth)
                self.interfaces[i].y
                self.interfaces[i].rect = QtCore.QRectF(
                    self.x_ilabel-self.__dx__/2, self.interfaces[i].y - fontHeight/2, width+self.__dx__, fontHeight)
