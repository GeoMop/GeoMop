import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
from geometry_files import TopologyType
from enum import IntEnum
import copy

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

    def __init__(self, depth, splited, fracture_name=None, diagram_id1=None, diagram_id2=None, fracture_interface=FractureInterface.none, fracture_diagram_id=None):
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
            self.fracture = Fracture( fracture_name, fracture_interface, fracture_diagram_id)
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
        
    def delete(self):
        """delete all data structure"""
        self.layers = []
        self.interfaces = []
     
    class LayersIterData():
        """Data clas for passing between itarion functions 
        get_first_layer_info and get_next_layer_info. This
        functions is use for layers serialization"""
        def __init__(self):
            self.layer_idx = 0
            """Layer idx"""
            self.is_shadow = False
            """Layer type is shadow"""
            self.block_idx = 0
            """Block idx, use for topology"""
            self.diagram_id1 = None
            """First diagram id"""
            self.stype1 = None
            """First surface type"""
            self.diagram_id2 = None
            """Second diagram id, None for copy block"""
            self.stype2 = None
            """second surface type"""
            self.fracture_before = None
            """Fracture before layer. (With same topology as first diagram)"""
            self.fracture_after = None
            """Fracture after layer. (With same topology as second diagram)"""
            self.fracture_own = None
            """Fracture after layer. (With own topology)"""
            self.end = False
            """Last layer"""
   
    def get_first_layer_info(self):
        """Get information about first layer. All temporary data is 
        save to returned variable. This variable can be pass on get_next_layer_info
        function or used for data serialization.
        return 
        """
        data = self.LayersIterData()
        if self.interfaces[0].diagram_id1 is None:
            i=1
            while self.interfaces[i].diagram_id1 is None:
                i += 1
            data.diagram_id1 = self.interfaces[i].diagram_id1
            data.stype1 = TopologyType.interpolated
            data.diagram_id2 = None
            if i==1:
                data.stype2 = TopologyType.given
            else:
                data.stype2 = TopologyType.interpolated
        else:
            data.diagram_id1 = self.interfaces[0].diagram_id1
            data.stype1 = TopologyType.given
            i=1
            if self.interfaces[1].diagram_id1 is None:
                data.stype2 = TopologyType.interpolated
                while len(self.interfaces)>i and self.interfaces[i].diagram_id1 is None:
                    if self.interfaces[i].splited:                        
                        break
                    i += 1
                if len(self.interfaces)<i and self.interfaces[i].diagram_id1 is not None:
                    data.diagram_id2 = self.interfaces[i].diagram_id1
                else:
                    data.diagram_id2 = None
            else:
                data.diagram_id2 = self.interfaces[1].diagram_id1
                data.stype2 = TopologyType.given
        if self.interfaces[0].fracture:
            data.fracture_before = self.interfaces[0].fracture
        if self.interfaces[1].fracture:
            if self.interfaces[1].fracture.type is FractureInterface.top:
                data.fracture_after = self.interfaces[1].fracture
            elif self.interfaces[1].fracture.type is FractureInterface.own:
                data.fracture_own = self.interfaces[1].fracture 
        return data        
        
    def get_next_layer_info(self, data):
        """Get information about next layer. All temporary data is 
        save to returned variable This variable can be pass on get_next_layer_info
        function or used for data serialization. This function is use for 
        all layers iteration"""
        i = data.layer_idx+1
        data.layer_idx = i
        if len(self.layers)==i:
            data.end = True  
            return data
        if self.layers[i].shadow:
            data.is_shadow = True
        else:
            data.is_shadow = False
            if self.interfaces[i].splited:
                data.block_idx += 1
                if self.interfaces[i].diagram_id2 is None:
                    j=i+1
                    while self.interfaces[j].diagram_id1 is None:
                        j += 1
                    data.diagram_id1 = self.interfaces[j].diagram_id1
                    data.stype1 = TopologyType.interpolated
                    data.diagram_id2 = None
                    if i==1:
                        data.stype2 = TopologyType.given
                    else:
                        data.stype2 = TopologyType.interpolated
                else:
                    data.diagram_id1 = self.interfaces[i].diagram_id2
                    data.stype1 = TopologyType.given
                    j=i
                    if self.interfaces[j].diagram_id1 is None:
                        data.stype2 = TopologyType.interpolated
                        while self.interfaces[j].diagram_id1 is None:
                            if self.interfaces[j].splited:                        
                                data.diagram_id2 = None
                                break
                            j += 1
                        if self.interfaces[j].diagram_id1 is not None:
                            data.diagram_id2 = self.interfaces[j].diagram_id1
                    else:
                        data.diagram_id2 = self.interfaces[i+1].diagram_id1
                        data.stype2 = TopologyType.given
            else:
                if self.interfaces[i].diagram_id1 is not None:                    
                    data.stype1 = TopologyType.given
                else:
                    data.stype1 = TopologyType.interpolated
                j = i+1
                next = True
                while self.interfaces[j].diagram_id1 is None:
                    if self.interfaces[j].splited:                        
                        next = False
                        data.stype2 = TopologyType.interpolated
                        break
                    j += 1
                if next:
                    if self.interfaces[i].diagram_id1 is not None:
                        data.diagram_id1 = self.interfaces[i].diagram_id1
                        data.diagram_id2 = self.interfaces[i].diagram_id2
                    if j==i+1:
                        data.stype2 = TopologyType.given
                    else:
                        data.stype2 = TopologyType.interpolated
        data.fracture_before = None
        data.fracture_after = None
        data.fracture_own = None
        if self.interfaces[i].fracture:
            if self.interfaces[i].splited: 
                if self.interfaces[i].fracture.type is FractureInterface.bottom:
                    data.fracture_before = self.interfaces[i].fracture
            else:
                data.fracture_before = self.interfaces[i].fracture
        if self.interfaces[i+1].fracture:
            if self.interfaces[i+1].fracture.type is FractureInterface.top:
                data.fracture_after = self.interfaces[i+1].fracture
            elif self.interfaces[i+1].fracture.type is FractureInterface.own:
                data.fracture_own = self.interfaces[i+1].fracture             
        return data
        
    def add_interface(self, depth, splited, fracture_name=None, diagram_id1=None, diagram_id2=None,fracture_interface=FractureInterface.none, fracture_id=None):
        """add new interface"""
        self.interfaces.append(Interface(depth, splited, fracture_name, diagram_id1, diagram_id2,fracture_interface, fracture_id))
        return len(self.interfaces)-1
        
    def add_layer(self, name, shadow=False):
        """add new layer"""
        self.layers.append(Layer(name, shadow))
        return len(self.layers)-1
        
    def append_layer(self, name, depth):
        """Append layer to the end"""
        self.add_layer(name)
        self.add_interface(depth, False)
        
    def prepend_layer(self, name, depth):
        """Prepend layer to the start"""
        self.layers.insert(0, Layer(name))
        self.interfaces.insert(0, Interface(depth, False)) 
 
    def add_layer_to_shadow(self, idx, name, depth, dup):
        """Append new layer to shadow block, return True if 
        shadow block is replaces"""
        self.interfaces[idx].diagram_id2 = dup.insert_id
        self._move_diagram_idx(idx+1, 1)  
        if float(depth)==self.interfaces[idx+1].depth:
            self.layers[idx].shadow=False
            self.layers[idx].name=name
            return True
        else:
            self.layers.insert(idx, Layer(name))
            self.interfaces.insert(idx+1, Interface(depth, True))
        return False
       
       
    def add_fracture(self, idx, name, position, dup):
        """add fracture to interface
        
        Variable dup is returned by get_diagram_dup and new diagrams was added
        outside this function"""
        if self.interfaces[idx].fracture is not None:
            raise Exception("Interface {0} has already fracture.".format(str(idx)))
        if position is None:
            self.interfaces[idx].fracture = Fracture(name)
        else:
            if position is FractureInterface.own:
                self.interfaces[idx].diagram_id2 += 1    
                self._move_diagram_idx(idx, 1)                
            self.interfaces[idx].fracture = Fracture(name, position, dup.insert_id-1)
        
    def get_diagram_dup_before(self, idx):
        """Return first idx for division and if is possible division make
        """
        dup = None
        id = None
        id_pred = None
        for i in range(idx, -1, -1):
            if i<idx:
                if self.interfaces[i].diagram_id2 is not None:
                    if id is None:
                        id = self.interfaces[i].diagram_id2
                    elif id_pred is None:
                        id_pred = self.interfaces[i].diagram_id2
                if self.interfaces[i].splited:
                    break
            if self.interfaces[i].diagram_id1 is not None:
                if i==idx:
                    id = self.interfaces[i].diagram_id1
                    # copy is maked
                    break
                if id is None:
                    id = self.interfaces[i].diagram_id1
                elif id_pred is None:
                    id_pred = self.interfaces[i].diagram_id1
                else:
                    break
        if id is not None and id_pred is None:
            dup = DupDiagramData(id+1)              
        else:
            dup =  DupDiagramData(id+1, False, id_pred, id)              
        if dup is not None:
            dup.idx = idx
            return dup
        raise Exception("Block with interface {0} has not diagram.".format(str(idx)))
        
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
            if self.interfaces[i].diagram_id1 is not None:
                    count += 1
            if self.interfaces[i].splited:                
                break
            i += 1
        i = idx-1
        while i>=0:
            if self.interfaces[i].splited:
                if self.interfaces[i].diagram_id2 is not None:
                    count += 1
                break                
            if self.interfaces[i].diagram_id1 is not None:
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
        
    def is_layer_removable(self, idx):
        """Return if layer can be removed"""
        if idx==0:
           return len(self.layers)>1 and self.interfaces[1].splited            
        if idx==len(self.layers)-1 or self.interfaces[idx+1].splited:
            if self.interfaces[idx].splited or self.interfaces[idx+1].diagram_id1 is None:
                return True
            return self._count_of_editable(idx+1)>1               
        return False
        
    def is_interface_removable(self, idx):
        """Return if layer can be removed"""
        if self.interfaces[idx].splited:
            return False
        if idx==0 or idx==len(self.interfaces)-1:
            return False
        if self.interfaces[idx].diagram_id1 is None:
            return True
        return self._count_of_editable(idx+1)>1               
        
    def is_block_removable(self, idx):
        """Return if layer can be removed"""
        for interface in self.interfaces:
            if interface.splited:
                return True
        return False        
        
    def _add_shadow(self, idx):
        """Transform idx layer to shadow block"""
        if idx == len(self.layers)-1:
            del self.interfaces[-1]
            del self.layers[-1]            
            if idx>0 and self.layers[idx-1].shadow:
                del self.interfaces[-1]
                del self.layers[-1]
                self.interfaces[idx-1].splited = False
                self.interfaces[idx-1].diagram_id2 = None                
            else:                
                if self.interfaces[idx].fracture is not None:
                    if self.interfaces[idx].fracture.type is FractureInterface.bottom:
                        self.interfaces[idx].fracture = None
                    else:
                        self.interfaces[idx].fracture.type = FractureInterface.none
                self.interfaces[idx].splited = False
                self.interfaces[idx].diagram_id2 = None
            return
        if idx == 0:
            del self.interfaces[0]
            del self.layers[0] 
            self.interfaces[idx].splited = False
            if self.interfaces[0].fracture is not None:
                if self.interfaces[0].fracture.type is FractureInterface.top:
                    self.interfaces[0].fracture = None
                else:
                    self.interfaces[0].fracture.type = FractureInterface.none
            return
        if idx>0 and self.layers[idx-1].shadow and self.layers[idx-1].shadow:
            del self.interfaces[idx+1]
            del self.layers[idx+1]
            del self.interfaces[idx]
            del self.layers[idx]            
            return
        if idx>0 and self.layers[idx-1].shadow:
            del self.interfaces[idx]
            del self.layers[idx]
            self.interfaces[idx].splited = True
            self.interfaces[idx].diagram_id2 = None
            return
        if self.layers[idx +1].shadow:
            del self.interfaces[idx]
            del self.layers[idx+1]
            self.interfaces[idx+1].splited = True
            self.interfaces[idx+1].diagram_id1 = None            
            return
        self.interfaces[idx].splited = True
        self.interfaces[idx].diagram_id2 = None
        self.layers[idx].shadow = True
        self.interfaces[idx+1].splited = True
        self.interfaces[idx+1].diagram_id1 = None
        if self.interfaces[idx].fracture is not None:
            if self.interfaces[idx].fracture.type is FractureInterface.bottom:
                self.interfaces[idx].fracture = None
        if self.interfaces[idx+1].fracture is not None:
            if self.interfaces[idx+1].fracture.type is FractureInterface.top:
                self.interfaces[idx+1].fracture = None
            
        
    def remove_layer(self, idx, removed_res, dup):
        """Remove layer. Variable removed_res is one, that is
        was returned by remove_layer_changes. Variable dup is 
        returned by get_diagram_dup and new diagrams was added
        outside this function"""
        
        if removed_res[1]==1:
            assert removed_res[0]==1
            self.interfaces[idx].diagram_id1=self.interfaces[idx+1].diagram_id1
            self._add_shadow(idx)
            return [self.interfaces[idx].diagram_id1+1]
        self._add_shadow(idx)
        if removed_res[0]==0:
            return []
        if removed_res[0]==1:
            self._move_diagram_idx(idx, -1)
            if self.interfaces[idx+1].diagram_id1 is not None:
                return [self.interfaces[idx+1].diagram_id1]
            else:
                return [self.interfaces[idx].diagram_id1]
        if removed_res[0]==2:
            self._move_diagram_idx(idx, -2)
            return [self.interfaces[idx+1].diagram_id1, self.interfaces[idx].diagram_id1]
        raise Exception("Invalid remove layer {0} operation".format(str(idx)))
        
    def remove_interface(self, idx, removed_res):
        """Remove interface and merge layers. Variable removed_res is one, that is
        was returned by remove_interface_changes."""
        diagrams = [] 
        if self.interfaces[idx].diagram_id1  is not None:
            diagrams.append(self.interfaces[idx].diagram_id1)
            self._move_diagram_idx(idx, -1)
        del self.interfaces[idx]
        del self.layers[idx]
        return diagrams
        
    def remove_block(self, idx, removed_res):
        """Remove all block where id idx layer. Variable removed_res is one, 
        that is was returned by remove_block_changes."""        
        (first_idx, first_slice_id, layers, fractures, slices) = removed_res        
        for i in range(0, layers-1):
            del self.interfaces[first_idx+1]
            del self.layers[first_idx+1]
        self._add_shadow(first_idx)
        res = []
        for i in range(0, slices):
            res.append(first_slice_id+i)            
        self._move_diagram_idx(idx, -slices)
        return res
        
    def remove_layer_changes(self, idx):
        """Return tuple with count (removed slices,added slice, removed fractures)"""        
        fractures=0
        if idx == len(self.interfaces) or self.interfaces[idx+1].splited:
            ret = 0            
            if self.interfaces[idx+1].splited:
                if self.interfaces[idx+1].fracture is not None and \
                    self.interfaces[idx+1].fracture.type is FractureInterface.top:
                    fractures += 1
                elif self.layers[idx+1].shadow and \
                    self.interfaces[idx+1].fracture is not None and \
                    self.interfaces[idx+1].fracture.type is FractureInterface.own:
                    fractures += 1
                    ret +=1
            else:
                if self.interfaces[idx+1].fracture is not None:
                    fractures += 1            
            if self.interfaces[idx].splited:
                if self.interfaces[idx].fracture is not None and \
                    self.interfaces[idx].fracture.type is FractureInterface.bottom:
                    fractures += 1
                elif idx>0 and self.layers[idx-1].shadow and \
                    self.interfaces[idx].fracture is not None and \
                    self.interfaces[idx].fracture.type is FractureInterface.own:
                    fractures += 1
                    ret +=1
                if self.interfaces[idx].diagram_id2 is not None:
                    ret += 1
                if self.interfaces[idx+1].diagram_id1  is not None:
                    ret += 1                    
                return (ret, 0, fractures)
            # layer is first all block
            if idx==0:
                if self.interfaces[idx+1].diagram_id1  is None or \
                    self.interfaces[idx].diagram_id1  is None:
                    return (ret+1, 0, fractures)
                else:
                    return (ret+2, 0, fractures)
            # interpolated
            if self.interfaces[idx+1].diagram_id1  is None:                
                return (ret, 0, fractures)
            # remain editable and before is not splited
            if self.interfaces[idx].diagram_id1  is not None or \
                idx==0:    
                return (ret+1, 0, fractures)
            else:
                return (ret+1, 1, fractures)          
        return (0, 0, fractures)

    def remove_block_changes(self, idx):
        """Return tuple with count (first layer, removed layers,removed slices, removed fractures)"""        
        first_idx = 0
        first_slice_id = None
        layers = 0
        fractures = 0
        slices = 0
        i=idx
        while i>=0:
            layers += 1
            if self.interfaces[i].diagram_id2 is not None:
                first_slice_id = self.interfaces[i].diagram_id2
                slices += 1
            if self.interfaces[i].splited:
                first_idx = i
                if self.interfaces[i].fracture is not None and \
                    self.interfaces[i].fracture.type is FractureInterface.bottom:
                    fractures += 1
                break
            if self.interfaces[i].fracture is not None:
                fractures += 1
            if self.interfaces[i].diagram_id1 is not None:
                first_slice_id = self.interfaces[i].diagram_id1
                slices += 1
            i -= 1
        i = idx+1
        layers -= 1
        while i<len(self.interfaces):
            layers += 1
            if self.interfaces[i].diagram_id1 is not None:
                if first_slice_id is None:
                    first_slice_id = self.interfaces[i].diagram_id1
                slices += 1
            if self.interfaces[i].splited:
                if self.interfaces[i].fracture is not None and \
                    self.interfaces[i].fracture.type is FractureInterface.top:
                    fractures += 1
                break                
            if self.interfaces[i].fracture is not None:
                fractures += 1          
            i += 1
        return (first_idx, first_slice_id, layers, fractures, slices)

    def remove_interface_changes(self, idx):
        """Return tuple with count (removed slices, removed fractures)"""        
        fractures = 0
        slices = 0
        if self.interfaces[idx].diagram_id1  is not None:
            slices += 1 
        if self.interfaces[idx].fracture is not None:
            fractures += 1              
        return (slices, fractures)
                
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
        elif type is ChangeInterfaceActions.top_interpolated:
            diagram = self.interfaces[idx].diagram_id1
            self.interfaces[idx].diagram_id1 = None
            if self.interfaces[idx].diagram_id2 is not None:
                self.interfaces[idx].diagram_id2 -= 1
            if self.interfaces[idx].fracture is not None and \
                self.interfaces[idx].fracture.fracture_diagram_id is not None:
                self.interfaces[idx].fracture.fracture_diagram_id -= 1                
            self._move_diagram_idx(idx, -1)
        elif type is ChangeInterfaceActions.bottom_interpolated:
            diagram = self.interfaces[idx].diagram_id2
            self.interfaces[idx].diagram_id2 = None
            self._move_diagram_idx(idx, -1)
        return diagram
        
    def change_to_editable(self, idx, type, dup):
        """Change interface type to editable
        
        Variable dup is returned by get_diagram_dup and new diagrams was added
        outside this function"""    
        if type is ChangeInterfaceActions.editable:
            self.interfaces[idx].diagram_id1 = dup.insert_id
            self._move_diagram_idx(idx, 1)
        elif type is ChangeInterfaceActions.bottom_editable:
            self.interfaces[idx].diagram_id2 = dup.insert_id
            self._move_diagram_idx(idx, 1)
        elif type is ChangeInterfaceActions.top_editable:
            self.interfaces[idx].diagram_id1 = dup.insert_id
            self._move_diagram_idx(idx, 1) 
        
    def split_interface(self, idx, dup):
        """Split interface.
        Variable dup is returned by get_diagram_dup and new diagrams was added
        outside this function"""
        self.interfaces[idx].splited = True
        if self.interfaces[idx].fracture is not None:
            self.interfaces[idx].fracture.type = FractureInterface.top
        self.interfaces[idx].diagram_id2 = dup.insert_id
        self._move_diagram_idx(idx, 1)
        
    def split_layer(self, idx, name, depth, split_type, dup):
        """Split set layer by interface with split_type type in set depth
        
        Variable dup is returned by get_diagram_dup and new diagrams was added
        outside this function"""
        new_layer = Layer(name)
        if split_type is LayerSplitType.interpolated:
            new_interface = Interface(depth, False)
        elif split_type is LayerSplitType.editable:
            new_interface = Interface(depth, False, None, dup.insert_id)
        elif split_type is LayerSplitType.split:
            new_interface = Interface(depth, True, None, dup.insert_id, dup.insert_id+1)
        else:
            raise Exception("Invalid split operation in interface {0}".format(str(idx)))
        if dup is not None:
            self._move_diagram_idx(idx, dup.count)
        self.layers.insert(idx+1, new_layer)
        self.interfaces.insert(idx+1, new_interface)

    def set_edited_diagram(self, diagram_id):
        """Find interface accoding to diagram id, and set id as
        edited"""
        for i in range(0, len(self.interfaces)):
            if self.interfaces[i].diagram_id1 is not None and \
                self.interfaces[i].diagram_id1 == diagram_id:
                return self.set_edited_interface(i, False)
            if self.interfaces[i].fracture is not None and \
                self.interfaces[i].fracture.fracture_diagram_id is not None and \
                self.interfaces[i].fracture.fracture_diagram_id == diagram_id:
                return self.set_edited_interface(i, False, True)
            if self.interfaces[i].diagram_id2 is not None and \
                self.interfaces[i].diagram_id2 == diagram_id:
                return self.set_edited_interface(i, True)
        return True 
        
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
            return self.interfaces[idx].diagram_id2
        return self.interfaces[idx].diagram_id1

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
        
