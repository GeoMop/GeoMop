from enum import IntEnum
from copy import deepcopy

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
    """
    
    diagram_map = None
    
    def __init__(self):
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
        
    # diagram functions
    
    def set_default_region(self, object_id, topology_id, dim):
        """Set default region in set object."""
        for layer_id in self.layers_topology[topology_id]:
            if dim==1:
                self.layer_region_1D[layer_id][object_id]=0
            elif dim==2:
                self.layer_region_2D[layer_id][object_id]=1
            else:
                self.layer_region_2D[layer_id][object_id]=2
        
        
    # layer functions

    def add_fracture(self, id, name, is_own, is_top):
        """insert layer to structure and copy regions"""
        self.layers[-id] = name
        move_id = id
        if (is_top or is_own) and id>0:
            move_id = id-1
        self.layer_region_1D[-id]=deepcopy(self.layer_region_1D[move_id])
        self.layer_region_2D[-id]=deepcopy(self.layer_region_2D[move_id])
        self.layer_region_3D[-id]=deepcopy(self.layer_region_3D[move_id])
        for top_id in self.layers_topology:
            if move_id in self.layers_topology[top_id]:
                self.layers_topology[top_id].append(-id)
        if is_own:
            self.move_topology(id)
        
    def add_layer(self, id, name, oper):
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
        
        self._add_to_topology(id, id)           
        if oper is TopologyOperations.insert or oper is TopologyOperations.insert_next:            
            self.move_topology(id)           
            
    def _add_to_topology(self, id, insert_id):
        """Add layer id and increment other"""
        max_topology_key = max(self.layers_topology)
        for i in range(max_topology_key, -1, -1):
            end = False
            old = deepcopy(self.layers_topology[i])
            self.layers_topology[i] = []
            for layer_id in old:
                if layer_id<=id:
                    if not end:
                        self.layers_topology[i].append(insert_id)
                    end = True
                    if layer_id<id:
                        self.layers_topology[i].append(layer_id)
                if layer_id>=id:
                    self.layers_topology[i].append(layer_id+1)
                elif id<=-layer_id:
                    self.layers_topology[i].append(layer_id-1)
            if end:
                break
        
    def move_topology(self, id):
        """increment layers id topology and bigger. If 
        with_fracture_id is set,fracture id -1 is moved too"""
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

    def unmove_topology(self, id):
        """decrement layers id topology and bigger. If 
        with_fracture_id is set,fracture id -1 is moved too"""
        max_topology_key = max(self.layers_topology)
        move_all = False
        for i in range(0, max_topology_key+1):
            if move_all: 
                # move bigger            
                self.layers_topology[i-1] = max_topology_key[i]
            if id in self.layers_topology[i]:
                move_all = True
                for layer_id in self.layers_topology[i]:
                    self.layers_topology[i-1].append(layer_id)
        del self.layers_topology[max_topology_key]
        
    def rename_layer(self, is_fracture, id, name):
        """copy data from related structure"""
        if is_fracture:
            self.layers[-id] = name
        else:
            self.layers[id] = name
        
    def delete_fracture(self, id):    
        """delete fracture from structure"""
        del self.layers[-id]
        del self.layer_region_1D[-id]
        del self.layer_region_2D[-id]
        del self.layer_region_3D[-id]
        for top_id in self.layers_topology:
            if -id in self.layers_topology[top_id]:
                self.layers_topology[top_id].remove(-id)
                break
        
    def delete_layer(self, id):
        """delete layer from structure"""
        self._unmove_dim(id, self.layer_region_1D)
        self._unmove_dim(id, self.layer_region_2D)
        self._unmove_dim(id, self.layer_region_3D)
        
        max_layer_key = max(self.layers)
        for i in range(id, max_layer_key):
            self.layers[i] = self.layers[i+1]
            
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
    
        if max_topology_key!=j and j!=0:
            # start and end removed
            if id-1 not in self.layers_topology[-1]:
                if id-1 not in self.layers_topology[-1]:
                    # shadow befor or after
                    shadow = removed_layer[0]
                    del removed_layer[0]
                    self.layers_topology[-1].append(shadow)
                    self.layer_region_1D[shadow] = []
                    self.layer_region_2D[shadow] = []
                    self.layer_region_3D[shadow] = []
                    
        for i in sorted(removed_layer):
            if i>0:
                self._unmove_dim(i, self.layer_region_1D)
                self._unmove_dim(i, self.layer_region_2D)
                self._unmove_dim(i, self.layer_region_3D)            
                max_layer_key = max(self.layers)
                
                for i in range(i, max_layer_key):
                    self.layers[i] = self.layers[i+1]                    
            else:
                del self.layers[i]
                del self.layer_region_1D[i]
                del self.layer_region_2D[i]
                del self.layer_region_3D[i]
        
    def copy_related(self, id, name):
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
        
    def delete_data(self, id):
        """For shadow block delete data, and set topology to -1"""
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
        
    def _move_dim(self, id, layer_region):
        """Move topology structure from index id"""
        max_layer_key = max(self.layers)
        for i in range(max_layer_key, id-1, -1):
            layer_region[i+1] = layer_region[i]
            if i!=id and -i in self.layer_region:
               self.layer_region[-i-1] = self.layer_region[-i]
               del self.layer_region[-i]
               
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
        self.regions.append(Region(color, name, dim, step, boundary, not_used)) 
    
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
