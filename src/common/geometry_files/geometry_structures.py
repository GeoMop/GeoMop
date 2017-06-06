"""Structures for Layer Geometry File"""

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
                    setattr(self, k, obj.deserialize(v))
            else:
                setattr(self, k, v)
    

class Surface(GeoObject):
    def __init__():
        pass


class Curve(GeoObject):
    def __init__():
        pass
        
        
class Bulk(GeoObject):
    def __init__():
        pass
        
        
class Well(GeoObject):
    def __init__():
        pass

class GL(GeoObject):
    """Geological layers"""
    
    def __init__(self, top_idx, bottom_idx):
        self.top_idx =  top_idx
        """Top topology index"""
        self.bottom_idx = bottom_idx
        """Bootom topology index"""

    
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
        
    def reset(self):
        """Reset node set"""
        self.nodes = []
        
        
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
            "suplement":UserSupplement
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
