import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
from enum import IntEnum

class DupDiagramData():
    """Data for duplicating didram description"""
    def __init__(self, insert_id, copy=True, dup1_id=None, dup2_id=None):
        self.insert_id = insert_id
        """Where will be diagram inserted"""
        self.copy = copy
        """make only copy"""
        self.dup1_id = dup1_id
        """First diagram id for duplicating"""
        self.dup1_id = dup1_id
        """Second diagram id for duplicating"""
        self.count = 1
        """Amout of new diagrams"""
        self.idx = None
        """Interface where is created new surface"""

class Layer():
    """One layer in panel"""
    
    def __init__(self, name, shadow=False):
        self.shadow = shadow
        """Laier is shadow"""
        self.name = name
        """Layer name, if name is """
        self.shadow = shadow
        """Laier is shadow"""
        if shadow:
            name = "shadow"
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
    
class LayerSplitType(IntEnum):
    """Fracture interface type"""
    interpolated = 0
    editable = 1
    split = 2
    
class ChangeInterfaceActions(IntEnum):
    """Interface possible actions"""
    interpolated = 0
    top_interpolated = 1
    bottom_interpolated = 2
    editable = 3
    top_editable = 4
    bottom_editable = 5
    split = 6

class ClickedControlType(IntEnum):
    """Type of control that is clicked"""
    none = 0
    view = 1
    edit = 2
    interface = 3
    fracture = 4
    layer = 5
    view2 = 6
    edit2 = 7
    fracture_view = 8
    fracture_edit = 9
    
class Fracture():
    """One fracture in panel"""
    
    def __init__(self, name, type=FractureInterface.none, fracture_diagram_id=None):
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
        self.viewed = False
        """fracture diagram is viwed"""
        self.edited = False
        """fracture diagram is  edited"""

