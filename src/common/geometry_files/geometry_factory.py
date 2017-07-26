"""Structures for Layer Geometry File"""

from .geometry_structures import LayerGeometry, NodeSet,  Topology, Segment, Node, GL
from .geometry_structures import InterpolatedNodeSet, SurfaceNodeSet, Surface, TopologyType

class GeometryFactory:
    """Class for creating geometry file from graphic representation of object"""
    
    def __init__(self, geometry=None):
        self.geometry =  geometry
        """Geometry data object"""
        if  geometry is None:
            self.geometry = LayerGeometry()
            
    def add_topology(self):
        """Add new topology and return its idx"""
        topology = Topology()
        self.geometry.plane_topologies.append( topology)
        return len(self.geometry.plane_topologies)-1

    def get_topology(self, node_set_idx):
        """Get node set topology idx"""
        ns = self.geometry.node_sets[node_set_idx].topology_idx
        return ns.topology_idx
      
    def get_gl_topology(self, gl):
        """Get gl topology idx"""
        if gl.top_type is TopologyType.interpolated:
            return self.get_topology(gl.top.source_ns[0])
        return self.get_topology(gl.top.ns_idx)

    def add_topologies_to_count(self, i):
        """If need add topologes to end , end return needed topology"""
        while len(self.geometry.plane_topologies)<=i:
            self.add_topology()
        return self.geometry.plane_topologies[i]
        
    def get_interpolated_ns(self, ns1_idx, ns2_idx, surface_idx):
        """Create and return interpolated node set"""
        ns = InterpolatedNodeSet(ns1_idx, ns2_idx, surface_idx)
        return ns
        
    def get_surface_ns(self, ns_idx, surface_idx):
        """Create and return surface node set"""
        ns = SurfaceNodeSet(ns_idx, surface_idx)
        return ns
        
    def add_plane_surface(self, depth):
        """Add new main layer"""
        surface = Surface(depth)
        self.geometry.surfaces.append(surface)
        return len(self.geometry.surfaces)-1        
    
    def add_GL(self, name, type, top_type, top, bottom_type=None, bottom=None):
        """Add new main layer"""
        gl = GL(name, type, top_type, top, bottom_type, bottom)
        self.geometry.main_layers.append(gl)
        return  len(self.geometry.main_layers)-1

    def add_node_set(self, topology_idx):
        ns = NodeSet(topology_idx)
        self.geometry.node_sets.append(ns)
        return  len(self.geometry.node_sets)-1
        
    def reset(self):
        self.geometry.node_sets = []
        self.geometry.plane_topologies = []
        self.geometry.surfaces = []        
    
    def add_node(self,node_set_idx, x, y):
        self.geometry.node_sets[node_set_idx].nodes.append(Node(x, y))
        return len(self.geometry.node_sets[node_set_idx].nodes)-1
        
    def get_nodes(self, node_set_idx):
        return self.geometry.node_sets[node_set_idx].nodes
     
    def add_segment(self,topology_idx, n1_idx, n2_idx):
        self.geometry.plane_topologies[topology_idx].segments.append(
            Segment(n1_idx, n2_idx))
        return len(self.geometry.plane_topologies[topology_idx].segments)-1
        
    def get_segments(self, node_set_idx):
        ns =  self.geometry.node_sets[node_set_idx]
        return self.geometry.plane_topologies[ns.topology_idx].segments

    def check_file_consistency(self):
        """check created file consistency"""
        errors =  []
        for ns_idx in range(0, len(self.geometry.node_sets)):
            ns = self.geometry.node_sets[ns_idx]
            topology_idx = ns.topology_idx
            if topology_idx<0 or topology_idx>=len(self.geometry.plane_topologies):
                errors.append("Topology {0} is out of geometry topologies range 0..{1}".format(
                    str(topology_idx), str(len(self.geometry.plane_topologies)-1)))
            for segment in self.geometry.plane_topologies[topology_idx].segments:
                if segment.n1_idx<0 or segment.n1_idx>=len(ns.nodes):
                    errors.append(
                        "First segment point {0} is out of node_set {1} nodes range 0..{2}".format(
                        str(segment.n1_idx), str(ns_idx), str(ns.nodes)))
                if segment.n2_idx<0 or segment.n2_idx>=len(ns.nodes):
                    errors.append(
                        "Second point {0} is out of node_set {1} nodes range 0..{2}".format(
                        str(segment.n2_idx), str(ns_idx), str(ns.nodes)))
        return errors
