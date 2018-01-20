"""Structures for Layer Geometry File"""

from .geometry_structures import LayerGeometry, NodeSet,  Topology
from .geometry_structures import InterpolatedNodeSet, InterfaceNodeSet, Surface, Interface
from .geometry_structures import Region, RegionDim, StratumLayer
from .geometry_structures import FractureLayer, ShadowLayer
from .bspline_io import bs_zsurface_read, bs_zsurface_write

class GeometryFactory:
    """Class for creating geometry file from graphic representation of object"""
    
    def __init__(self, geometry = None):
        if geometry is None:
            self.geometry =  LayerGeometry()
            self.geometry.version = [0, 5, 0]
        else:
            self.geometry = geometry
        self.used_interfaces = {}

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
        
    def get_regions(self):
        """Get list of regions"""
        return self.geometry.regions
    
    def get_surfaces(self):
        """Get list of regions"""
        surfaces = []
        for surface in self.geometry.surfaces:
            s = surface.__dict__
            s['approximation'] = bs_zsurface_read(s['approximation'])                                                                  
            surfaces.append(s)
        return surfaces
        
    def add_region(self, color, name, dim, step,  boundary, not_used):
        """Get list of regions"""
        region = Region(dict(color=color, name=name, dim=dim, mesh_step=step, boundary=boundary, not_used=not_used))
        return self.geometry.regions.append(region)
        
    def add_surface(self, approximation, grid_file, name, xy_transform, quad):
        """Get list of regions"""
        
        surface = Surface(dict(approximation=bs_zsurface_write(approximation), 
            name=name, grid_file=grid_file, 
            xy_transform=xy_transform, quad=quad))
        return self.geometry.surfaces.append(surface)

    def get_topology(self, node_set_idx):
        """Get node set topology idx"""
        ns = self.geometry.node_sets[node_set_idx]
        return ns.topology_id

    # def set_topology(self, tp_idx, decomp):
    #     topology = self.add_topologies_to_count(tp_idx)
    #
    #     topology.segments = []
    #     for seg in decomp.segments.values():
    #         segment = Segment(dict(node_ids=(seg.vtxs[0].index, seg.vtxs[1].index)))
    #         topology.segments.append(segment)
    #
    #     topology.polygons = []
    #     for poly in decomp.polygons.values():
    #         polygon = Polygon()
    #         polygon.outer_wire = [seg.index for seg, side in poly.outer_wire.segments()]
    #         polygon.holes = []
    #         for hole in poly.holes.values():
    #             wire = [seg.index for seg, side in hole.segments()]
    #             polygon.holes.append(wire)
    #         polygon.free_points = []
    #         for pt in poly.free_points.values():
    #             polygon.free_points.append(pt.index)
    #         topology.polygons.append(polygon)

    def set_topology(self, tp_idx, topology):
        topology = self.add_topologies_to_count(tp_idx)
      
    def get_gl_topology(self, gl):
        """Get gl topology idx"""
        if type(gl.top) == InterpolatedNodeSet:
            return self.get_topology(gl.top.surf_nodesets[0].nodeset_id)
        elif type(gl.top) == InterfaceNodeSet:
            return self.get_topology(gl.top.nodeset_id)

    def add_topologies_to_count(self, i):
        """If need add topologes to end , end return needed topology"""
        while len(self.geometry.topologies)<=i:
            self.add_topology()
        return self.geometry.topologies[i]
        
    def get_interpolated_ns(self, ns1_idx, ns2_idx, interface_idx, interface_idx_1=None, interface_idx_2= None):
        """Create and return interpolated node set"""
        interface_idx_1 = interface_idx
        interface_idx_2 = interface_idx
        # TODO: make real surface nodesets and take them as parameters
        surf_nodesets = ( dict( nodeset_id=ns1_idx, interface_id=interface_idx_1 ), dict( nodeset_id=ns2_idx, interface_id=interface_idx_2 ) )
        ns = InterpolatedNodeSet(dict(surf_nodesets=surf_nodesets, interface_id=interface_idx) )
        return ns
        
    def get_interface_ns(self, ns_idx, interface_idx):
        """Create and return interface node set"""
        ns = InterfaceNodeSet(dict( nodeset_id=ns_idx, interface_id=interface_idx ))
        return ns

    def add_interface_plane(self, depth):
        """Add new main layer"""
        interface = Interface.make_interface(depth)
        self.geometry.interfaces.append(interface)
        return len(self.geometry.interfaces)-1

    def add_interface(self, interface):
        """Add new main layer""" 
        if interface in self.used_interfaces:
            return self.geometry.interfaces.index(self.used_interfaces[interface])
        new_interface = Interface({
            "depth":interface.depth, 
            "surface_id":interface.surface_id, 
            "transform_z":interface.transform_z})
        self.used_interfaces[interface] = new_interface
        self.geometry.interfaces.append(interface)
        return len(self.geometry.interfaces)-1

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

    def add_node_set(self, topology_idx, points=[]):
        """Add new node set"""
        ns = NodeSet(dict(topology_id = topology_idx, nodes = points ))
        self.geometry.node_sets.append(ns)
        return  len(self.geometry.node_sets)-1
        
    def reset(self):
        """Remove all data from base structure"""
        self.geometry.node_sets = []
        self.geometry.topologies = []
        self.geometry.surfaces = []
        self.geometry.interfaces = []
        self.geometry.regions = []
        self.geometry.layers = []
        self.geometry.curves = []
        self.used_interfaces = {}
        
    # def add_node(self, node_set_idx, x, y):
    #     """Add one node"""
    #     self.geometry.node_sets[node_set_idx].nodes.append( (x, y) )
    #     return len(self.geometry.node_sets[node_set_idx].nodes)-1
        
    def get_nodes(self, node_set_idx):
        """Get list of nodes"""
        return
     
    # def add_segment(self,topology_idx, n1_idx, n2_idx):
    #     """Add one segment"""
    #     segment = Segment(dict( node_ids=(n1_idx, n2_idx) ))
    #     self.geometry.topologies[topology_idx].segments.append(segment)
    #
    #     return len(self.geometry.topologies[topology_idx].segments)-1

    # def add_polygon(self,topology_idx, p_idxs):
    #     """Add one polygon"""
    #     poly = Polygon(dict( segment_ids=p_idxs ))
    #     self.geometry.topologies[topology_idx].polygons.append(poly)
    #     return len(self.geometry.topologies[topology_idx].polygons)-1
        
    # def get_segments(self, node_set_idx):
    #     """Get list of segments"""
    #     ns =  self.geometry.node_sets[node_set_idx]
    #     return self.geometry.topologies[ns.topology_id].segments
        
    # def  get_polygons(self, node_set_idx):
    #     """Get list of polygons"""
    #     ns =  self.geometry.node_sets[node_set_idx]
    #     return self.geometry.topologies[ns.topology_id].polygons
        
    def get_GL_regions(self, gl_idx):
        """Return lis of gl regions"""
        return [
                self.geometry.layers[gl_idx].node_region_ids,
                self.geometry.layers[gl_idx].segment_region_ids,
                self.geometry.layers[gl_idx].polygon_region_ids
            ]


    # TODO: move checks into clases ??

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
        
