from geometry_files.geometry_factory import  GeometryFactory
from geometry_files.geometry import GeometrySer
from geometry_files.geometry_structures import LayerType, TopologyType
from .diagram_structures import Diagram
from .layers_structures import FractureInterface

class LESerializer():
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
        cfg.diagrams = [Diagram(cfg.history)]
        cfg.diagram = cfg.diagrams[0]
        cfg.node_set_idx = ns_idx        
        cfg.diagrams[0].topology_idx = tp_idx
        cfg.layers.add_interface("0", False, None, ns_idx)
        cfg.layers.add_interface("100", False)
        cfg.layers.add_layer("New Layer")
        cfg.layers.compute_composition()
        return gf.geometry
        
    def save(self, cfg, path):
        """Save diagram data to set file"""
        # diagrams
        gf = GeometryFactory(self.geometry)
        gf.reset()        
        
        # layers
        layers_info = cfg.layers.get_first_layer_info()
        tp_idx = gf.add_topology()
        last_ns_idx = -1
        while not layers_info.end:
            if layers_info.block_idx > tp_idx:
                gf.add_topologies_to_count(layers_info.block_idx)
                tp_idx = layers_info.block_idx
            if layers_info.diagram_id1 is not None and \
                layers_info.diagram_id1>last_ns_idx:
                ns_idx = gf.add_node_set(tp_idx)
                self._write_ns(cfg, ns_idx, gf)
            if layers_info.diagram_id2 is not None and \
                layers_info.diagram_id2>last_ns_idx:
                ns_idx = gf.add_node_set(tp_idx)
                self._write_ns(cfg, ns_idx, gf)
            if layers_info.is_shadow:
                gf.add_GL("shadow", LayerType.shadow, None, None)
            else:                
                if layers_info.stype1 is TopologyType.interpolated:
                    surface_idx = gf.add_plane_surface(cfg.layers.interfaces[layers_info.layer_idx].depth)
                    ns1 = gf.get_interpolated_ns(layers_info.diagram_id1, layers_info.diagram_id2, surface_idx)
                    ns1_type = TopologyType.interpolated
                else:
                    surface_idx = gf.add_plane_surface(cfg.layers.interfaces[layers_info.layer_idx].depth)
                    ns1 = gf.get_surface_ns(layers_info.diagram_id1, surface_idx)
                    ns1_type = TopologyType.given
                if layers_info.stype2 is TopologyType.interpolated:
                    surface_idx = gf.add_plane_surface(cfg.layers.interfaces[layers_info.layer_idx+1].depth)
                    ns2 = gf.get_interpolated_ns(layers_info.diagram_id1, layers_info.diagram_id2, surface_idx)
                    ns2_type = TopologyType.interpolated
                else:
                    surface_idx = gf.add_plane_surface(cfg.layers.interfaces[layers_info.layer_idx+1].depth)
                    ns2 = gf.get_surface_ns(layers_info.diagram_id2, surface_idx)
                    ns2_type = TopologyType.given         
                if layers_info.fracture_before:
                    gf.add_GL(layers_info.fracture_before.name, LayerType.fracture, ns1_type, ns1)
                gf.add_GL(cfg.layers.layers[layers_info.layer_idx].name, LayerType.stratum, ns1_type, ns1, ns2_type, ns2)
                if layers_info.fracture_after:
                    gf.add_GL(layers_info.fracture_after.name, LayerType.fracture, ns2_type, ns2)
                if layers_info.fracture_own is not None:
                    gf.add_topologies_to_count(layers_info.block_idx+1)
                    if layers_info.fracture_own.fracture_diagram_id>last_ns_idx:
                        ns_idx = gf.add_node_set(tp_idx+1)
                        self._write_ns(cfg, ns_idx, gf)
                    surface_idx = gf.add_plane_surface(cfg.layers.interfaces[layers_info.layer_idx+1].depth)
                    ns = gf.get_surface_ns(layers_info.fracture_own.fracture_diagram_id, surface_idx)
                    gf.add_GL(layers_info.fracture_own.name, LayerType.fracture, TopologyType.given, ns)
                    layers_info.block_idx += 1
            layers_info = cfg.layers.get_next_layer_info(layers_info)
        gf.geometry.supplement.last_node_set = cfg.node_set_idx
        errors = gf.check_file_consistency()
        if len(errors)>0:
            raise LESerializerException("Some file consistency errors occure", errors)
            
        reader = GeometrySer(path)
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
            raise LESerializerException(
                "Some file consistency errors occure in {0}".format(self.diagram.path), errors)
        self.diagrams = []    
        for i in range(0, len(gf.geometry.node_sets)):
            cfg.diagrams.append(Diagram())
            self._read_ns(cfg, i, gf)        
        ns_idx = 0    
        last_stratum = None
        last_fracture = None
        for i in range(0, len(gf.geometry.main_layers)):
            layer = gf.geometry.main_layers[i]
            # add interface
            depth = gf.geometry.surfaces[layer.top.surface_idx].get_depth()
            if last_stratum.bottom_type is TopologyType.interpolated and \
                layer.top_type is TopologyType.interpolated:                
                if gf.get_gl_topology(last_stratum) == gf.get_gl_topology(layer):                    
                    if last_fracture is not None:
                        cfg.layers.add_interface(depth, False, last_fracture.name)
                        last_fracture = None
                    else:
                        cfg.layers.add_interface(depth, False)
                else:
                    if last_fracture is not None:
                        if last_fracture.top_type is TopologyType.interpolated:
                            if gf.get_gl_topology(last_stratum) == gf.get_gl_topology(last_fracture):
                                cfg.layers.add_interface(depth, True, last_fracture.name, None, None, FractureInterface.top)   
                            else:
                                cfg.layers.add_interface(depth, True, last_fracture.name, None, None, FractureInterface.bottom)   
                        else:
                            cfg.layers.add_interface(depth, True, last_fracture.name, None, None, FractureInterface.own, 
                                last_fracture.top.ns_idx)   
                        last_fracture = None    
                    else:
                        cfg.layers.add_interface(depth, True, last_fracture.name)
            elif last_stratum.bottom_type is TopologyType.given and \
                layer.top_type is TopologyType.given and \
                last_stratum.bottom.ns_idx == layer.top.ns_idx:   
                if last_fracture is not None:
                    cfg.layers.add_interface(depth, False, last_fracture.name, layer.top.ns_idx)
                    last_fracture = None
                else:
                    cfg.layers.add_interface(depth, False, None, layer.top.ns_idx)
            else:
                fracture_name = None
                fracture_type = FractureInterface.none
                fracture_id = None
                if last_fracture is not None:
                    fracture_name = last_fracture.name
                    if last_fracture.top_type is TopologyType.interpolated:
                        if gf.get_gl_topology(last_stratum) == gf.get_gl_topology(last_fracture):
                            fracture_type = FractureInterface.top
                        else:
                            fracture_type = FractureInterface.bottom   
                    else:
                        fracture_type = FractureInterface.own 
                        fracture_id = last_fracture.top.ns_idx   
                    last_fracture = None
                id1 = None
                id2 = None
                if last_stratum.bottom_type is TopologyType.given:
                    id1 = last_stratum.bottom.ns_idx
                if last_stratum.bottom_type is TopologyType.given:    
                    id2 = layer.top.ns_idx
                cfg.layers.add_interface(depth, True, fracture_name, id1, id2, fracture_type, fracture_id)
            # add layer
            if layer.layer_type == LayerType.fracture:
                last_fracture = layer
            else:
                cfg.layers.add_layer(layer.name, layer.layer_type is LayerType.shadow) 
                last_stratum = layer
        #last interface
        depth = gf.geometry.surfaces[last_stratum.bottom.surface_idx].get_depth()
        id1 = None
        if last_stratum.bottom_type is TopologyType.given:
            id1 = last_stratum.bottom.ns_idx
        if last_fracture is not None:
            cfg.layers.add_interface(depth, False, last_fracture.name, id1)
        else:
            cfg.layers.add_interface(depth, False, None, id1)        
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

    
class LESerializerException(Exception):
    def __init__(self, message, errors):
        super(LESerializerException, self).__init__(message)
        self.errors = errors
