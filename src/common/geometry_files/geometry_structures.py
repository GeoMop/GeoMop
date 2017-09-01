"""Structures for Layer Geometry File"""

import sys
import os
geomop_src = os.path.join(os.path.split(os.path.dirname(os.path.realpath(__file__)))[0], "common")
sys.path.append(geomop_src)

from json_data import *




class LayerType(IntEnum):
    """Layer type"""
    stratum = 0
    fracture = 1
    shadow = 2
    

class TopologyType(IntEnum):
    given = 0
    interpolated = 1


class RegionDim(IntEnum):
    well = 1
    fracture = 2
    bulk = 3

class TopologyObject(IntEnum):
    node = 0
    segment = 1
    polygon = 2


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

class Curve(JsonData):
    def __init__():
        pass    

class Surface(GeoObject):
    
    def __init__(self, depth):
        self.transform = [[1, 0, 0], [0, 1, 0], [0, 0, depth]] 
        """Transform4x4Matrix"""
        self.grid = None
        """List of input grid 3DPoints. None for plane"""
        self.b_spline = None
        """B-spline,None for plane"""
        
    def get_depth(self):
        """Return surface depth in 0"""
        return self.transform[2][2]
        
    def __eq__(self, other):
        """operators for comparation"""
        if self.grid!=other.grid:
            return False
        if self.b_spline!=other.b_spline:
            return False
        for i in range(0, 3):
            for j in range(0, 3):
                if self.transform[i][j]!=other.transform[i][j]:
                    return False 
        return True



class Segment(JsonData):

    """Line object"""
    def __init__(self, config={}):
        self.node_ids  = ( int, int )
        """First point index"""
        """Second point index"""
        self.surface_idx = None
        """Surface index"""
        super().__init__(config)


class Polygon(JsonData):

    """Polygon object"""
    def __init__(self, config={}):
        self.segment_ids = [ int ]
        """List of segments index"""
        self.surface_id = int
        """Surface index"""
        super().__init__(config)



class Topology(JsonData):
    """Topological presentation of geometry objects"""

    def __init__(self, config={}):
        self.segments = [ ClassFactory(Segment) ]
        """List of topology segments (line)"""
        self.polygons = [ ClassFactory(Polygon) ]
        """List of topology polygons"""
        super().__init__(config)

class NodeSet(JsonData):

    """Set of point (nodes) with topology"""
    

    def __init__(self, config={}):
        self.topology_id = int
        """Topology index"""
        self.nodes = [ (float, float) ]
        """list of Nodes"""
        self.linked_node_set_id = None
        """node_set_idx of pair interface node set or None"""
        self.linked_node_ids = [ int ]
        """If linked_node_set is not None there is list od pair indexes of nodes or none
        if node has not pair"""
        super().__init__(config)

    def reset(self):
        """Reset node set"""
        self.nodes = []

    
class SurfaceNodeSet(JsonData):
    """Node set in space for transformation(x,y) ->(u,v). 
    Only for GL"""

    def __init__(self, config={}):
        self.nodeset_id = int
        """Node set index"""
        self.surface_id = int
        """Surface index"""
        super().__init__(config)

class InterpolatedNodeSet(JsonData):
    """Two node set with same Topology in space for transformation(x,y) ->(u,v).
    If both node sets is same, topology is vertical    
    Only for GL"""

    def __init__(self, config={}):
        self.source_nodeset_ids = ( int, int )
        """Top and bottom node set index"""
        self.surface_id = int
        """Surface index"""
        super().__init__(config)

class Region(JsonData):
    """Description of disjunct geometri area sorte by dimension (dim=1 well, dim=2 fracture, dim=3 bulk). """
    
    def __init__(self, config={}):
        self.color = ""
        """8-bite region color"""
        self.name = ""
        """region name"""
        self.dim = RegionDim
        """dimension (dim=1 well, dim=2 fracture, dim=3 bulk)"""
        self.topo_dim = TopologyObject

        self.boundary = False
        """Is boundary region"""
        self.not_used = False
        """is used - TODO: do we need it??"""
        self.mesh_step = float
        """mesh step"""
        self.brep_shape_ids = [ int ]
        """List of shape indexes - in BREP geometry """
        super().__init__(config)

class GeoLayer(JsonData):
    """Geological layers"""
    
    def __init__(self, config={}):
        self.name =  ""
        """Layer Name"""

        """Layer type :class:`geometry_files.geometry_structures.LayerType`"""
        self.top =  ClassFactory( [SurfaceNodeSet, InterpolatedNodeSet] )
        """Accoding topology type surface node set or interpolated node set"""
        
        self.bottom = ClassFactory( [SurfaceNodeSet, InterpolatedNodeSet] )
        """ optional, only for stratum type, accoding bottom topology 
        type surface node set or interpolated node set"""

        # assign regions to every topology object
        self.polygon_region_ids = [ int ]
        self.segment_region_ids = [ int ]
        self.node_region_ids = [ int ]

        super().__init__(config)

       # # set __class__ keys:
       #  if config['top_type'] is TopologyType.given:
       #      self.top = SurfaceNodeSet.__new__(SurfaceNodeSet)
       #  elif self.top_type is TopologyType.interpolated:
       #      self.top = InterpolatedNodeSet.__new__(InterpolatedNodeSet)
       #  self.top.deserialize(data["top"])
       #  if self.layer_type is LayerType.stratum:
       #      self.bottom_type = TopologyType(data["bottom_type"])
       #      if self.bottom_type is TopologyType.given:
       #          self.bottom = SurfaceNodeSet.__new__(SurfaceNodeSet)
       #      else:
       #          self.bottom = InterpolatedNodeSet.__new__(InterpolatedNodeSet)
       #      self.bottom.deserialize(data["bottom"])


class FractureLayer(GeoLayer):
    def __init__(self, config={}):
        super().__init__(config)

class StratumLayer(GeoLayer):
    def __init__(self, config={}):
        super().__init__(config)


class UserSupplement(JsonData):
    def __init__(self, config={}):
        self.last_node_set = 0
        """Last edited node set"""
        super().__init__(config)


class LayerGeometry(JsonData):

    def __init__(self, config={}):
        self.regions = [ ClassFactory(Region) ]

        #    [Region("#000000", "NONE_1D", 1),
        #     Region("#000000", "NONE_2D", 2),
        #     Region("#000000", "NONE_3D", 3)]
        """List of regions"""
        self.main_layers = [ ClassFactory( [StratumLayer, FractureLayer] ) ]
        """List of geological layers"""
        self.surfaces = [ ClassFactory(Surface) ]
        """List of B-spline surfaces"""
        self.curves = [ ClassFactory(Curve) ]
        """List of B-spline curves,"""
        self.plane_topologies = [ ClassFactory(Topology) ]
        """List of topologies"""
        self.node_sets = [ ClassFactory( NodeSet) ]
        """List of node sets"""
        self.supplement = ClassFactory( UserSupplement )
        """Addition data that is used for displaying in layer editor"""
        super().__init__(config)