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
    invalid = -1
    node = 0
    segment = 1
    polygon = 2


class Curve(JsonData):
    def __init__(self, config={}):
        super().__init__(config)

class Surface(JsonData):
    
    def __init__(self, config={}):
        self.transform = 4*(3*(float,), )
        """Transform4x4Matrix"""
        self.grid = None
        """List of input grid 3DPoints. None for plane"""
        self.b_spline = None
        """B-spline,None for plane"""
        super().__init__(config)

    @staticmethod
    def make_surface(depth):
        mat = 4*[3*[0]]
        mat[0][0] = mat[1][1] = mat[2][2] = 1.0
        mat[3][2] = depth

    def get_depth(self):
        """Return surface depth in 0"""
        return self.transform[3][2]
        
    def __eq__(self, other):
        """operators for comparation"""
        if self.grid!=other.grid:
            return False
        if self.b_spline!=other.b_spline:
            return False
        if self.transform != other.transform:
            return False
        return True



class Segment(JsonData):

    """Line object"""
    def __init__(self, config={}):
        self.node_ids  = ( int, int )
        """First point index"""
        """Second point index"""
        self.surface_id = None
        """Surface index"""
        super().__init__(config)


class Polygon(JsonData):

    """Polygon object"""
    def __init__(self, config={}):
        self.segment_ids = [ int ]
        """List of segments index"""
        self.surface_id = None
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
        self.linked_node_ids = [ ]
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
        self.interface_type = TopologyType.given


class InterpolatedNodeSet(JsonData):
    """Two node set with same Topology in space for transformation(x,y) ->(u,v).
    If both node sets is same, topology is vertical    
    Only for GL"""

    def __init__(self, config={}):
        self.surf_nodesets = ( SurfaceNodeSet, SurfaceNodeSet )
        """Top and bottom node set index"""
        self.surface_id = int
        """Surface index"""
        super().__init__(config)
        self.interface_type = TopologyType.interpolated



class Region(JsonData):
    """Description of disjunct geometri area sorte by dimension (dim=1 well, dim=2 fracture, dim=3 bulk). """
    
    def __init__(self, config={}):
        self.color = ""
        """8-bite region color"""
        self.name = ""
        """region name"""
        self.topo_dim = TopologyObject
        """dimension (0,1,2) in Stratum layer: well, fracture, bulk"""
        self.boundary = False
        """Is boundary region"""
        self.not_used = False
        """is used - TODO: do we need it??"""
        self.mesh_step = 1.0
        """mesh step"""
        self.brep_shape_ids = [ ]
        """List of shape indexes - in BREP geometry """
        super().__init__(config)

class GeoLayer(JsonData):
    """Geological layers"""
    
    def __init__(self, config={}):
        self.name =  ""
        """Layer Name"""

        self.top =  ClassFactory( [SurfaceNodeSet, InterpolatedNodeSet] )
        """Accoding topology type surface node set or interpolated node set"""
        
        # assign regions to every topology object
        self.polygon_region_ids = [ int ]
        self.segment_region_ids = [ int ]
        self.node_region_ids = [ int ]

        super().__init__(config)
        self.layer_type = LayerType.shadow




class FractureLayer(GeoLayer):
    def __init__(self, config={}):

        super().__init__(config)
        self.layer_type = LayerType.fracture
        self.top_type = self.top.interface_type

class StratumLayer(GeoLayer):
    def __init__(self, config={}):

        self.bottom = ClassFactory( [SurfaceNodeSet, InterpolatedNodeSet] )
        """ optional, only for stratum type, accoding bottom topology
        type surface node set or interpolated node set"""

        super().__init__(config)
        self.layer_type = LayerType.stratum
        self.top_type = self.top.interface_type
        self.bottom_type = self.bottom.interface_type


class ShadowLayer(GeoLayer):
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
        """List of regions"""
        self.layers = [ ClassFactory( [StratumLayer, FractureLayer] ) ]
        """List of geological layers"""
        self.surfaces = [ ClassFactory(Surface) ]
        """List of B-spline surfaces"""
        self.curves = [ ClassFactory(Curve) ]
        """List of B-spline curves,"""
        self.topologies = [ ClassFactory(Topology) ]
        """List of topologies"""
        self.node_sets = [ ClassFactory( NodeSet) ]
        """List of node sets"""
        self.supplement = UserSupplement()
        """Addition data that is used for displaying in layer editor"""
        super().__init__(config)