class Interface():
    """One interface in panel. Diagram 1 is top and 2 is bottom. If diagram 2
    is None"""

    def __init__(self, depth, splited, fracture_name=None, diagram_id1=None, diagram_id2=None, fracture_diagram_id=None):
        self.depth = 0.0
        """Float depth description"""
        try:
            self.depth = float(depth)            
        except:
            raise ValueError("Invalid depth type")
        self.splited = splited
        """Interface have two independent surfaces"""
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
        
    @property
    def str_depth(self):
        """Retuen depth in string format"""
        return str(self.depth)
    
    def set_depth(self, depth): 
        """Check and aave depth in right format"""
        try:
            self.depth = float(depth)            
        except:
            raise ValueError("Invalid depth type")
            
    def get_fracture_position(self):
        """Return dictionry with string description of fracture possitions -> FractureInterface enum
        if is only one possibility, return None"""
        if not self.splited:
            return None
        return {"Top surface":FractureInterface.top, 
            "Own surface":FractureInterface.own, 
            "Bottom surface":FractureInterface.bottom}

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
        return self.__dx__*5+self.__dx_controls__*2 +self.__dx__*3
        
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
        """Coordinate of the longest layer name end"""
        self.x_ilabel_width = 0
        """Coordinate of the longest interface name end"""
        self.y_font = 0
        """Font height"""        
        
    def add_interface(self, depth, splited, fracture_name=None, diagram_id1=None, diagram_id2=None, fracture_id=None):
        """add new interface"""
        self.interfaces.append(Interface(depth, splited, fracture_name, diagram_id1, diagram_id2, fracture_id))
        return len(self.interfaces)-1
        
    def add_layer(self, name):
        """add new layer"""
        self.layers.append(Layer(name))
        return len(self.layers)-1
        
    def append_layer(self, name, depth):
        """Append layer to the end"""
        self.add_layer(name)
        self.add_interface(depth, False)    
       
    def add_fracture(self, idx, name, position, dup):
        """add fracture to interface"""
        if self.interfaces[idx].fracture is not None:
            raise Exception("Interface {0} has already fracture.".format(str(idx)))
        if position is None:
            self.interfaces[idx].fracture = Fracture(name)
        else:
            if position is FractureInterface.own:
                self.interfaces[idx].diagram_id2 += 1    
                self._move_diagram_idx(idx, 1)                
            self.interfaces[idx].fracture = Fracture(name, position, dup.insert_id-1)
        
    def get_diagram_dup(self, idx):
        """Return first idx for division and if is possible division make
        """
        dup = None
        id = None
        id_pred = None
        id2 = None
        id_po = None
        for i in range(idx, -1, -1):
            if self.interfaces[i].diagram_id2 is not None:
                if id is None:
                    id = self.interfaces[i].diagram_id2
                elif id_pred is None:
                    id_pred = self.interfaces[i].diagram_id2
            if self.interfaces[i].splited:
                break
            if self.interfaces[i].diagram_id1 is not None:
                if id is None:
                    id = self.interfaces[i].diagram_id1
                elif id_pred is None:
                    id_pred = self.interfaces[i].diagram_id1
                else:
                    break
        for i in range(idx+1, len(self.interfaces)):
            if self.interfaces[i].diagram_id1 is not None:
                if id2 is None:
                    id2 = self.interfaces[i].diagram_id1
                elif id_po is None:
                    id_po = self.interfaces[i].diagram_id1
                else:
                    break
            if self.interfaces[i].splited:
                break  
        if id is not None and id2 is not None:
            dup = DupDiagramData(id+1, False, id, id2)
        elif id2 is None and id is not None and id_pred is None:
            dup = DupDiagramData(id+1)              
        elif id2 is not None and id is None and id_po is None:
            dup = DupDiagramData(id2)              
        elif id2 is None and id is not None and id_pred is not None:
            dup =  DupDiagramData(id+1, False, id_pred, id)              
        elif id2 is not None and id is None and id_po is not None:
            dup =  DupDiagramData(id2, False, id2, id_po)
        if dup is not None:
            dup.idx = idx
            return dup
        raise Exception("Block with interface {0} has not diagram.".format(str(idx)))
      
    def _move_diagram_idx(self, idx, incr):
        """Increase diagram indexes increment in interfaces bigger than idx"""
        for i in range(idx+1, len( self.interfaces)):
            if self.interfaces[i].diagram_id1 is not None:
                self.interfaces[i].diagram_id1 += incr
            if self.interfaces[i].diagram_id2 is not None:
                self.interfaces[i].diagram_id2 += incr
            if self.interfaces[i].fracture is not None and \
                self.interfaces[i].fracture.fracture_diagram_id is not None:
                self.interfaces[i].fracture.fracture_diagram_id += incr
                
    def _count_of_editable(self, idx):
        """Return count of editable surfaces in block"""
        count = 0
        i = idx
        while i<len(self.interfaces):
            if self.interfaces[idx].diagram_id1 is not None:
                    count += 1
            if self.interfaces[idx].splited:                
                break
            i += 1
        i = idx
        while i>=0:
            if self.interfaces[idx].splited:
                if self.interfaces[idx].diagram_id2 is not None:
                    count += 1
                break                
            if self.interfaces[idx].diagram_id1 is not None:
                count += 1            
            i -= 1
        return count
                
    def get_change_interface_actions(self, idx):
        """Get list of interface possible actions"""
        ret = []
        count = self._count_of_editable(idx)
        if self.interfaces[idx].splited:
            count2 = self._count_of_editable(idx+1)
            if self.interfaces[idx].diagram_id1 is not None and count>1:
                ret.append(ChangeInterfaceActions.top_interpolated)
            if self.interfaces[idx].diagram_id1 is None:
                ret.append(ChangeInterfaceActions.top_editable)           
            if self.interfaces[idx].diagram_id2 is not None and count2>1:
                ret.append(ChangeInterfaceActions.bottom_interpolated)
            if self.interfaces[idx].diagram_id2 is None:
                ret.append(ChangeInterfaceActions.bottom_editable)           
        else:
            if self.interfaces[idx].diagram_id1 is not None and count>1:
                ret.append(ChangeInterfaceActions.interpolated)
            if self.interfaces[idx].diagram_id1 is None:
                ret.append(ChangeInterfaceActions.editable)
            if idx>0 and idx<len(self.interfaces)-1:
                ret.append(ChangeInterfaceActions.split)
        return ret
                
    def remove_fracture(self, idx):
        """Remove fracture from idx interface. If fracture has surface,
        return surface idx end move all surfaces idx else return None"""
        ret = None
        if self.interfaces[idx].fracture.type==FractureInterface.own:
            ret = self.interfaces[idx].fracture.fracture_diagram_id
            if self.interfaces[idx].diagram_id2 is not None:
                self.interfaces[idx].diagram_id2 -= 1
            self._move_diagram_idx(idx, -1)
        self.interfaces[idx].fracture = None
        return ret
        
    def change_to_interpolated(self, idx, type):
        """Change interface type to interpolated"""
        diagram = None
        if type is ChangeInterfaceActions.interpolated:
            diagram = self.interfaces[idx].diagram_id1
            self.interfaces[idx].diagram_id1 = None
            self._move_diagram_idx(idx, -1)
        elif type is ChangeInterfaceActions.bottom_interpolated:
            diagram = self.interfaces[idx].diagram_id1
            self.interfaces[idx].diagram_id1 = None
            if self.interfaces[idx].diagram_id2 is not None:
                self.interfaces[idx].diagram_id2 -= 1
            if self.interfaces[idx].fracture is not None and \
                self.interfaces[idx].fracture.fracture_diagram_id is not None:
                self.interfaces[idx].fracture.fracture_diagram_id -= 1                
            self._move_diagram_idx(idx, -1)
        elif type is ChangeInterfaceActions.top_interpolated:
            diagram = self.interfaces[idx].diagram_id2
            self.interfaces[idx].diagram_id2 = None
            self._move_diagram_idx(idx, -1)
        return diagram
        
    def change_to_editable(self, idx, type, dup):
        """Change interface type to editable"""    
        if type is ChangeInterfaceActions.editable:
            self.interfaces[idx].diagram_id1 = dup.insert_id
            self._move_diagram_idx(idx, 1)
        elif type is ChangeInterfaceActions.bottom_editable:
            self.interfaces[idx].diagram_id2 = dup.insert_id
            self._move_diagram_idx(idx, 1)
        elif type is ChangeInterfaceActions.top_editable:
            self.interfaces[idx].diagram_id1 = dup.insert_id
            self._move_diagram_idx(idx, 1)
 
        
    def split_interface(self, idx):
        """Split interface with and return how many copies of idx diagram 
        should be added insert after idx interface"""
