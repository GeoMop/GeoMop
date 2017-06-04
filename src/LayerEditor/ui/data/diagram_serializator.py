from .diagram_structures import *
from geometry_files.geometry_factory import  GeometryFactory
from geometry_files.geometry import GeometrySer

class DiagramSerializer():
    """Class for diagram data serialization"""
  
    def __init__(self, diagram):        
        self.diagram = diagram
        """Diagram data"""
        
    def save(self, path=None):
        """Save diagram data to set file
        If path is not None, data is saved to new file from path"""
        assert path is not None or self.diagram.path is not None 
        if path is not None:
            gf = GeometryFactory()
            tp_idx = gf.add_topology()
            ns_idx = gf.add_node_set(tp_idx)
            ns = gf.geometry.node_sets[ns_idx]
            self.diagram.path = path
            self.node_set_idx = ns_idx
            reader = GeometrySer(path)
        else:
            reader = GeometrySer(self.diagram.path)
            geometry =  reader.read()
            gf = GeometryFactory(geometry)
            assert ns_idx<len(geometry.node_sets)
            ns = geometry.node_sets[ns_idx]
            ns.reset()
        for point in self.diagram.points:
            gf.add_node(ns_idx, point.x(), point.y())
        for line in self.diagram.lines:
            gf.add_segment( ns.topology_idx, ns.nodes.index(line.p1), ns.nodes.index(line.p2))
        errors = gf.check_file_consistency()
        if len(errors)>0:
            raise DiagramSerializerException("Some file consistency errors occure", errors)
        reader.save(gf.geometry)
    
    def load(self, ns_idx=0):
        """Load diagram data from set file"""
        assert self.diagram.path is not None 
        reader = GeometrySer(self.diagram.path)
        geometry =  reader.read()
        gf = GeometryFactory(geometry)
        errors = gf.check_file_consistency()
        if len(errors)>0:
            raise DiagramSerializerException(
                "Some file consistency errors occure in {0}".format(self.diagram.path), errors)        
        assert ns_idx<len(geometry.node_sets)
        nodes = gf.get_nodes(ns_idx)
        self.diagram.reset_history()
        for node in nodes:
            self.diagram.add_point(node.x, node.y, 'Import point', None, True)
        segments = gf.get_segments(ns_idx)
        for segment in segments:
            self.diagram.join_line(self.diagram.points(segment.n1_idx), 
                self.diagram.points(segment.n2_idx), "Import line", None, True)

    
class DiagramSerializerException(PyperclipException):
    def __init__(self, message, errors):
        super(PyperclipWindowsException, self).__init__(message)
        self.errors = errors
