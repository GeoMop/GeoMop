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

class TopologyDim(IntEnum):
    invalid = -1
    node = 0
    segment = 1
    polygon = 2


class Curve(JsonData):
    def __init__(self, config={}):
        super().__init__(config)

class SurfaceApproximation(JsonData):
    def __init__(self, config={}):
        self.b_spline = None
        """B-spline,None for plane"""


class Surface(JsonData):
    
    def __init__(self, config={}):
        self.transform_xy = 2*(3*(float,), )
        """Transformation matrix and shift in XY plane."""
        self.transform_z = 2*(float,)
        """Transformation in Z direction (scale and shift)."""
        self.depth = float
        """ Representative Z coord of the surface."""
        self.grid_file = ""
        """List of input grid 3DPoints. None for plane"""
        self.grid_polygon = 4*(2*(float,))
        """Vertices of the boundary polygon of the grid."""
        self.approximation = ClassFactory(SurfaceApproximation)
        super().__init__(config)

    @staticmethod
    def make_surface(depth):
        surf = Surface(dict(depth=depth))
        surf.transform_xy = 2*[3*[0.0]]
        surf.transform_xy[0][0] = surf.transform_xy[1][1] = 1.0
        surf.transform_z = [1.0, -depth]
        surf.approximation = None
        surf.grid_file = None

    def get_depth(self):
        """Return surface depth in 0"""
        return self.depth
        
    def __eq__(self, other):
        """operators for comparation"""
        if self.depth != other.depth:
            return False
        if self.transform_z != other.transform_z:
            return False
        if self.transform_xy != other.transform_xy:
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
    _not_serialized_attrs_ = ['interface_type']
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
    _not_serialized_attrs_ = ['interface_type']
    def __init__(self, config={}):
        self.surf_nodesets = ( ClassFactory([SurfaceNodeSet]), ClassFactory([SurfaceNodeSet]) )
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
        self.topo_dim = TopologyDim
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
    _not_serialized_attrs_ = ['layer_type']
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
    _not_serialized_attrs_ = ['layer_type', 'top_type']
    def __init__(self, config={}):
        super().__init__(config)
        self.layer_type = LayerType.fracture
        self.top_type = self.top.interface_type

class StratumLayer(GeoLayer):
    _not_serialized_attrs_ = ['layer_type', 'top_type','bottom_type']
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
        self.init_area = [(float, float)]
        """Initialization area (polygon x,y coordinates)"""
        
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

