from enum import IntEnum
from copy import deepcopy
from collections import OrderedDict
from .history import RegionHistory
from geometry_files import RegionDim

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
    
class ShapeDim(IntEnum):
    """Type of shape"""
    point = 0
    """Point"""
    line = 1
    """Line"""
    poly = 2
    """Polygon"""

class Region():
    """
    Class for graphic presentation of region
    """
    def __init__(self, color, name, dim, step,  boundary=False, not_used=False):
        self.name = name
        """Region name"""
        self.color = color
        """Region color"""
        self.dim = dim
        """dimension (point = 0, well = 1, fracture = 2, bulk = 3)"""
        self.boundary = boundary
        """Is boundary region"""
        self.not_used = not_used     
        """is used"""
        self.mesh_step = step
        """mesh step"""
        
    def cmp_shape_dim(self, layer_id, dim):
        """Compare real shape dimension on set layer with region dimension and evaluate
        if dimensions are compatible"""
        if self.dim is RegionDim.none:
            return True
        if layer_id<0:
            return self.dim.value==dim
        return self.dim.value==(dim+1)


class Regions():
    """
    Regions diagram
    
    All regions function for layer panel contains history operation without 
    label and must be placed after first history operation with label. Function 
    that worked with regions value and si not used by layer panel, should contain
    label.
    """

    DEFAULT_REGION = 0
    
    def __init__(self, global_history):
        self.regions = []
        """List of regions"""
        self.layers = {}
        """Dictionary of layers (layers_id:layers_name)"""
        self.layers_topology = {}
        """Dictionary of lists layers in topology (topology id:[layers_id])"""
        self.layers_topology[-1]=[]
        self.layer_region_0D = {}
        """Dictionary of indexes lists 1D shapes (points) (layers_id:{point.id:region.id})"""
        self.layer_region_1D = {}
        """Dictionary of indexes lists 2D shapes (lines) (layers_id:{line.id:region.id})"""
        self.layer_region_2D = {}
        """Dictionary of indexes lists 3D shapes (polygons) (layers_id:[{polygon.id:region.id}])"""
        self._history = RegionHistory(global_history)
        """History class"""
        self.current_layer_id = None
        """Id of selected layer in region panel"""
        self.current_topology_id = None
        """Id of selected topology in region panel"""
        self.current_regions = {}
        """Map all layers in current topology, and its regions"""
        self.remap_reg_from = None
        """If this variable is set, remap in move topology shapes id from set diagram"""
        self.remap_reg_to = None
        """If this variable is set, remap in move topology shapes id to values in set diagram"""

    def get_default_regions(self, topology_id):
        """Return default region"""       
        default = [] 
        for layer_id in self.layers_topology[self.current_topology_id]:
            default.append(self.DEFAULT_REGION)
        return default

    # region panels functions
    
    def _set_default_regions(self, dim, shape_id, topology_id, to_history=False, label=None):
        """Set default region in set object."""
        if not topology_id in self.layers_topology:
            return
        if dim==0:
            layer_region = self.layer_region_0D
        elif dim==1:
            layer_region = self.layer_region_1D
        else:
            layer_region = self.layer_region_2D
        for layer_id in self.layers_topology[topology_id]:
            layer_region[layer_id][shape_id]=0
            if to_history:
                self._history.change_shape_region(shape_id, layer_id, dim, None, label)
    
    def add_regions(self, dim, shape_id, to_history=False, label=None):
        """Shape region for all layers in current topology is added to 
        current value"""
        if len(self.current_regions)==0 :
            return self._set_default_regions( dim, shape_id, self.current_topology_id, to_history, label)
        if dim==0:
            layer_region = self.layer_region_0D
        elif dim==1:
            layer_region = self.layer_region_1D
        else:
            layer_region = self.layer_region_2D
        for layer_id in self.layers_topology[self.current_topology_id]:
            if not self.current_regions[layer_id].cmp_shape_dim(layer_id, dim):
                # default region
                layer_region[layer_id][shape_id] = 0
                if to_history:
                    self._history.change_shape_region(shape_id, layer_id, dim, None, label)
            else:
                region = self.current_regions[layer_id]
                layer_region[layer_id][shape_id] = self.regions.index(region)
                if to_history:
                    self._history.change_shape_region(shape_id, layer_id, dim, None, label)

    def copy_regions(self, dim, shape_id, copy_id, to_history=False, label=None):
        """Shape region for all layers in current topology is added to 
        current value"""
        if dim==0:
            layer_region = self.layer_region_0D
        elif dim==1:
            layer_region = self.layer_region_1D
        else:
            layer_region = self.layer_region_2D
        for layer_id in self.layers_topology[self.current_topology_id]:
            layer_region[layer_id][shape_id] = layer_region[layer_id][copy_id]
            if to_history:
                self._history.change_shape_region(shape_id, layer_id, dim, None, label)
        
    def set_regions(self, dim, shape_id, to_history=False, label=None):
        """Shape region for all layers in current topology is set to 
        current value"""
        ret = True
        if dim==0:
            layer_region = self.layer_region_0D
        elif dim==1:
            layer_region = self.layer_region_1D
        else:
            layer_region = self.layer_region_2D
        for layer_id in self.layers_topology[self.current_topology_id]:            
            region = self.current_regions[layer_id]            
            old_region_id = layer_region[layer_id][shape_id]
            if old_region_id!=self.regions.index(region):
                if region.cmp_shape_dim(layer_id, dim):
                    layer_region[layer_id][shape_id] = self.regions.index(region)
                    if to_history:
                        self._history.change_shape_region(shape_id, layer_id, dim, old_region_id, label)
                else:
                    ret = False
        return ret
        
    def set_regions_from_list(self, dim, shape_id, topology_id, list, to_history=False, label=None):
        """Shape region for all layers in current topology is set to 
        current value"""
        if not topology_id in self.layers_topology:
            return
        if dim==0:
            layer_region = self.layer_region_0D
        elif dim==1:
            layer_region = self.layer_region_1D
        else:
            layer_region = self.layer_region_2D
        for i in range(0, len(self.layers_topology[topology_id])):
            layer_id = self.layers_topology[topology_id][i]
            layer_region[layer_id][shape_id]=list[i]
            if to_history:
                self._history.change_shape_region(shape_id, layer_id, dim, None, label)
                    
    def set_region(self, dim, shape_id, to_history=False, label=None):
        """Shape region for current layer is set to current value"""
        if dim==0:
            layer_region = self.layer_region_0D
        elif dim==1:
            layer_region = self.layer_region_1D
        else:
            layer_region = self.layer_region_2D            
        region = self.current_regions[self.current_layer_id]            
        old_region_id = layer_region[self.current_layer_id][shape_id]
        if old_region_id!=self.regions.index(region):
            if region.cmp_shape_dim(self.current_layer_id, dim):
                layer_region[self.current_layer_id][shape_id] = self.regions.index(region)
                if to_history:
                    self._history.change_shape_region(shape_id, self.current_layer_id, dim, old_region_id, label)
            else:
                return False
        return True
        
    def set_default(self, dim, shape_id, to_history=False, label=None):
        """Shape region for current layer is set to default value.
        If region is already set to default return False"""
        if dim==0:
            layer_region = self.layer_region_0D
        elif dim==1:
            layer_region = self.layer_region_1D
        else:
            layer_region = self.layer_region_2D            
        old_region_id = layer_region[self.current_layer_id][shape_id]            
        if old_region_id==0:
            return False
        layer_region[self.current_layer_id][shape_id] = self.DEFAULT_REGION
        if to_history:
            self._history.change_shape_region(shape_id, self.current_layer_id, dim, old_region_id, label)
        return True
                
    def del_regions(self, dim, shape_id, to_history=False, label=None):
        """Shape region for all layers in current topology is removed from 
        current value"""
        if dim==0:
            layer_region = self.layer_region_0D
        elif dim==1:
            layer_region = self.layer_region_1D
        else:
            layer_region = self.layer_region_2D
        for layer_id in self.layers_topology[self.current_topology_id]:
            old_region_id = layer_region[layer_id][shape_id] 
            del layer_region[layer_id][shape_id]
            if to_history:
                self._history.change_shape_region(shape_id, layer_id, dim, old_region_id, label)                    
                
    def get_regions(self, dim, shape_id):
        """Get Shape regions for all layers in current topology"""
        if dim==0:
            layer_region = self.layer_region_0D
        elif dim==1:
            layer_region = self.layer_region_1D
        else:
            layer_region = self.layer_region_2D
        regions = []
        for layer_id in self.layers_topology[self.current_topology_id]:
            regions.append(layer_region[layer_id][shape_id])
        return regions
        
    def get_region(self, dim, shape_id):
        """Get Shape regions for all layers in current topology"""
        if dim==0:
            layer_region = self.layer_region_0D
        elif dim==1:
            layer_region = self.layer_region_1D
        else:
            layer_region = self.layer_region_2D
        return layer_region[self.current_layer_id][shape_id]
        
    def get_region_color(self, dim, shape_id):
        """Return current region color for set shape"""
        if dim==0:
            return self.regions[self.layer_region_0D[self.current_layer_id][shape_id]].color
        elif dim==1:
            return self.regions[self.layer_region_1D[self.current_layer_id][shape_id]].color
        return self.regions[self.layer_region_2D[self.current_layer_id][shape_id]].color
        
    def get_region_id(self, dim, shape_id):
        """Return current region color for set shape"""
        if dim==0:
            return self.layer_region_0D[self.current_layer_id][shape_id]
        elif dim==1:
            return self.layer_region_1D[self.current_layer_id][shape_id]
        return self.layer_region_2D[self.current_layer_id][shape_id]
    
    def get_layers(self, topology_idx):
        """Return dictionary layers (id:layer_name) with set topology"""
        pom = {}
        for id in self.layers_topology[topology_idx]:
            pom[id] = self.layers[id]
        ret = OrderedDict(sorted(pom.items(), key=lambda x: 2*x[0] if x[0]>=0 else -2*x[0]-3))        
        return ret
        
    def add_new_region(self, color, name, dim, to_history=False, label=None):
        """Add region"""
        region = Region(color, name, dim, step = 0.0)
        self.regions.append(region)
        if to_history:
            self._history.delete_region(len(self.regions)-1, label)
        return region   
  
    def insert_region(self, id, region, to_history=True, label=None):
        """Add region"""
        self.regions.insert(id, region)
        if to_history:
            self._history.delete_region(id, label) 
        return region
      
    def set_region_name(self, id, name, to_history=False, label=None):
        """Add region"""
        region = deepcopy(self.regions[id])
        self.regions[id].name = name
        if to_history:
            self._history.change_region(id, region, label) 
        return region 
       
    def set_region_color(self, id, color, to_history=False, label=None):
        """Add region"""
        region = deepcopy(self.regions[id])
        self.regions[id].color = color
        if to_history:
            self._history.change_region(id, region, label) 
        return region 

    def set_region_boundary(self, id, boundary, to_history=False, label=None):
        """Add region"""
        region = deepcopy(self.regions[id])
        self.regions[id].boundary = boundary
        if to_history:
            self._history.change_region(id, region, label)         
        return region 

    def set_region_mesh_step(self, id, step, to_history=False, label=None):
        """Add region"""
        region = deepcopy(self.regions[id])
        self.regions[id].mesh_step = step
        if to_history:
            self._history.change_region(id, region, label)
        return region

    def set_region_not_used(self, id, not_used, to_history=False, label=None):
        """Add region"""
        region = deepcopy(self.regions[id])
        self.regions[id].not_used = not_used
        if to_history:
            self._history.change_region(id, region, label) 
        
    def delete_region(self, id, to_history=True, label=None):
        """Add region"""
        region = self.regions[id]
        del self.regions[id]
        if to_history:
            self._history.insert_region(id, region, label) 
        return region        
    # layer panel functions

    def add_fracture(self, id, name, is_own, is_bottom, to_history=True):
        """insert layer to structure and copy regions"""
        self.layers[-id-1] = name        
        move_id = None
        if (not is_bottom and not is_own):
            move_id, topology_id = self._find_less(id)
        if move_id is None:
            move_id = id
        self._copy_regions_to_default(-id-1, move_id)
        for top_id in self.layers_topology:
            if move_id in self.layers_topology[top_id]:
                self.layers_topology[top_id].append(-id-1)
        if is_own:
            self.move_topology(id, False)
        if to_history:
            self._history.delete_fracture(id)            
            self._history.save_data(-id-1, self.layer_region_0D[-id-1], self.layer_region_1D[-id-1], 
                self.layer_region_2D[-id-1])
                
    def _copy_regions_to_default(self, id, move_id):
        """for set layer copy regions and set theirs value to default"""
        for layer_region in [self.layer_region_0D, self.layer_region_1D, self.layer_region_2D]:
            layer_region[id]=deepcopy(layer_region[move_id])
            for shape_id in layer_region[id]:
                layer_region[id][shape_id] = 0
            
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
            move_id, topology_id = self._find_more(id-1)
        self._move_dim(id, self.layer_region_0D)
        self.layer_region_0D[id]=deepcopy(self.layer_region_0D[move_id])
        self._move_dim(id, self.layer_region_1D)
        self.layer_region_1D[id]=deepcopy(self.layer_region_1D[move_id])
        self._move_dim(id, self.layer_region_2D)
        self.layer_region_2D[id]=deepcopy(self.layer_region_2D[move_id])
        
        max_layer_key = max(self.layers)
        for i in range(max_layer_key, id-1, -1):
            self.layers[i+1] = self.layers[i]
            if i!=id and -i in self.layers:
               self.layers[-i-1] = self.layers[-i]
               del self.layers[-i]
        self.layers[id]=name
        if to_history:
            self._history.delete_layer(id)
            self._history.save_data(id, self.layer_region_0D[id], self.layer_region_1D[id], 
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
                if layer_id<=id and id>=-layer_id-1:
                    if not end:
                        self.layers_topology[i].append(id)
                    end = True
                    if layer_id<id:
                        self.layers_topology[i].append(layer_id)
                if layer_id>=id:
                    self.layers_topology[i].append(layer_id+1)
                elif id<-layer_id-1:
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
            if -id-1 in self.layers_topology[i]:
                self.layers_topology[i].remove(-id-1)
            if len(self.layers_topology[i])==0:
                del_row += 1
                if max_topology_key==i:
                    del self.layers_topology[i]
            else:            
                if max(self.layers_topology[i])>id or min(self.layers_topology[i])<-id-1:
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
        
    def remap_region_shapes(self, top_id, to_history=True):
        """Remap all shapes id in set topology to new diagram"""
        for id in self.layers_topology[top_id]:
            new_reg = {}
            for i in range(0, len(self.remap_reg_from.points)):
                new_reg[self.remap_reg_to.points[i].id] = self.layer_region_0D[id][self.remap_reg_from.points[i].id]
            r0D = self.layer_region_0D[id]    
            self.layer_region_0D[id] = new_reg
            new_reg = {}
            for i in range(0, len(self.remap_reg_from.lines)):
                new_reg[self.remap_reg_to.lines[i].id] = self.layer_region_1D[id][self.remap_reg_from.lines[i].id]
            r1D = self.layer_region_1D[id]    
            self.layer_region_1D[id] = new_reg
            new_reg = {}
            for i in range(0, len(self.remap_reg_from.polygons)):
                new_reg[self.remap_reg_to.polygons[i].id] = self.layer_region_2D[id][self.remap_reg_from.polygons[i].id]
            r2D = self.layer_region_2D[id]    
            self.layer_region_2D[id] = new_reg
            if to_history:
                self._history.change_data(self.remap_reg_to, id, r0D, r1D, r2D)                
        self.remap_reg_from = None
        self.remap_reg_to = None
            
    def move_topology(self, id, to_history=True):
        """increment layers id topology and bigger."""
        max_topology_key = max(self.layers_topology)
        new_top = None
        for i in range(max_topology_key, -1, -1):
            if id in self.layers_topology[i]:
                #split rest
                new_top = i+1
                self.layers_topology[i+1] = []
                for layer_id in self.layers_topology[i]:
                    if layer_id>=id or id<-layer_id-1:
                        self.layers_topology[i+1].append(layer_id)
                for layer_id in self.layers_topology[i+1]:
                    self.layers_topology[i].remove(layer_id)
                break
            # move bigger            
            self.layers_topology[i+1] = self.layers_topology[1]
        if self.remap_reg_from is not None:
            self.remap_region_shapes(new_top, to_history)
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
            self.layers[-id-1] = name
        else:
            self.layers[id] = name
        if to_history:            
            self._history.rename_layer(is_fracture, id, name)
        
    def delete_fracture(self, id, to_history=True):    
        """delete fracture from structure"""
        topology_removed = False
        is_bottom = self.get_topology(-id-1) == self.get_topology(id)
        name = self.layers[-id-1]
        
        del self.layers[-id-1]
        r0D = self.layer_region_0D[-id-1]
        del self.layer_region_0D[-id-1]
        r1D = self.layer_region_1D[-id-1]
        del self.layer_region_1D[-id-1]
        r2D = self.layer_region_2D[-id-1]
        del self.layer_region_2D[-id-1]
        for top_id in self.layers_topology:
            if -id-1 in self.layers_topology[top_id]:
                self.layers_topology[top_id].remove(-id-1)
                if len(self.layers_topology[top_id])==0:
                    move_id, topology_id = self._find_more(id)
                    if topology_id is not None:                    
                        self.unmove_topology(move_id, False)
                        topology_removed = True
                break
        if to_history:            
            self._history.add_fracture(id, name, is_bottom, topology_removed) 
            self._history.load_data(-id-1, r0D, r1D, r2D)
        return topology_removed
        
    def delete_layer(self, id, to_history=True):
        """delete layer from structure"""
        name = self.layers[id]
        
        r0D = self.layer_region_0D[id]
        self._unmove_dim(id, self.layer_region_0D)
        r1D = self.layer_region_1D[id]
        self._unmove_dim(id, self.layer_region_1D)
        r2D = self.layer_region_2D[id]
        self._unmove_dim(id, self.layer_region_2D)
        
        max_layer_key = max(self.layers)
        for i in range(id, max_layer_key):
            self.layers[i] = self.layers[i+1]
            
        del_row = self._remove_from_topology(id)
        if to_history:
            self._history.add_layer(id, name, del_row>0)
            self._history.load_data(id, r0D, r1D, r2D)
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
                    r0D = self.layer_region_0D[shadow]
                    r1D = self.layer_region_1D[shadow]
                    r2D = self.layer_region_2D[shadow]
                    self.layer_region_0D[shadow] = []
                    self.layer_region_1D[shadow] = []
                    self.layer_region_2D[shadow] = []
                    self._history.rename_layer(False, id, old_name)
                    self._history.load_data(id, r0D, r1D, r2D)
                    remove_shadow = False
        
        for i in sorted(removed_layer):
            if i>=0:
                name = self.layers[i]
                r0D = self.layer_region_0D[i]
                r1D = self.layer_region_1D[i]
                r2D = self.layer_region_2D[i]                 
                self._history.add_layer(i, name, i==0 and remove_shadow)
                self._history.load_data(i, r0D, r1D, r2D)                
        
        for i in sorted(removed_layer, reverse=True):
            if i>0:
                self._unmove_dim(i, self.layer_region_0D)
                self._unmove_dim(i, self.layer_region_1D)
                self._unmove_dim(i, self.layer_region_2D)            
                max_layer_key = max(self.layers)                
                for i in range(i, max_layer_key):
                    self.layers[i] = self.layers[i+1]
            else:
                name = self.layers[i]
                r0D = self.layer_region_0D[i]
                r1D = self.layer_region_1D[i]
                r2D = self.layer_region_2D[i]
                del self.layers[i]
                del self.layer_region_0D[i]
                del self.layer_region_1D[i]
                del self.layer_region_2D[i]
                self._history.delete_fracture(-i-1, name, False, False) 
                self._history.load_data(i, r0D, r1D, r2D)
        
    def copy_related(self, id, name, to_history=True):
        """copy data from related structure"""
        self.layers[id] = name
        copy_id, topology_id = self._find_less(id)
        move_id, topology_id = self._find_more(id)
        self.move_topology(move_id)
        self.layers_topology[-1].remove(id)
        self.layers_topology[topology_id].append(id)
        if id<0:
            self._copy_regions_to_default(self, 1, copy_id)
        else:
            self.layer_region_0D[id]=deepcopy(self.layer_region_0D[copy_id])
            self.layer_region_1D[id]=deepcopy(self.layer_region_1D[copy_id])
            self.layer_region_2D[id]=deepcopy(self.layer_region_2D[copy_id])
        if to_history:
            self._history.delete_data(id)
        
    def delete_data(self, id, to_history=True):
        """For shadow block delete data, and set topology to -1"""
        old_name = self.layers[id]
        r0D = self.layer_region_0D[id]
        r1D = self.layer_region_1D[id]
        r2D = self.layer_region_2D[id]
        self.layer_region_0D[id] = []
        self.layer_region_1D[id] = []
        self.layer_region_2D[id] = []
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
            self._history.rename_layer(False, id, old_name)
            self._history.load_data(id, r0D, r1D, r2D)
        
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
        
    def find_top_id(self, id):
        """return topology id for set layer id"""
        for top_id in self.layers_topology:
            if id in self.layers_topology[top_id]:
                return top_id
        return None        
        
    # serialize functions    
        
    def add_region(self, color, name, dim, step,  boundary=False, not_used=False):
        """Add region"""
        region = Region(color, name, dim, step, boundary, not_used)
        self.regions.append(region)
    
    def add_shapes_to_region(self, is_fracture, layer_id, layer_name, topology_idx, regions):
        """
        Add shapes to region
        
        Call diagram static function make_revert_map before this function
        """
        if is_fracture:
            layer_id = -layer_id-1
        if not topology_idx in self.layers_topology:
            self.layers_topology[topology_idx] = [layer_id]
        else:
            if not layer_id in self.layers_topology[topology_idx]:
                self.layers_topology[topology_idx].append(layer_id)
        if not layer_id in self.layers:
            self.layers[layer_id] = layer_name
            
        self.layer_region_0D[layer_id] = regions[0]
        self.layer_region_1D[layer_id] = regions[1]
        self.layer_region_2D[layer_id] = regions[2]
        
    def get_shapes_from_region(self, is_fracture, layer_id):
        """
        Get shapes from region
        Call diagram static function make_map before this function
        """
        regions = [{}, {}, {}]
        if is_fracture:
            layer_id = -layer_id-1
        else:
            layer_id = layer_id
        
        if layer_id in self.layer_region_0D:
            regions[0] = self.layer_region_0D[layer_id]
        if layer_id in self.layer_region_1D:
            regions[1] = self.layer_region_1D[layer_id]
        if layer_id in self.layer_region_2D:
            regions[2] = self.layer_region_2D[layer_id]
        return regions
