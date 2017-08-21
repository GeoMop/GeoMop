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
    def __init__(self):
        self.regions = []
        """List of regions"""
        self.layers = {}
        """Dictionary of layers (layers_id:layers_name)"""
        self.layers_topology = {}
        """Dictionary of lists layers in topology (topology id:[layers_id])"""
        self.layer_region_1D = {}
        """Dictionary of indexes lists 1D shapes (points) (layers_id:[idxs])"""
        self.layer_region_2D = {}
        """Dictionary of indexes lists 2D shapes (lines) (layers_id:[idxs])"""
        self.layer_region_3D = {}
        """Dictionary of indexes lists 3D shapes (polygons) (layers_id:[idxs])"""
        
    def add_region(self, color, name, dim, step=0.01,  boundary=False, not_used=False):
        """Add region"""
        self.regions.append(Region(color, name, dim, step, boundary, not_used)) 
    
    def add_shapes_to_region(self, is_fracture, layer_id, layer_name, topology_idx, regions):
        """Add shapes to region"""
        if is_fracture:
            layer_id = "f"+str(layer_id)
        else:
            layer_id = str(layer_id)
        if not topology_idx in self.layers_topology:
            self.layers_topology[topology_idx] = [layer_id]
        else:
            if not layer_id in self.layers_topology[topology_idx]:
                self.layers_topology[topology_idx].append(layer_id)
        if not layer_id in self.layers:
            self.layers[layer_id] = layer_name
        self.layer_region_1D[layer_id] = regions[0]
        self.layer_region_2D[layer_id] = regions[1]
        self.layer_region_3D[layer_id] = regions[2]
        
    def get_shapes_from_region(self, is_fracture, layer_id):
        """Get shapes from region"""
        regions = [[], [], []]
        if is_fracture:
            layer_id = "f"+str(layer_id)
        else:
            layer_id = str(layer_id)
        if layer_id in self.layer_region_1D:
            regions[0] = self.layer_region_1D[layer_id]
        if layer_id in self.layer_region_2D:
            regions[1] = self.layer_region_2D[layer_id]
        if layer_id in self.layer_region_3D:
            regions[2] = self.layer_region_3D[layer_id]
        return regions
    
