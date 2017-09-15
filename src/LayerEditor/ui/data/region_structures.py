from enum import IntEnum
from copy import deepcopy
from collections import OrderedDict
from .history import RegionHistory

class TopologyOperations(IntEnum):
    """Type of topology operation"""
    none = 0
    """Added diagrams have topology index copy_top_id"""
    insert = 1
    """Added diagrams have topology index 
    copy_top_id+1 and next is move about 1"""
    insert_next = 2
    """First added diagram have topology index
    copy_top_id, next added diagrams have topology 
    index copy_top_id+1 and next is move about 1"""

class Region():
    """
    Class for graphic presentation of region
    """
    def __init__(self, color, name, dim, step=0.01,  boundary=False, not_used=False):
        self.name = name
        """Region name"""
        self.color = color
        """Region color"""
        self.dim = dim
        """dimension (dim=1 well, dim=2 fracture, dim=3 bulk)"""
        self.boundary = boundary
        """Is boundary region"""
        self.not_used = not_used     
        """is used"""
        self.mesh_step = step
        """mesh step"""


class Regions():
    """
    Regions diagram
    
    All regions function for layer panel contains history operation without 
    label and must be placed after first history operation with label. Function 
    that worked with regions value and si not used by layer panel, should contain
    label.
    """
    
    diagram_map = None
    
    def __init__(self, global_history):
        self.regions = []
        """List of regions"""
        self.layers = {}
        """Dictionary of layers (layers_id:layers_name)"""
        self.layers_topology = {}
        """Dictionary of lists layers in topology (topology id:[layers_id])"""
        self.layers_topology[-1]=[]
        self.layer_region_1D = {}
        """Dictionary of indexes lists 1D shapes (points) (layers_id:{point.id:region.id})"""
        self.layer_region_2D = {}
        """Dictionary of indexes lists 2D shapes (lines) (layers_id:{line.id:region.id})"""
        self.layer_region_3D = {}
        """Dictionary of indexes lists 3D shapes (polygons) (layers_id:[{polygon.id:region.id}])"""
        self._history = RegionHistory(global_history)
        """History class"""
        
    # region panels functions
    
    def get_layers(self, topology_idx):
        """Return dictionary layers (id:layer_name) with set topology"""
        pom = {}
        for id in self.layers_topology[topology_idx]:
            pom[id] = self.layers[id]
        ret = OrderedDict(sorted(pom.items(), key=lambda x: 2*x[0] if x[0]>0 else -2*x[0]-1))        
        return ret
        
    def add_new_region(self, color, name, dim):
        """Add region"""
        region = Region(color, name, dim)
        self.regions.append(region)
        self._history.delete_region(id, "Add new region")
        return region   
  
    def insert_region(self, id, region, to_history=True, label=None):
        """Add region"""
        self.regions.insert(id, region)
        if to_history:
            self._history.delete_region(id, label) 
        return region
      
    def set_region_name(self, id, name):
        """Add region"""
        region = deepcopy(self.regions[id])
        self.regions[id].name = name
        self._history.change_region(id, region, "Set region name") 
        return region 
       
    def set_region_color(self, id, color):
        """Add region"""
        region = deepcopy(self.regions[id])
        self.regions[id].color = color
        self._history.change_region(id, region, "Set region color") 
        return region 

    def set_region_boundary(self, id, boundary):
        """Add region"""
        region = deepcopy(self.regions[id])
        self.regions[id].boundary = boundary
        self._history.change_region(id, region, "Set region boundary")         
        return region 

    def set_region_not_use(self, id, not_use):
        """Add region"""
        region = deepcopy(self.regions[id])
        self.regions[id].not_use = not_use
        self._history.change_region(id, region, "Set region usage") 
        
    def delete_region(self, id, to_history=True, label=None):
        """Add region"""
        region = self.regions[id]
        del self.regions[id]
        if to_history:
            self._history.insert_region(id, region, label) 
        return region
        
    # diagram functions
    
    def set_default_region(self, object_id, topology_id, dim):
        """Set default region in set object."""
        if not topology_id in self.layers_topology:
            return
        for layer_id in self.layers_topology[topology_id]:
            if dim==1:
                self.layer_region_1D[layer_id][object_id]=0
            elif dim==2:
                self.layer_region_2D[layer_id][object_id]=1
            else:
                self.layer_region_3D[layer_id][object_id]=2        
        
    # layer panel functions

    def add_fracture(self, id, name, is_own, is_top, to_history=True):
        """insert layer to structure and copy regions"""
        self.layers[-id] = name        
        move_id = None
        if (not is_top):
            move_id, topology_id = self._find_less(id)
        if move_id is None:
            move_id = id
        self.layer_region_1D[-id]=deepcopy(self.layer_region_1D[move_id])
        self.layer_region_2D[-id]=deepcopy(self.layer_region_2D[move_id])
        self.layer_region_3D[-id]=deepcopy(self.layer_region_3D[move_id])
        for top_id in self.layers_topology:
            if move_id in self.layers_topology[top_id]:
                self.layers_topology[top_id].append(-id)
        if is_own:
            self.move_topology(id, False)
        if to_history:
            self._history.delete_fracture(-id)            
            self._history.save_data(-id, self.layer_region_1D[-id], self.layer_region_2D[-id], 
                self.layer_region_2D[-id])
            
    def add_layer_history(self, id, name, insert):
        """Add layer for reverse history operation"""
        oper = TopologyOperations.none
        if insert:
            oper = TopologyOperations.insert
        self.add_layer(id, name, oper, False)
        
    def get_topology(self, layer_id):
        """Get topology id for set layer or fracture"""
        max_topology_key = max(self.layers_topology) 
        for i in range(0, max_topology_key+1):
            if layer_id in self.layers_topology[i]:
                return i        
        
    def add_layer(self, id, name, oper, to_history=True):
        """insert layer to structure and copy regions"""
        move_id, topology_id = self._find_less(id)
        if move_id is None:
            move_id, topology_id = self._find_more(id)
        self._move_dim(id, self.layer_region_1D)
        self.layer_region_1D[id]=deepcopy(self.layer_region_1D[move_id])
        self._move_dim(id, self.layer_region_2D)
        self.layer_region_2D[id]=deepcopy(self.layer_region_2D[move_id])
        self._move_dim(id, self.layer_region_3D)
        self.layer_region_3D[id]=deepcopy(self.layer_region_3D[move_id])
        
        max_layer_key = max(self.layers)
        for i in range(max_layer_key, id-1, -1):
            self.layers[i+1] = self.layers[i]
            if i!=id and -i in self.layers:
               self.layers[-i-1] = self.layers[-i]
               del self.layers[-i]
        self.layers[id]=name
        if to_history:
            self._history.delete_layer(id)
            self._history.save_data(id, self.layer_region_1D[id], self.layer_region_2D[id], 
                self.layer_region_2D[id])
        
        self._add_to_topology(id)           
        if oper is TopologyOperations.insert or oper is TopologyOperations.insert_next:            
            self.move_topology(id, False)           
            
    def _add_to_topology(self, id):
        """Add layer id and increment other"""
        max_topology_key = max(self.layers_topology)
        for i in range(max_topology_key, -1, -1):
            end = False
            old = deepcopy(self.layers_topology[i])
            self.layers_topology[i] = []
            for layer_id in old:
                if layer_id<=id and id>=-layer_id:
                    if not end:
                        self.layers_topology[i].append(id)
                    end = True
                    if layer_id<id:
                        self.layers_topology[i].append(layer_id)
                if layer_id>=id:
                    self.layers_topology[i].append(layer_id+1)
                elif id<=-layer_id:
                    self.layers_topology[i].append(layer_id-1)
            if end:
                break
                
    def _remove_from_topology(self, id):
        """Remove layer id and decrement other"""
        max_topology_key = max(self.layers_topology) 
        del_row = 0
        for i in range(0, max_topology_key+1):
            if id in self.layers_topology[i]:
                self.layers_topology[i].remove(id)
            if -id in self.layers_topology[i]:
                self.layers_topology[i].remove(-id)
            if len(self.layers_topology[i])==0:
                del_row += 1
                if max_topology_key==i:
                    del self.layers_topology[i]
            else:            
                if max(self.layers_topology[i])>id or min(self.layers_topology[i])<-id:
                    old = deepcopy(self.layers_topology[i])
                    self.layers_topology[i-del_row] = []
                    for layer_id in old:
                        if layer_id>id:
                            self.layers_topology[i-del_row].append(layer_id-1)
                        elif layer_id<-id:
                            self.layers_topology[i-del_row].append(layer_id+1)
                        else:
                            self.layers_topology[i-del_row].append(layer_id)
        return del_row
        
    def move_topology(self, id, to_history=True):
        """increment layers id topology and bigger."""
        max_topology_key = max(self.layers_topology)
        for i in range(max_topology_key, -1, -1):
            if id in self.layers_topology[i]:
                #split rest
                self.layers_topology[i+1] = []
                for layer_id in self.layers_topology[i]:
                    if layer_id>=id or id<=-layer_id:
                        self.layers_topology[i+1].append(layer_id)
                for layer_id in self.layers_topology[i+1]:
                    self.layers_topology[i].remove(layer_id)
                break
            # move bigger            
            self.layers_topology[i+1] = max_topology_key[i]
        if to_history:
            self._history.unmove_topology(id)

    def unmove_topology(self, id, to_history=True):
        """decrement layers id topology and bigger."""
        max_topology_key = max(self.layers_topology)
        move_all = False
        for i in range(0, max_topology_key+1):
            if move_all: 
                # move bigger            
                self.layers_topology[i-1] = max_topology_key[i]
            else:
                if id in self.layers_topology[i]:
                    move_all = True
                    for layer_id in self.layers_topology[i]:
                        self.layers_topology[i-1].append(layer_id)
        del self.layers_topology[max_topology_key]
        if to_history:
            self._history.move_topology(id)
        
    def rename_layer(self, is_fracture, id, name, to_history=True):
        """copy data from related structure"""
        if is_fracture:
            self.layers[-id] = name
        else:
            self.layers[id] = name
        if to_history:            
            self._history.rename_layer(is_fracture, id, name)
        
    def delete_fracture(self, id, to_history=True):    
        """delete fracture from structure"""
        topology_removed = False
        is_top = self.get_topology(-id) == self.get_topology(id)
        name = self.layers[-id]
        
        del self.layers[-id]
        r1D = self.layer_region_1D[-id]
        del self.layer_region_1D[-id]
        r2D = self.layer_region_2D[-id]
        del self.layer_region_2D[-id]
        r3D = self.layer_region_3D[-id]
        del self.layer_region_3D[-id]
        for top_id in self.layers_topology:
            if -id in self.layers_topology[top_id]:
                self.layers_topology[top_id].remove(-id)
                if len(self.layers_topology[top_id])==0:
                    move_id, topology_id = self._find_more(id)
                    if topology_id is not None:                    
                        self.unmove_topology(move_id, False)
                        topology_removed = True
                break
        if to_history:            
            self._history.add_fracture(id, name, is_top, topology_removed) 
            self._history.load_data(id, r1D, r2D, r3D)
        return topology_removed
        
    def delete_layer(self, id, to_history=True):
        """delete layer from structure"""
        name = self.layers[id]
        
        r1D = self.layer_region_1D[id]
        self._unmove_dim(id, self.layer_region_1D)
        r2D = self.layer_region_2D[id]
        self._unmove_dim(id, self.layer_region_2D)
        r3D = self.layer_region_3D[id]
        self._unmove_dim(id, self.layer_region_3D)
        
        max_layer_key = max(self.layers)
        for i in range(id, max_layer_key):
            self.layers[i] = self.layers[i+1]
            
        del_row = self._remove_from_topology(id)
        if to_history:
            self._history.add_layer(id, name, del_row>0)
            self._history.load_data(id, r1D, r2D, r3D)
        return del_row>0
        
    def delete_block(self, id, layers):
        """delete block from structure"""
        max_topology_key = max(self.layers_topology)
        removed_layer = None
        j=0
        for i in range(0, max_topology_key+1):
            if removed_layer is not None:
                j=i
                self.layers_topology[i-1] = self.layers_topology[i]
            if id in self.layers_topology[i]:
                removed_layer = self.layers_topology[i]
        del self.layers_topology[max_topology_key]
        
        remove_shadow = True
    
        if max_topology_key!=j and j!=0:
            # start or end is not removed
            if id-1 not in self.layers_topology[-1]:
                if id-1 not in self.layers_topology[-1]:
                    # other shadow is not befor or after
                    shadow = removed_layer[0]
                    old_name = self.layers[removed_layer[0]]
                    del removed_layer[0]
                    self.layers_topology[-1].append(shadow)
                    r1D = self.layer_region_1D[shadow]
                    r2D = self.layer_region_2D[shadow]
                    r3D = self.layer_region_3D[shadow]
                    self.layer_region_1D[shadow] = []
                    self.layer_region_2D[shadow] = []
                    self.layer_region_3D[shadow] = []
                    self._history.copy_data(id, old_name)
                    self._history.load_data(id, r1D, r2D, r3D)
                    remove_shadow = False
        
        for i in sorted(removed_layer):
            if i>=0:
                name = self.layers[i]
                r1D = self.layer_region_1D[i]
                r2D = self.layer_region_2D[i]
                r3D = self.layer_region_3D[i]                 
                self._history.add_layer(i, name, i==0 and remove_shadow)
                self._history.load_data(i, r1D, r2D, r3D)                
        
        for i in sorted(removed_layer, reverse=True):
            if i>0:
                self._unmove_dim(i, self.layer_region_1D)
                self._unmove_dim(i, self.layer_region_2D)
                self._unmove_dim(i, self.layer_region_3D)            
                max_layer_key = max(self.layers)                
                for i in range(i, max_layer_key):
                    self.layers[i] = self.layers[i+1]
            else:
                name = self.layers[i]
                r1D = self.layer_region_1D[i]
                r2D = self.layer_region_2D[i]
                r3D = self.layer_region_3D[i]
                del self.layers[i]
                del self.layer_region_1D[i]
                del self.layer_region_2D[i]
                del self.layer_region_3D[i]
                self._history.delete_fracture(-i, name, False, False) 
                self._history.load_data(i, r1D, r2D, r3D)
        
    def copy_related(self, id, name, to_history=True):
        """copy data from related structure"""
        self.layers[id] = name
        copy_id, topology_id = self._find_less(id)
        move_id, topology_id = self._find_more(id)
        self.move_topology(move_id)
        self.layers_topology[-1].remove(id)
        self.layers_topology[topology_id].append(id)
        self.layer_region_1D[id]=deepcopy(self.layer_region_1D[copy_id])
        self.layer_region_2D[id]=deepcopy(self.layer_region_2D[copy_id])
        self.layer_region_3D[id]=deepcopy(self.layer_region_3D[copy_id])
        if to_history:
            self._history.delete_data(id)
        
    def delete_data(self, id, to_history=True):
        """For shadow block delete data, and set topology to -1"""
        old_name = self.layers[id]
        r1D = self.layer_region_1D[id]
        r2D = self.layer_region_2D[id]
        r3D = self.layer_region_3D[id]
        self._unmove_dim(id, self.layer_region_3D)
        self.layer_region_1D[id] = []
        self.layer_region_2D[id] = []
        self.layer_region_3D[id] = []
        self.layers[id] = "shadow"
        for top_id in self.layers_topology:
            if id in self.layers_topology[top_id]:
                self.layers_topology[top_id].remove(id)
                if len(self.layers_topology[top_id])==0:
                    move_id, topology_id = self._find_more(id)
                    if topology_id is not None:                    
                        self.unmove_topology(move_id)
                    else:
                        del self.layers_topology[top_id]
                break
        self.layers_topology[-1].append(id)
        if to_history:
            self._history.copy_data(id, old_name)
            self._history.load_data(id, r1D, r2D, r3D)
        
    def _move_dim(self, id, layer_region):
        """Move topology structure from index id"""
        max_layer_key = max(self.layers)
        for i in range(max_layer_key, id-1, -1):
            layer_region[i+1] = layer_region[i]
            if i!=id and -i in layer_region:
               layer_region[-i-1] = layer_region[-i]
               del layer_region[-i]
               
    def _unmove_dim(self, id, layer_region):
        """UnMove topology structure from index id"""
        max_layer_key = max(self.layers)
        for i in range(id, max_layer_key):
            layer_region[i] = layer_region[i+1]
    
    def _find_less(self, id):
        """Find less layer and return its id and topology id"""
        i = id-1
        while i>=0:
            if i not in self.layers_topology[-1]:
                for top_id in self.layers_topology:
                    if i in self.layers_topology[top_id]:
                        return i, top_id
            i -= 1
        return None, None
    
    def _find_more(self, id):
        """Find bigger layer and return its id and topology id"""
        i = id+1
        while i<len(self.layers):
            if i not in self.layers_topology[-1]:
                for top_id in self.layers_topology:
                    if i in self.layers_topology[top_id]:
                        return i, top_id
            i += 1
        return None, None
        
    def _find(self, id):
        """return topology id"""
        for top_id in self.layers_topology:
            if id in self.layers_topology[top_id]:
                return top_id
        return None
        
        
    # serialize functions    
        
    def add_region(self, color, name, dim, step=0.01,  boundary=False, not_used=False):
        """Add region"""
        region = Region(color, name, dim, step, boundary, not_used)
        self.regions.append(region)
    
    def add_shapes_to_region(self, is_fracture, layer_id, layer_name, topology_idx, regions):
        """
        Add shapes to region
        
        Call diagram static function make_revert_map before this function
        """
        if is_fracture:
            layer_id = -layer_id
        if not topology_idx in self.layers_topology:
            self.layers_topology[topology_idx] = [layer_id]
        else:
            if not layer_id in self.layers_topology[topology_idx]:
                self.layers_topology[topology_idx].append(layer_id)
        if not layer_id in self.layers:
            self.layers[layer_id] = layer_name
            
        top_id = self._find(layer_id) 
        self.layer_region_1D[layer_id]={}
        self.layer_region_2D[layer_id]={}
        self.layer_region_3D[layer_id]={}
            
        for i in range(0, len(regions[0])):
            self.layer_region_1D[layer_id][self.diagram_map[top_id][0][i]] = regions[0][i] 
        for i in range(0, len(regions[1])):
            self.layer_region_2D[layer_id][self.diagram_map[top_id][1][i]] = regions[1][i] 
        for i in range(0, len(regions[2])):
            self.layer_region_3D[layer_id][self.diagram_map[top_id][2][i]] = regions[2][i]
        
    def get_shapes_from_region(self, is_fracture, layer_id):
        """
        Get shapes from region
        Call diagram static function make_map before this function
        """
        regions = [[], [], []]
        if is_fracture:
            layer_id = -layer_id
        else:
            layer_id = layer_id
        
        top_id = self._find(layer_id)
        if layer_id in self.layer_region_1D:
            tmp = {}
            for id, reg in self.layer_region_1D[layer_id].items():
                tmp[self.diagram_map[top_id][0][id]] = reg 
            regions[0] = [value for (key, value) in sorted(tmp.items())]
        if layer_id in self.layer_region_2D:
            tmp = {}
            for id, reg in self.layer_region_2D[layer_id].items():
                tmp[self.diagram_map[top_id][1][id]] = reg 
            regions[1] = [value for (key, value) in sorted(tmp.items())]
        if layer_id in self.layer_region_3D:
            tmp = {}
            for id, reg in self.layer_region_3D[layer_id].items():
                tmp[self.diagram_map[top_id][2][id]] = reg 
            regions[2] = [value for (key, value) in sorted(tmp.items())]

        return regions
