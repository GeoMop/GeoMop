"""Structures for Layer Geometry File"""

from .geometry_structures import LayerGeometry, NodeSet,  Topology, Segment
from .geometry_structures import InterpolatedNodeSet, SurfaceNodeSet, Surface
from .geometry_structures import Region, Polygon
import geometry_files.geometry_structures as gs

class GeometryFactory:
    """Class for creating geometry file from graphic representation of object"""
    
    def __init__(self, geometry=None):
        self.geometry =  geometry
        """Geometry data object"""
        if  geometry is None:
            default_regions = [
                Region(dict( color="#000000", name="NONE_1D", not_used=True, topo_dim=gs.TopologyDim.node)),
                Region(dict( color="#000000", name="NONE_2D", not_used=True, topo_dim=gs.TopologyDim.segment)),
                Region(dict( color="#000000", name="NONE_3D", not_used=True, topo_dim=gs.TopologyDim.polygon))
                ]
            self.geometry = LayerGeometry( dict(regions=default_regions) )
            
    def add_topology(self):
        """Add new topology and return its idx"""
        topology = Topology()
        self.geometry.topologies.append( topology)
        return len(self.geometry.topologies)-1
        
    def get_regions(self):
        """Get list of regions"""
        return self.geometry.regions
        
    def add_region(self, color, name, dim, step,  boundary, not_used):
        """Get list of regions"""
        region = Region(dict(color=color, name=name, topo_dim=dim-1, mesh_step=step, boundary=boundary, not_used=not_used))
        return self.geometry.regions.append(region)

    def get_topology(self, node_set_idx):
        """Get node set topology idx"""
        ns = self.geometry.node_sets[node_set_idx]
        return ns.topology_id
      
    def get_gl_topology(self, gl):
        """Get gl topology idx"""
        if type(gl.top) == InterpolatedNodeSet:
            return self.get_topology(gl.top.surf_nodesets[0].nodeset_id)
        elif type(gl.top) == SurfaceNodeSet:
            return self.get_topology(gl.top.nodeset_id)

    def add_topologies_to_count(self, i):
        """If need add topologes to end , end return needed topology"""
        while len(self.geometry.topologies)<=i:
            self.add_topology()
        return self.geometry.topologies[i]
        
    def get_interpolated_ns(self, ns1_idx, ns2_idx, surface_idx, surface_idx_1=None, surface_idx_2= None):
        """Create and return interpolated node set"""
        surface_idx_1 = surface_idx
        surface_idx_2 = surface_idx
        # TODO: make real surface nodesets and take them as parameters
        surf_nodesets = ( dict( nodeset_id=ns1_idx, surface_id=surface_idx_1 ), dict( nodeset_id=ns2_idx, surface_id=surface_idx_2 ) )
        ns = InterpolatedNodeSet(dict(surf_nodesets=surf_nodesets, surface_id=surface_idx) )
        return ns
        
    def get_surface_ns(self, ns_idx, surface_idx):
        """Create and return surface node set"""
        ns = SurfaceNodeSet(dict( nodeset_id=ns_idx, surface_id=surface_idx ))
        return ns
        
    def add_plane_surface(self, depth):
        """Add new main layer"""        
        surface = Surface.make_surface(depth)
        if len(self.geometry.surfaces)==0 or \
            surface!=self.geometry.surfaces[-1]:
            self.geometry.surfaces.append(surface)
        return len(self.geometry.surfaces)-1        
    
    def add_GL(self, name, type, regions_idx, top_type, top, bottom_type=None, bottom=None):
        """Add new main layer"""
        layer_class = [ gs.StratumLayer, gs.FractureLayer, gs.ShadowLayer ][type]


        iface_classes = [ SurfaceNodeSet, InterpolatedNodeSet ]
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

    def add_node_set(self, topology_idx):
        """Add new node set"""
        ns = NodeSet(dict(topology_id = topology_idx, nodes = [] ))
        self.geometry.node_sets.append(ns)
        return  len(self.geometry.node_sets)-1
        
    def reset(self):
        """Remove all data from base structure"""
        self.geometry.node_sets = []
        self.geometry.topologies = []
        self.geometry.surfaces = []
        self.geometry.regions = []
        self.geometry.layers = []
        self.geometry.curves = []
        
    def add_node(self, node_set_idx, x, y):
        """Add one node"""
        self.geometry.node_sets[node_set_idx].nodes.append( (x, y) )
        return len(self.geometry.node_sets[node_set_idx].nodes)-1
        
    def get_nodes(self, node_set_idx):
        """Get list of nodes"""
        return self.geometry.node_sets[node_set_idx].nodes
     
    def add_segment(self,topology_idx, n1_idx, n2_idx):
        """Add one segment"""
        segment = Segment(dict( node_ids=(n1_idx, n2_idx) ))
        self.geometry.topologies[topology_idx].segments.append(segment)

        return len(self.geometry.topologies[topology_idx].segments)-1

    def add_polygon(self,topology_idx, p_idxs):
        """Add one polygon"""
        poly = Polygon(dict( segment_ids=p_idxs ))
        self.geometry.topologies[topology_idx].polygons.append(poly)
        return len(self.geometry.topologies[topology_idx].polygons)-1
        
    def get_segments(self, node_set_idx):
        """Get list of segments"""
        ns =  self.geometry.node_sets[node_set_idx]
        return self.geometry.topologies[ns.topology_id].segments
        
    def  get_polygons(self, node_set_idx):
        """Get list of polygons"""
        ns =  self.geometry.node_sets[node_set_idx]
        return self.geometry.topologies[ns.topology_id].polygons
        
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
        