# history specific operation

    def insert_layer(self, layer, idx):
        """insert set layer"""
        self.layers.insert(idx, layer)
        
    def delete_layer(self, idx):
        """delete layer and return object"""
        ret = self.layers[idx]
        del self.layers[idx]
        return ret
        
    def change_layer(self, layer, idx):
        """Switch idx layer to set layer"""
        old = self.layers[idx]
        self.layers[idx] = layer
        return old
        
    def strip_edited(self, interface):
        """If some of interface diagram editing is set to true, 
        is set to false and return true, else false"""
        if interface.edited1:
            interface.edited1 = False
            return True
        if interface.edited2:
            interface.edited2 = False
            return True
        if interface.fracture is not None and \
            interface.fracture.edited:
            interface.fracture.edited = False
            return True
        return False
        
    def insert_interface(self, interface, idx):
        """insert set layer and move diagram indexes, if is needed"""
        self.interfaces.insert(idx, interface)
        move = 0
        if interface.diagram_id1 is not None:
            move += 1
        if interface.diagram_id2 is not None:
            move += 1
        if interface.fracture is not None and \
            interface.fracture.fracture_diagram_id is not None:
            move += 1
        if move>0:
            self._move_diagram_idx(idx+1, move)
            
    def delete_interface(self, idx):
        """delete set interface and move diagram indexes, if is 
        needed. Return deleted interface"""
        ret = self.interfaces[idx]

        del self.interfaces[idx]
        move = 0
        if ret.diagram_id1 is not None:
            move += 1
        if ret.diagram_id2 is not None:
            move += 1
        if ret.fracture is not None and \
            ret.fracture.fracture_diagram_id is not None:
            move += 1
        if move>0:
            self._move_diagram_idx(idx, -move)
        return ret 

    def change_interface(self, interface, idx):
        """Switch idx layer to set layer"""
        old = self.interfaces[idx]
        self.interfaces[idx] = interface
        
        move = 0
        if interface.diagram_id1 is not None:
            move += 1
        if interface.diagram_id2 is not None:
            move += 1
        if interface.fracture is not None and \
            interface.fracture.fracture_diagram_id is not None:
            move += 1
        if old.diagram_id1 is not None:
            move -= 1
        if old.diagram_id2 is not None:
            move -= 1
        if old.fracture is not None and \
            old.fracture.fracture_diagram_id is not None:
            move -= 1
        if move!=0:
            self._move_diagram_idx(idx+1, move)        
        return old

    def get_group_copy(self, idx, count):
        """Return copy of set interfaces and layers.
        """
        interfaces = [copy.deepcopy(self.interfaces[idx])]
        layers = []
        for i in range(idx, idx+count):
            interfaces.append(copy.deepcopy(self.interfaces[i+1]))
            layers.append(copy.deepcopy(self.layers[i]))
        return layers, interfaces
        
    def switch_group_copy(self, idx, old_count, new_layers, new_interfaces):
        """Switch count of old interfaces and layers to new set
        and return old interfaces and layers.
        """
        interfaces = [self.interfaces.pop(idx)]
        layers = []
        for i in range(idx, idx+old_count):
            interfaces.append(self.interfaces.pop(idx))
            layers.append(self.layers.pop(idx))
        for i in range(len(new_layers)-1, -1, -1):
            self.layers.insert(idx, new_layers[i])
        for i in range(len(new_interfaces)-1, -1, -1):
            self.interfaces.insert(idx, new_interfaces[i])
            
        move = 0
        for interface in new_interfaces: 
            if interface.diagram_id1 is not None:
                move += 1
            if interface.diagram_id2 is not None:
                move += 1
            if interface.fracture is not None and \
                interface.fracture.fracture_diagram_id is not None:
                move += 1
        for interface in interfaces:
            if interface.diagram_id1 is not None:
                move -= 1
            if interface.diagram_id2 is not None:
                move -= 1
            if interface.fracture is not None and \
                interface.fracture.fracture_diagram_id is not None:
                move -= 1                
        if move!=0:
            self._move_diagram_idx(idx+len(new_interfaces), move) 
        return layers, interfaces    
        
    def get_orig_copy(self, idx, count):
        """Return copy of set interfaces and layers.
        """
        interfaces = [copy.deepcopy(self.interfaces[idx])]
        layers = []
        for i in range(idx, idx+count):
            interfaces.append(copy.deepcopy(self.interfaces[i+1]))
            layers.append(copy.deepcopy(self.layers[idx]))
        return layers, interfaces
        
# display operations   
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
                if self.layers[i].shadow:
                    width = fm.width("shadow")
                else:
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
