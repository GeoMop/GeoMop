"""Model for Layer Geometry File"""
import json
import os

from gm_base.geometry_files import layers_io
from gm_base.geometry_files.format_last import LayerGeometry, NodeSet, Topology, LayerType, TopologyType
from gm_base.geometry_files.format_last import InterpolatedNodeSet, InterfaceNodeSet, Surface, Interface
from gm_base.geometry_files.format_last import Region, RegionDim, StratumLayer
from gm_base.geometry_files.format_last import FractureLayer, ShadowLayer
from gm_base.geometry_files.bspline_io import bs_zsurface_read, bs_zsurface_write
from gm_base.polygons import polygons_io


class LayerGeometryModel:
    """This class wraps data in LayerGeometry and provides methods for reading/modifying it"""

    def __init__(self, filename=None):
        """Creates new geometry or loads geometry from file if filename is specified"""
        if filename is None:
            self.geometry = LayerGeometry()
            self.geometry.version = [0, 5, 5]
        else:
            self.geometry = layers_io.read_geometry(filename)
            errors = self.check_file_consistency()
            if len(errors)>0:
                raise DataInconsistentException(
                    "Some file consistency errors occure in {0}".format(filename), errors)
        self.used_interfaces = {}
        self.base_dir = os.path.dirname(filename or "")


    # def make_rel_path(self, abs_path):
    #     rel_path = os.path.relpath(abs_path, self.base_dir)
    #     if (rel_path[0:2] == ".."):
    #         print("Warning: referenced file is out of the base directory, rel path: %s\n"%(rel_path))
    #     return rel_path

    # def make_abs_path(self, rel_path):
    #     return  os.path.normpath(os.path.join(self.base_dir, rel_path))

    def set_default_data(self):
        """Initialize with some default starting data"""
        self.geometry = LayerGeometry()
        self.geometry.version = [0, 5, 5]

        lname = "Layer_1"
        self.set_default()

        regions = ([], [], [])  # No node, segment, polygon or regions.
        ns_top = InterfaceNodeSet(dict( nodeset_id=0, interface_id=self.add_interface_plane(0.0) ))
        ns_bot = self.make_interpolated_ns(0, 0, self.add_interface_plane(-100.0))
        self.add_GL(lname, LayerType.stratum, regions,
                  TopologyType.given, ns_top,
                  TopologyType.interpolated, ns_bot)
        tp_idx = self.add_topology()
        ns_idx = self.add_node_set(tp_idx)
        self.geometry.supplement.last_node_set = ns_idx

    def set_default(self):
        default_regions = [                                                                                # Stratum layer
            Region(dict(color="##", name="NONE", not_used=True, dim=RegionDim.none))         # TopologyDim.polygon
        ]
        for reg in default_regions:
            self.geometry.regions.append(reg)

    def add_topology(self, topology=Topology()):
        """Add new topology and return its idx"""
        self.geometry.topologies.append( topology)
        return len(self.geometry.topologies)-1
    #
    # def get_regions(self):
    #     """Get list of regions"""
    #     return self.geometry.regions

    # def load_surfaces(self):
    #     """Generator for surfaces of the LayerGeometry."""
    #     for surface in self.geometry.surfaces:
    #         surface.grid_file = self.make_abs_path(surface.grid_file)
    #         surface.approximation = bs_zsurface_read(surface.approximation)
    #         yield surface
    #
    # def save_surfaces(self, surfaces):
    #     for s in surfaces:
    #         surface = Surface(dict(
    #             approximation=bs_zsurface_write(s.approximation),
    #             name=s.name,
    #             grid_file=self.make_rel_path(s.grid_file),
    #             approx_error=s.approx_error
    #         ))
    #         self.geometry.surfaces.append(surface)
    #
    # def add_region(self, color, name, dim, step,  boundary, not_used):
    #     """Get list of regions"""
    #     region = Region(dict(color=color, name=name, dim=dim, mesh_step=step, boundary=boundary, not_used=not_used))
    #     return self.geometry.regions.append(region)
    #
    #
    def get_topology(self, node_set_idx):
        """Get node set topology idx"""
        ns = self.geometry.node_sets[node_set_idx]
        return ns.topology_id

    def get_topologies(self):
        return self.geometry.topologies

    #
    # def set_topology(self, tp_idx, topology):
    #     topology = self.add_topologies_to_count(tp_idx)
    #
    def get_gl_topology(self, gl):
        """Get gl topology idx"""
        if type(gl) is ShadowLayer:
            return -1

        if type(gl.top) == InterpolatedNodeSet:
            return self.get_topology(gl.top.surf_nodesets[0].nodeset_id)
        elif type(gl.top) == InterfaceNodeSet:
            return self.get_topology(gl.top.nodeset_id)

    # def add_topologies_to_count(self, i):
    #     """If need add topologes to end , end return needed topology"""
    #     while len(self.geometry.topologies)<=i:
    #         self.add_topology()
    #     return self.geometry.topologies[i]
    #

    def make_interpolated_ns(self, ns1_idx, ns2_idx, interface_idx, interface_idx_1=None, interface_idx_2= None):
        """Create and return interpolated node set"""
        interface_idx_1 = interface_idx
        interface_idx_2 = interface_idx
        # TODO: make real surface nodesets and take them as parameters
        surf_nodesets = ( dict( nodeset_id=ns1_idx, interface_id=interface_idx_1 ), dict( nodeset_id=ns2_idx, interface_id=interface_idx_2 ) )
        ns = InterpolatedNodeSet(dict(surf_nodesets=surf_nodesets, interface_id=interface_idx) )
        return ns
    #
    # def get_interface_ns(self, ns_idx, interface_idx):
    #     """Create and return interface node set"""
    #     ns = InterfaceNodeSet(dict( nodeset_id=ns_idx, interface_id=interface_idx ))
    #     return ns
    #
    @staticmethod
    def make_interface(elevation):
        inter = Interface(dict(elevation=elevation, surface_id=None))
        inter.transform_z = [1.0, 0.0]
        return inter

    def add_interface_plane(self, elevation):
        """Add new main layer"""
        interface = self.make_interface(elevation)
        self.geometry.interfaces.append(interface)
        return len(self.geometry.interfaces)-1
    #
    # def add_interface(self, interface):
    #     """Add new main layer"""
    #     if interface in self.used_interfaces:
    #         return self.geometry.interfaces.index(self.used_interfaces[interface])
    #     if interface.surface_id is None:
    #         transform_z = [1.0, interface.elevation]
    #     else:
    #         transform_z = interface.transform_z
    #     new_interface = Interface({
    #         "elevation":interface.elevation,
    #         "surface_id":interface.surface_id,
    #         "transform_z":transform_z})
    #     self.used_interfaces[interface] = new_interface
    #     self.geometry.interfaces.append(new_interface)
    #     return len(self.geometry.interfaces)-1
    #
    #
    # def get_interface(self, iface_id):
    #     interface = self.geometry.interfaces[iface_id]
    #     if interface.surface_id is None:
    #         interface.transform_z = [1.0, 0.0]
    #     return interface
    #
    def add_GL(self, name, type, regions_idx, top_type, top, bottom_type=None, bottom=None):
        """Add new main layer"""
        layer_class = [ StratumLayer, FractureLayer, ShadowLayer ][type]


        iface_classes = [ InterfaceNodeSet, InterpolatedNodeSet ]
        top_interface = iface_classes[top_type]
        assert isinstance(top, top_interface)
        layer_config = dict(name=name, top=top)
        if bottom_type is not None:
            bot_interface = iface_classes[bottom_type]
            assert isinstance(bottom, bot_interface)
            layer_config['bottom'] = bottom

        gl = layer_class(layer_config)
        gl.node_region_ids = regions_idx[0]
        gl.segment_region_ids = regions_idx[1]
        gl.polygon_region_ids = regions_idx[2]
        self.geometry.layers.append(gl)

        return  len(self.geometry.layers)-1

    def copy_GL(self, layer):
        layer_data = layer.layer_data
        if isinstance(layer_data, StratumLayer):
            type = LayerType.stratum
            bottom_top = layer_data.bottom
            if isinstance(layer_data.bottom, InterfaceNodeSet):
                bottom_type = TopologyType.given
            else:
                bottom_type = TopologyType.interpolated
        elif isinstance(layer_data, FractureLayer):
            type = LayerType.fracture
            bottom_type = None
            bottom_top = None
        else:
            type = LayerType.shadow
            bottom_type = None
            bottom_top = None

        region_idx = (layer_data.node_region_ids,
                      layer_data.segment_region_ids,
                      layer_data.polygon_region_ids)
        if isinstance(layer_data.top, InterfaceNodeSet):
            top_type = TopologyType.given
        else:
            top_type = TopologyType.interpolated



        self.add_GL(layer_data.name,
                    type,
                    region_idx,
                    top_type,
                    layer_data.top,
                    bottom_type,
                    bottom_top)

    def add_node_set(self, topology_idx, points=[]):
        """Add new node set"""
        ns = NodeSet(dict(topology_id = topology_idx, nodes = points ))
        self.geometry.node_sets.append(ns)
        return  len(self.geometry.node_sets)-1

    # def reset(self):
    #     """Remove all data from base structure"""
    #     self.geometry.node_sets = []
    #     self.geometry.topologies = []
    #     self.geometry.surfaces = []
    #     self.geometry.interfaces = []
    #     self.geometry.regions = []
    #     self.geometry.layers = []
    #     self.geometry.curves = []
    #     self.used_interfaces = {}
    #
    #
    # def get_nodes(self, node_set_idx):
    #     """Get list of nodes"""
    #     return
    #
    #
    # # TODO: move checks into clases ??
    #
    def check_file_consistency(self):
        """check created file consistency"""
        errors =  []
        for ns_idx in range(0, len(self.geometry.node_sets)):
            ns = self.geometry.node_sets[ns_idx]
            topology_idx = ns.topology_id
            if topology_idx<0 or topology_idx>=len(self.geometry.topologies):
                errors.append("Topology {} is out of geometry topologies range 0..{}".format(
                    topology_idx, len(self.geometry.topologies)-1 ))
            for segment in self.geometry.topologies[topology_idx].segments:
                for i, node_id in enumerate(segment.node_ids):
                    if node_id<0 or node_id>=len(ns.nodes):
                        errors.append(
                            "Segment point {}:{} is out of node_set {} nodes range 0..{}".format(
                            i, node_id, ns_idx, len(ns.nodes)))
        # topology test
        curr_top = self.geometry.node_sets[0].topology_id
        used_top = [curr_top]
        for ns in self.geometry.node_sets:
            if curr_top != ns.topology_id:
                curr_top = ns.topology_id
                if curr_top in used_top:
                    errors.append("Topology {} is in more that one block.".format(curr_top))
                else:
                    used_top.append(curr_top)
        return errors

    # """
    # TODO:
    # - rename UserSupplement
    # - make it conforming to the JsonData approach
    # """
    # def get_shape_files(self):
    #     for shp in self.geometry.supplement.shps:
    #         shp['file'] = self.make_abs_path(shp['file'])
    #         yield shp
    #
    # def add_shape_file(self, shp):
    #     shp['file'] = self.make_rel_path(shp['file'])
    #     self.geometry.supplement.shps.append(shp.copy())
    #
    def save(self, path=""):
        errors = self.check_file_consistency()
        if len(errors) > 0:
            raise DataInconsistentException("Some file consistency errors occure", errors)
        if path:
            with open(path, 'w') as f:
                json.dump(self.geometry.serialize(), f, indent=4, sort_keys=True)
            return None
        else:
            return json.dumps(self.geometry.serialize(), indent=4, sort_keys=True)
    #
    # def load(self, cfg, path):
    #     geometry =  layers_io.read_geometry(path)
    #     self.create_geo_data(path, geometry, cfg)

    def get_node_set(self, ns_idx):
        return self.geometry.node_sets[ns_idx]

    def get_layers(self):
        return self.geometry.layers


class DataInconsistentException(Exception):
    def __init__(self, message, errors):
        super(DataInconsistentException, self).__init__(message)
        self.errors = errors