#        self.interfaces[idx].splitted = True
#        if self.interfaces[idx].fracture is not None:
#            self.interfaces[idx].fracture.type = FractureInterface.top
#        last_id = self.get_last_diagram_id(idx)
#        self.interfaces[idx].diagram_id2 = last_id
#        self._move_diagram_idx(idx, 1)
        return 1 
        
    def split_layer(self, idx, name, depth, split_type, dup):
        """Split set layer by interface with split_type type in set depth
        return how many copies of idx diagram  should be added insert
        after idx interface"""
        new_layer = Layer(name)
        if split_type is LayerSplitType.interpolated:
            new_interface = Interface(depth, False)
        elif split_type is LayerSplitType.editable:
            new_interface = Interface(depth, False, None, dup.insert_id)
        elif split_type is LayerSplitType.split:
            new_interface = Interface(depth, True, None, dup.insert_id, dup.insert_id)
        else:
            raise Exception("Invalid split operation in interface {0}".format(str(idx)))
        if dup is not None:
            self._move_diagram_idx(idx, dup.count)
        self.layers.insert(idx+1, new_layer)
        self.interfaces.insert(idx+1, new_interface)        
        
        
    def set_edited_interface(self, idx, second, fracture=False):
        """If interface with set idx is set as edited return False, 
        else change edited interface in data and return True"""
        #check
        if fracture:
            if self.interfaces[idx].fracture is None:
                raise Exception("Invalid interface operation: Interface {0} has not editable fracture".format(str(idx)))
            if self.interfaces[idx].fracture.edit_rect is None:
                raise Exception("Invalid interface operation: Fracture in interface {0} has not editable surface".format(str(idx)))
        elif second:
            if self.interfaces[idx].edit_rect2 is None:
                raise Exception("Invalid interface operation: Interface {0} has not two editable surfaces".format(str(idx)))
        else:
            if self.interfaces[idx].edit_rect1 is None:
                raise Exception("Invalid interface operation: Interface {0} has not editable  surface".format(str(idx)))
        # settings                
        for i in range(0, len(self.interfaces)):
            if i==idx:
                if fracture:
                    if self.interfaces[idx].fracture.edited:
                        return False
                    self.interfaces[i].edited1 = False
                    self.interfaces[i].edited2 = False
                    self.interfaces[idx].fracture.edited = True # fracture existance is checked in the begining of this function
                elif second:
                    if self.interfaces[i].edited2:
                        return False
                    else:
                        self.interfaces[i].edited2 = True
                    self.interfaces[i].edited1 = False
                    if self.interfaces[idx].fracture is not None:
                        self.interfaces[idx].fracture.edited = False
                else:                        
                    if self.interfaces[i].edited1:
                        return False
                    else:
                        self.interfaces[i].edited1 = True
                    self.interfaces[i].edited2 = False
                    if self.interfaces[idx].fracture is not None:
                        self.interfaces[idx].fracture.edited = False
            else:
                self.interfaces[i].edited1 = False
                self.interfaces[i].edited2 = False
                if self.interfaces[idx].fracture is not None:
                    self.interfaces[idx].fracture.edited = False
        return True
        
    def get_diagram_idx(self, idx, second, fracture=False):
        """Get diagram (surface) idx from interface idx or none if 
        interface has not diagram"""
        if fracture:
            if self.interfaces[idx].fracture is None:
                return None
            return self.interfaces[idx].fracture.fracture_diagram_id
        elif second:
            return self.interfaces[idx].diagram_id1
        return self.interfaces[idx].diagram_id2

    def set_viewed_interface(self, idx, second, fracture=False):
        """Invert set viewed value and return its value"""
        #check
        if fracture:
            if self.interfaces[idx].fracture is None:
                raise Exception("Invalid interface operation: Interface {0} has not viewable fracture".format(str(idx)))
            if self.interfaces[idx].fracture.view_rect is None:
                raise Exception("Invalid interface operation: Fracture in interface {0} has not viewable surface".format(str(idx)))
        elif second:
            if self.interfaces[idx].view_rect2 is None:
                raise Exception("Invalid interface operation: Interface {0} has not two viewable surfaces".format(str(idx)))
        else:
            if self.interfaces[idx].view_rect1 is None:
                raise Exception("Invalid interface operation: Interface {0} has not viewable surface".format(str(idx)))
        # settings                
        if fracture:
            self.interfaces[idx].fracture.viewed = not self.interfaces[idx].fracture.viewed
            return self.interfaces[idx].fracture.viewed
        elif second:
            self.interfaces[idx].viewed2 = not self.interfaces[idx].viewed2
            return self.interfaces[idx].viewed2
        self.interfaces[idx].viewed1 = not self.interfaces[idx].viewed1
        return self.interfaces[idx].viewed1
        
    def _compute_controls(self, y):
        """Compute view and edit controls possition"""
        view_rect = QtCore.QRectF(self.x_view, y-self.__dx_controls__/2, self.__dx_controls__, self.__dx_controls__)
        edit_rect = QtCore.QRectF(self.x_edit, y-self.__dx_controls__/2, self.__dx_controls__, self.__dx_controls__)
        return view_rect, edit_rect   
        
    def compute_composition(self):
        """Compute coordinates for layers elements"""
        fm = QtGui.QFontMetrics(self.font)
        fontHeight = fm.height()
        self.y_font = fontHeight
        y_pos = fontHeight*1.5+2*self.__dy_row__ # after label
        for i in range(0, len(self.interfaces)):
            self.interfaces[i].view_rect1 = None
            self.interfaces[i].edit_rect1 = None
            self.interfaces[i].view_rect2 = None
            self.interfaces[i].edit_rect2 = None
            #interface
            if not self.interfaces[i].splited:
                # interpolated
                self.interfaces[i].y_top = None
                self.interfaces[i].y_bottom = None
                if self.interfaces[i].fracture is None: 
                    #without fracture
                    self.interfaces[i].y = y_pos                    
                else:
                    width = fm.width(self.interfaces[i].fracture.name) 
                    if  width+self.__dx__>self.x_label_width:
                        self.x_label_width = width+self.__dx__
                    self.interfaces[i].y = (fontHeight+self.__dy_row__)/2+y_pos 
                    #fracture                   
                    self.interfaces[i].fracture.rect = QtCore.QRectF(
                        self.x_label, self.__dy_row__/2+y_pos, width, fontHeight) 
                    self.interfaces[i].fracture.view_rect = None
                    self.interfaces[i].fracture.edit_rect = None
                    y_pos += fontHeight+self.__dy_row__
                if self.interfaces[i].diagram_id1 is not None:
                    (self.interfaces[i].view_rect1, self.interfaces[i].edit_rect1) = self._compute_controls(self.interfaces[i].y)
            else:
                # two given or interpolated and given blok
                if self.interfaces[i].fracture is None:   
                    #without fracture
                    self.interfaces[i].y_top = y_pos
                    self.interfaces[i].y = y_pos+2*self.__dy_row__                    
                    self.interfaces[i].y_bottom = y_pos+4*self.__dy_row__
                    y_pos += 5*self.__dy_row__                    
                else:
                    width = fm.width(self.interfaces[i].fracture.name)
                    if  width+self.__dx__>self.x_label_width:
                        self.x_label_width = width+self.__dx__
                    if self.interfaces[i].fracture.type==FractureInterface.top:
                        self.interfaces[i].y_top = (fontHeight+self.__dy_row__)/2+y_pos
                        self.interfaces[i].y = fontHeight*3/4+self.__dy_row__*9/4+y_pos
                        self.interfaces[i].y_bottom = fontHeight+3*self.__dy_row__+y_pos
                        #fracture
                        self.interfaces[i].fracture.rect = QtCore.QRectF(
                            self.x_label, self.__dy_row__/2+y_pos, width, fontHeight) 
                        self.interfaces[i].fracture.view_rect = None
                        self.interfaces[i].fracture.edit_rect = None
                    elif self.interfaces[i].fracture.type==FractureInterface.own:
                        y_mid = (fontHeight+self.__dy_row__)/2+y_pos+self.__dy_row__
                        self.interfaces[i].y_top = y_pos
                        self.interfaces[i].y = y_mid
                        self.interfaces[i].y_bottom = fontHeight+3*self.__dy_row__+y_pos
                        #fracture
                        self.interfaces[i].fracture.rect = QtCore.QRectF(
                            self.x_label, 3*self.__dy_row__/2+y_pos, width, fontHeight) 
                            
                        (self.interfaces[i].fracture.view_rect, self.interfaces[i].fracture.edit_rect) = self._compute_controls(y_mid)                        
                    else:
                        self.interfaces[i].y_top = y_pos
                        self.interfaces[i].y = fontHeight/4+self.__dy_row__*5/4+y_pos
                        self.interfaces[i].y_bottom = (fontHeight+self.__dy_row__)/2+y_pos+2*self.__dy_row__ 
                        #fracture
                        self.interfaces[i].fracture.rect = QtCore.QRectF(
                            self.x_label, 5*self.__dy_row__/2+y_pos, width, fontHeight) 
                        self.interfaces[i].fracture.view_rect = None
                        self.interfaces[i].fracture.edit_rect = None                       
                    y_pos += fontHeight+4*self.__dy_row__
                if self.interfaces[i].diagram_id1 is not None:
                    (self.interfaces[i].view_rect1, self.interfaces[i].edit_rect1) = self._compute_controls(self.interfaces[i].y_top)
                if self.interfaces[i].diagram_id2 is not None:
                    (self.interfaces[i].view_rect2, self.interfaces[i].edit_rect2) = self._compute_controls(self.interfaces[i].y_bottom)
            # 
            #layers
            if i<len(self.layers):
                width = fm.width(self.layers[i].name)
                if  width>self.x_label_width:
                    self.x_label_width = width
                self.layers[i].y =  y_pos+self.__dy_row__
                self.layers[i].rect = QtCore.QRectF(
                    self.x_label, self.__dy_row__/2+y_pos, width, fontHeight)
                y_pos += fontHeight+self.__dy_row__
            
            # interface label
            for i in range(0, len(self.interfaces)):
                width = fm.width(self.interfaces[i].str_depth)
                if  width>self.x_ilabel_width:
                        self.x_ilabel_width = width
                self.interfaces[i].y
                self.interfaces[i].rect = QtCore.QRectF(
                    self.x_ilabel, self.interfaces[i].y - fontHeight/2, width, fontHeight)

    def get_clickable_type(self, x, y):
        """Return control type of below point"""
        if x<self.x_view or \
            (x>self.x_view+self. __dx_controls__ and x< self.x_edit) or \
            (x>self.x_edit+self. __dx_controls__ and x< self.x_label) or \
            (x>self.x_label+self.x_label_width and x< self.x_ilabel) or \
            x>self.x_ilabel+self.x_ilabel_width:
            return ClickedControlType.none
        p = QtCore.QPointF(x, y)
        for i in range(0, len(self.interfaces)):
            # interface            
            if self.interfaces[i].rect.contains(p):
                return ClickedControlType.interface
            if self.interfaces[i].view_rect1 is not None:
                if self.interfaces[i].view_rect1.contains(p):
                    return ClickedControlType.view
            if self.interfaces[i].edit_rect1 is not None:
                if self.interfaces[i].edit_rect1.contains(p):
                    return ClickedControlType.edit
            if self.interfaces[i].view_rect2 is not None:
                if self.interfaces[i].view_rect2.contains(p):
                    return ClickedControlType.view2
            if self.interfaces[i].edit_rect2 is not None:
                if self.interfaces[i].edit_rect2.contains(p):
                    return ClickedControlType.edit2
            #fracture
            if self.interfaces[i].fracture is not None:
                if self.interfaces[i].fracture.rect.contains(p):
                    return ClickedControlType.fracture
                if self.interfaces[i].fracture.view_rect is not None:
                    if self.interfaces[i].fracture.view_rect.contains(p):
                        return ClickedControlType.fracture_view
                if self.interfaces[i].fracture.edit_rect is not None:
                    if self.interfaces[i].fracture.edit_rect.contains(p):
                        return ClickedControlType.fracture_edit
            if i<len(self.layers):
                if self.layers[i].rect.contains(p):
                    return ClickedControlType.layer
        return ClickedControlType.none

    def get_clickable_idx(self, x, y, type):
        """Return number of control below point"""
        if type is ClickedControlType.none:
            return None
        p = QtCore.QPointF(x, y)
        for i in range(0, len(self.interfaces)):
            # interface            
            if type is ClickedControlType.interface and self.interfaces[i].rect.contains(p):
                return i
            if type is ClickedControlType.view and self.interfaces[i].view_rect1 is not None:
                if self.interfaces[i].view_rect1.contains(p):
                    return i
            if type is ClickedControlType.edit and self.interfaces[i].edit_rect1 is not None:
                if self.interfaces[i].edit_rect1.contains(p):
                    return i
            if type is ClickedControlType.view2 and self.interfaces[i].view_rect2 is not None:
                if self.interfaces[i].view_rect2.contains(p):
                    return i
            if type is ClickedControlType.edit2 and self.interfaces[i].edit_rect2 is not None:
                if self.interfaces[i].edit_rect2.contains(p):
                    return i
            #fracture
            if self.interfaces[i].fracture is not None:
                if type is ClickedControlType.interface and self.interfaces[i].fracture.rect.contains(p):
                    return i
                if type is ClickedControlType.interface and self.interfaces[i].fracture.view_rect is not None:
                    if self.interfaces[i].fracture.view_rect.contains(p):
                        return i
                if type is ClickedControlType.fracture_edit and self.interfaces[i].fracture.edit_rect is not None:
                    if self.interfaces[i].fracture.edit_rect.contains(p):
                        return i
            if type is ClickedControlType.layer and i<len(self.layers):
                if self.layers[i].rect.contains(p):
                    return i

        return None
