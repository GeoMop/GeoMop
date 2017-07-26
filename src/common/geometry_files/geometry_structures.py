"""Structures for Layer Geometry File"""

from enum import IntEnum

class LayerType(IntEnum):
    """Layer type"""
    stratum = 0
    fracture = 1
    shadow = 2
    

class TopologyType(IntEnum):
    given = 0
    interpolated = 1


class GeoObject:
    class_def = {}
    
    def serialize(self):
        d = {}
        for k, v in self.__dict__.items():
            if isinstance(v, GeoObject):
                d[k] = v.serialize()                
            elif isinstance(v, list):
                d[k]=[]
                for item in v:
                    if isinstance(item, GeoObject):
                        d[k].append(item.serialize()) 
                    else:
                        d[k].append(item)
            else:
                d[k] = v
        return d
                
    def deserialize(self, data):
        for k, v in data.items():
            if k in self.class_def:
                if isinstance(v, list):
                    list_ = []
                    for item in v:
                        obj = self.class_def[k].__new__(self.class_def[k])
                        obj.deserialize(item)
                        list_.append(obj)
                    setattr(self, k, list_)
                else:
                    obj = self.class_def[k].__new__(self.class_def[k])
                    obj.deserialize(v)
                    setattr(self, k, obj)
            else:
                setattr(self, k, v)
    

class Surface(GeoObject):
    
    def __init__(self, depth):
        self.transform = [0, 0, depth, 1] 
        """Transform4x4Matrix"""
        self.grid = None
        """List of input grid 3DPoints. None for plane"""
        self.b_spline = None
        """B-spline,None for plane"""
        
    def get_depth(self):
        """Return surface depth in 0"""
        return self.transform[2]


class Curve(GeoObject):
    def __init__():
        pass
        
        
class Bulk(GeoObject):
    def __init__():
        pass
        
        
class Well(GeoObject):
    def __init__():
        pass
        
    
class Fracture(GeoObject):
    """Fracture object"""

    def __init__(self, region_idx):    
        self.region_idx = region_idx
        """region index"""
        self.poly_lines = []
        """Lis of Faces (polygon lines]"""


class Segment(GeoObject):
    """Face object"""
    def __init__(self, n1_idx, n2_idx):
        self.n1_idx = n1_idx
        """First point index"""
        self.n2_idx = n2_idx
        """Second point index"""
        self.surface_idx = None
        """Surface index"""


class Node(GeoObject):
    """Node coordinates"""
    
    def __init__(self, x, y):
        self.x = x
        """X - coordinate"""
        self.y = y
        """y coordinate"""
        
        
class Topology(GeoObject):
    """Topological 2D presentation of bulks,fracture and well"""
    
    class_def={
            "segments":Segment, 
            "bulks":Bulk, 
            "fractures":Fracture, 
            "wells":Well
        }

    def __init__(self):
        self.segments = []
        """List of topology segments (line)"""
        self.bulks = []
        """List of bulk objects"""
        self.fractures = []
        """List of fracture objects"""
        self.wells = []
        """List of well objects"""
 

class NodeSet(GeoObject):
    """Set of point (nodes) with topology"""
    
    class_def={
            "nodes": Node
        }
        
    def __init__(self, topology_idx):
        self.topology_idx = topology_idx
        """Topology index"""
        self.nodes = []
        """list of Nodes"""
        self.linked_node_set = None
        """node_set_idx of pair interface node set or None"""
        self.linked_nodes = []
        """If linked_node_set is not None there is list od pair indexes of nodes or none
        if node has not pair"""

        
    def reset(self):
        """Reset node set"""
        self.nodes = []

    
class SurfaceNodeSet(GeoObject):
    """Node set in space for transformation(x,y) ->(u,v). 
    Only for GL"""
    
    class_def={
            "ns_idx": NodeSet, 
            "surface_idx":Surface
        }

    def __init__(self, ns_idx, surface_idx):
        self.ns_idx = ns_idx,
        """Node set index"""
        self.surface_idx = surface_idx
        """Surface index"""


class InterpolatedNodeSet(GeoObject):
    """Two node set with same Topology in space for transformation(x,y) ->(u,v).
    If both node sets is same, topology is vertical    
    Only for GL"""
    
    class_def={
        "source_ns": NodeSet, 
        "surface_idx":Surface
    }

    def __init__(self, ns1_idx, ns2_idx, surface_idx):
        self.source_ns = [ns1_idx, ns2_idx]
        """Top and bottom node set index"""
        self.surface_idx = surface_idx
        """Surface index"""    


class GL(GeoObject):
    """Geological layers"""
    
    def __init__(self, name, type, top_type, top, bottom_type=None, bottom=None):
        self.name =  name
        """Layer Name"""
        self.layer_type = type
        """Layer type :class:`geometry_files.geometry_structures.LayerType`"""
        self.top_type = top_type
        """Topology type :class:`geometry_files.geometry_structures.TopologyType`"""
        self.top =  top
        """Accoding topology type surface node set or interpolated node set"""
        
        self.bottom_type = bottom_type
        """ optional, only for stratum type, bottom topology type 
        :class:`geometry_files.geometry_structures.TopologyType`"""
        self.bottom = bottom
        """ optional, only for stratum type, accoding bottom topology 
        type surface node set or interpolated node set"""
        
    def serialize(self):
        d = {}
        d["name"] = self.name
        d["layer_type"] = self.layer_type.value
        d["top_type"] = self.top_type.value
        d["top"] = self.top.serialize()
        if self.layer_type is LayerType.stratum:
            d["bottom_type"] = self.bottom_type.value
            d["bottom"] = self.bottom.serialize()
        return d
                
    def deserialize(self, data):
        self.name = data["name"]
        self.layer_type = LayerType(data["layer_type"])
        self.top_type = TopologyType(data["top_type"])
        if self.top_type is TopologyType.given:
            self.top = SurfaceNodeSet.__new__(SurfaceNodeSet)
        else:
            self.top = InterpolatedNodeSet.__new__(InterpolatedNodeSet)
        self.top.deserialize(data["top"])
        if self.layer_type is LayerType.stratum:
            self.bottom_type = TopologyType(data["bottom_type"])
            if self.bottom_type is TopologyType.given:
                self.bottom = SurfaceNodeSet.__new__(SurfaceNodeSet)
            else:
                self.bottom = InterpolatedNodeSet.__new__(InterpolatedNodeSet)
            self.bottom.deserialize(data["bottom"])
            
        
class UserSupplement(GeoObject):
    def __init__(self):
        self.last_node_set = 0
        """Last edited node set"""
        

class LayerGeometry(GeoObject):
    """Geometry File Layer Data"""
    class_def={
            "main_layers":GL, 
            "surfaces":Surface, 
            "curves":Curve, 
            "plane_topologies":Topology, 
            "node_sets": NodeSet, 
            "supplement":UserSupplement
        }
    
    def __init__(self):
        self.main_layers = []
        """List of geological layers"""
        self.surfaces = []
        """List of surfaces"""
        self.curves = []
        """List of curves"""
        self.plane_topologies = []
        """List of topologies"""
        self.node_sets = []
        """List of nodes"""
        self.supplement = UserSupplement()
        """Addition data that is used for displaying in layer editor"""
