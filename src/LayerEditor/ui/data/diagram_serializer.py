from geometry_files.geometry_factory import  GeometryFactory
from geometry_files.geometry import GeometrySer
from .diagram_structures import Diagram

class DiagramSerializer():
    """Class for diagram data serialization"""
  
    def __init__(self, cfg):        
        self.geometry = self._get_first_geometry(cfg)
        """Geometry faktory"""
        
    def _get_first_geometry(self, cfg):
        """Get emty geometry (new)"""
        gf = GeometryFactory()            
        tp_idx = gf.add_topology()        
        ns_idx = gf.add_node_set(tp_idx)        
        gf.geometry.supplement.last_node_set = ns_idx
        cfg.diagrams = [Diagram()]
        cfg.diagram = cfg.diagrams[0]
        cfg.node_set_idx = ns_idx        
        cfg.diagrams[0].topology_idx = tp_idx
        return gf.geometry
        
    def save(self, cfg, path=None):
        """Save diagram data to set file
        If path is not None, data is saved to new file from path"""
        assert path is not None or self.diagram.path is not None 
        if path is not None:
            cfg.path = path
        gf = GeometryFactory(self.geometry)
        gf.reset_ns()
        for i in range(0, len(cfg.diagrams)):
            tp_idx = cfg.diagrams[i].topology_idx
            gf.add_topologies_to_count(tp_idx)
            ns_idx = gf.add_node_set(tp_idx)
            assert ns_idx==i
            self._write_ns(cfg, i, gf)
        gf.geometry.supplement.last_node_set = cfg.node_set_idx
        errors = gf.check_file_consistency()
        if len(errors)>0:
            raise DiagramSerializerException("Some file consistency errors occure", errors)
            
        reader = GeometrySer(cfg.path)
        reader.write(gf.geometry)
            
    def _write_ns(self, cfg, ns_idx, gf):
        """write one node set from diagram structure to geometry file structure"""
        assert ns_idx<len(self.geometry.node_sets)
        ns = self.geometry.node_sets[ns_idx]        
        for point in cfg.diagrams[ns_idx].points:            
            gf.add_node(ns_idx, point.x, point.y)
        for line in cfg.diagrams[ns_idx].lines:
            gf.add_segment( ns.topology_idx, cfg.diagrams[ns_idx].points.index(line.p1), 
                cfg.diagrams[ns_idx].points.index(line.p2))                
    
    def load(self, cfg, path):
        """Load diagram data from set file"""
        assert path is not None or self.diagram.path is not None 
        if path is None:
            path = self.path
        else:
            self.path = path
        reader = GeometrySer(path)
        self.geometry =  reader.read()
        gf = GeometryFactory(self.geometry)
        errors = gf.check_file_consistency()        
        if len(errors)>0:
            raise DiagramSerializerException(
                "Some file consistency errors occure in {0}".format(self.diagram.path), errors)
        self.diagrams = []    
        for i in range(0, len(gf.geometry.node_sets)):
            cfg.diagrams.append(Diagram())
            self._read_ns(cfg, i, gf)
        ns_idx = 0
        if gf.geometry.supplement.last_node_set < len(gf.geometry.node_sets):
            ns_idx = gf.geometry.supplement.last_node_set
        cfg.diagram = cfg.diagrams[ns_idx]
        cfg.node_set_idx = ns_idx        
                
    def _read_ns(self, cfg, ns_idx, gf):
        """read  one node set from geometry file structure to diagram structure""" 
        nodes = gf.get_nodes(ns_idx)
        for node in nodes:
            cfg.diagrams[ns_idx].add_point(node.x, node.y, 'Import point', None, True)        
        segments = gf.get_segments(ns_idx)
        for segment in segments:
            cfg.diagrams[ns_idx].join_line(cfg.diagrams[ns_idx].points[segment.n1_idx], 
                cfg.diagrams[ns_idx].points[segment.n2_idx], "Import line", None, True)   
        cfg.diagrams[ns_idx].topology_idx

    
class DiagramSerializerException(Exception):
    def __init__(self, message, errors):
        super(DiagramSerializerException, self).__init__(message)
        self.errors = errors
