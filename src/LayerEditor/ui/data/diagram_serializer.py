from geometry_files.geometry_factory import  GeometryFactory
from geometry_files.geometry import GeometrySer
from leconfig import cfg

class DiagramSerializer():
    """Class for diagram data serialization"""
  
    def __init__(self):        
        self.geometry = self._get_first_geometry()
        """Geometry faktory"""
        
    def _get_first_geometry(self):
        """Get emty geometry (new)"""
        gf = GeometryFactory()            
        tp_idx = gf.add_topology()
        ns_idx = gf.add_node_set(tp_idx)
        self.geometry = gf.geometry
        self.geometry.supplement = ns_idx
        cfg.node_set_idx = ns_idx
        
    def save(self, path=None):
        """Save diagram data to set file
        If path is not None, data is saved to new file from path"""
        assert path is not None or self.diagram.path is not None 
        if path is not None:
            cfg.path = path
        gf = GeometryFactory(self.geometry)            
        reader = GeometrySer(cfg.path)
        self._read_ns(ns_idx, gf)    
            
    def _read_ns(self, ns_idx, gf):
        reader = GeometrySer(cfg.path)
        assert ns_idx<len(self.geometry.node_sets)
        ns = self.geometry.node_sets[ns_idx]
        ns.reset()
        for point in self.diagram.points:
            gf.add_node(ns_idx, point.x, point.y)
        for line in self.diagram.lines:
            gf.add_segment( ns.topology_idx, self.diagram.points.index(line.p1), self.diagram.points.index(line.p2))
        gf.geometry.supplement = ns_idx
        errors = gf.check_file_consistency()
        if len(errors)>0:
            raise DiagramSerializerException("Some file consistency errors occure", errors)
        reader.write(gf.geometry)
    
    def load(self, ns_idx=None, path=None):
        """Load diagram data from set file"""
        if path is None:
            path = self.diagram.path
        else:
            self.diagram.path = path
        reader = GeometrySer(path)
        geometry =  reader.read()
        gf = GeometryFactory(geometry)
        errors = gf.check_file_consistency()        
        if len(errors)>0:
            raise DiagramSerializerException(
                "Some file consistency errors occure in {0}".format(self.diagram.path), errors)
        if ns_idx is None:
            ns_idx = gf.geometry.supplement            
        assert ns_idx<len(geometry.node_sets)        
        nodes = gf.get_nodes(ns_idx)
        self.diagram.reset_history()
        for node in nodes:
            self.diagram.add_point(node.x, node.y, 'Import point', None, True)
        segments = gf.get_segments(ns_idx)
        for segment in segments:
            self.diagram.join_line(self.diagram.points[segment.n1_idx], 
                self.diagram.points[segment.n2_idx], "Import line", None, True)
        self.diagram.node_set_idx = ns_idx

    
class DiagramSerializerException(Exception):
    def __init__(self, message, errors):
        super(DiagramSerializerException, self).__init__(message)
        self.errors = errors
