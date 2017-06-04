"""Structures for Layer Geometry File"""

from .geometry_structures import LayerGeometry, NodeSet,  Topology, Segment, Node

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

    def add_node_set(self, topology_idx):
        ns = NodeSet(topology_idx)
        self.geometry.node_sets.append(ns)
        return  len(self.geometry.node_sets)-1
        
    def reset_node_set(self, node_set_idx):
        self.geometry.node_sets[node_set_idx].reset()
    
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
