"""Structures for Layer Geometry File"""

import sys
import os
geomop_src = os.path.join(os.path.split(os.path.dirname(os.path.realpath(__file__)))[0], "common")
sys.path.append(geomop_src)

from json_data import JsonData, IntEnum, ClassFactory
import geometry_files.layer_format_conversions as lfc


class LayerType(IntEnum):
    """Layer type"""
    stratum = 0
    fracture = 1
    shadow = 2


class TopologyType(IntEnum):
    given = 0
    interpolated = 1


class RegionDim(IntEnum):
    invalid = -2
    none = -1
    point = 0
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
        """List of segments index of the outer wire."""
        self.holes = []
        """List of lists of segments of hole's wires"""
        self.free_points = [ int ]
        """List of free points in polygon."""
        self.surface_id = None
        """Surface index"""
        super().__init__(config)

    def __eq__(self, other):
        return self.segment_ids == other.segment_ids \
            and self.holes == other.holes \
            and self.free_points == other.free_points \
            and self.surface_id == other.surface_id


class Topology(JsonData):
    """Topological presentation of geometry objects"""

    def __init__(self, config={}):
        self.segments = [ ClassFactory(Segment) ]
        """List of topology segments (line)"""
        self.polygons = [ ClassFactory(Polygon) ]
        """List of topology polygons"""
        super().__init__(config)

    def __eq__(self, other):
        return self.segments == other.segments \
            and self.polygons == other.polygons \



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
        """List of node IDs that match node ids in other nodesets on the same interface. I.e. arbitrary number of nodesets can be linkedIf linked_node_set is not None there is list od pair indexes of nodes or none
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
        self.dim = RegionDim.invalid
        """ Real dimension of the region. (0,1,2,3)"""
        #self.topo_dim = TopologyDim.invalid
        #"""For backward compatibility. Dimension (0,1,2) in Stratum layer: node, segment, polygon"""
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
        self.init_area = [(0.0, 0.0), (1.0, 1.0)]
        """Initialization area (polygon x,y coordinates)"""

        super().__init__(config)


class LayerGeometry(JsonData):

    def __init__(self, config={}):
        self.version = [0,4,0]
        """Version of the file format."""
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

    @staticmethod
    def fix_region_dim(region, extruded):
        assert region.topo_dim != TopologyDim.invalid
        assert not region.not_used
        if not hasattr(region, 'dim'):
            region.dim = RegionDim(region.topo_dim + extruded)
        assert region.dim == RegionDim(region.topo_dim + extruded)




    @staticmethod
    def fix_layer_regions(layer, regions):
        extruded = (layer.layer_type == LayerType.stratum)
        for reg_list in  [layer.polygon_region_ids, layer.segment_region_ids, layer.node_region_ids]:
            for i_reg in range(len(reg_list)):
                if reg_list[i_reg] > 2:
                    # Remove 2d and 3d None regions from the list.
                    reg_list[i_reg] -= 2
                    reg_idx = reg_list[i_reg]
                    LayerGeometry.fix_region_dim(regions[reg_idx], extruded)
                else:
                    reg_list[i_reg] = 0
        layer.polygon_region_ids.insert(0, 0)
        return layer


    @classmethod
    def convert(cls, other):
        none_region_json = dict(
            dim=RegionDim.none,
            name="NONE",
            not_used=True,
            boundary=None,
            mesh_step=None,
            color="##"
        )

        assert other.regions[0].not_used
        assert other.regions[1].not_used
        assert other.regions[2].not_used
        regions =  [ Region(none_region_json) ]
        for reg in  other.regions[3:]:
            regions.append(convert_json_data(reg))

        layers = [ LayerGeometry.fix_layer_regions(GeoLayer.convert(layer), regions) for layer in other.layers]

        inst = cls(dict(
            version = [0, 4, 9],
            regions = regions,
            layers = layers,
            surfaces = convert_object(other.surfaces),
            curves = convert_object(other.curves),
            topologies = convert_object(other.topologies),
            node_sets = convert_object(other.node_sets),
            supplement = convert_object(other.supplement)
        ))
        return inst

    # def convert    if self.version < [0, 5, 0]:
    #         # 0.4.0 to 0.5.0 conversion
    #         for layer in self.layers:
    #             # add None region for outer polygon, always with index 0
    #             assert self.regions[2].not_used
    #             layer.polygon_region_ids.insert(0, 2)
    #             layer.fix_region_dim(self.regions)
    #         # conversion of decomposistions is done when decompositions are reconstructed
    #
    #         self.version = [0, 5, 0]


# def convert_to(gs_obj, *args):
#     """
#     Convert from format version 0.4.0 to 0.4.9.
#     :param layers: LayersGeometry object in version 0.4.0.
#     :return: layers in version 0.4.9
#     """
#     assert  issubclass(gs_obj.__class__, JsonData)
#     geo_name = gs_obj.__class__.__name__
#     class_obj = getattr(sys.modules[__name__], geo_name)
#     geo_obj =  class_obj.convert(class_obj, gs_obj, *args)
#     return geo_obj

def convert_object(old_obj):
    return lfc.convert_object(sys.modules[__name__], old_obj)


def convert_json_data(old_obj):
    return lfc.convert_json_data(sys.modules[__name__], old_obj)


