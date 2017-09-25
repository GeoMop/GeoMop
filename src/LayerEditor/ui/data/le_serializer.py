from geometry_files import GeometryFactory, GeometrySer, LayerType, TopologyType
from .diagram_structures import Diagram
from .layers_structures import FractureInterface, Surface

class LESerializer():
    """Class for diagram data serialization"""
  
    def __init__(self, cfg):        
        self.geometry = self._get_first_geometry(cfg)
        """Geometry faktory"""
        
    def _get_first_geometry(self, cfg):
        """Get emty geometry (new)"""        
        cfg.diagrams = []
        cfg.layers.delete()
        lname = "New Layer"
        
        gf = GeometryFactory() 
        tp_idx = gf.add_topology()        
        ns_idx = gf.add_node_set(tp_idx)        
        gf.geometry.supplement.last_node_set = ns_idx
        cfg.diagrams = [Diagram(tp_idx, cfg.history)]
        cfg.diagram = cfg.diagrams[0]
        for region in gf.get_regions():
            cfg.add_region(region.color, region.name, region.topo_dim, region.mesh_step,
                region.boundary, region.not_used)
        cfg.add_shapes_to_region(False, 0, lname, tp_idx, [[], [], []])
        cfg.layers.add_interface(Surface("0"), False, None, ns_idx)
        cfg.layers.add_interface(Surface("100"), False)
        cfg.layers.add_layer(lname)
        cfg.layers.compute_composition()
        cfg.layers.set_edited_diagram(0)
        return gf.geometry
        
    def set_new(self, cfg):
        """Set new file"""
        cfg.release_all()
        self.geometry = self._get_first_geometry(cfg)        
        
    def save(self, cfg, path):
        """Save diagram data to set file"""
        # diagrams
        gf = GeometryFactory(self.geometry)
        gf.reset() 
        Diagram.make_map()       
        # regions
        for reg in cfg.diagram.regions.regions:
            gf.add_region(reg.color, reg.name, reg.dim, reg.mesh_step, reg.boundary, reg.not_used)
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
                last_ns_idx += 1
                ns_idx = gf.add_node_set(tp_idx)
                self._write_ns(cfg, ns_idx, gf)
            if layers_info.diagram_id2 is not None and \
                layers_info.diagram_id2>last_ns_idx:
                last_ns_idx += 1
                ns_idx = gf.add_node_set(tp_idx)
                self._write_ns(cfg, ns_idx, gf)
            if layers_info.stype1 is TopologyType.interpolated:
                surface_idx = gf.add_plane_surface(cfg.layers.interfaces[layers_info.layer_idx].surface)
                if layers_info.diagram_id2 is None:
                    id2 = layers_info.diagram_id1
                    surface2 = layers_info.surface1
                else:
                    id2 = layers_info.diagram_id2
                    surface2 = layers_info.surface2
                ns1 = gf.get_interpolated_ns(layers_info.diagram_id1, id2, surface_idx, 
                    layers_info.surface1, surface2)
                ns1_type = TopologyType.interpolated
            else:
                surface_idx = gf.add_plane_surface(cfg.layers.interfaces[layers_info.layer_idx].surface)
                ns1 = gf.get_surface_ns(layers_info.diagram_id1, surface_idx)
                ns1_type = TopologyType.given
            if layers_info.stype2 is TopologyType.interpolated:
                surface_idx = gf.add_plane_surface(cfg.layers.interfaces[layers_info.layer_idx+1].surface)
                if layers_info.diagram_id2 is None:
                    id2 = layers_info.diagram_id1
                    surface2 = layers_info.surface1
                else:
                    id2 = layers_info.diagram_id2
                    surface2 = layers_info.surface2
                ns2 = gf.get_interpolated_ns(layers_info.diagram_id1, id2, surface_idx, 
                    layers_info.surface1, surface2)
                ns2_type = TopologyType.interpolated
            else:
                surface_idx = gf.add_plane_surface(cfg.layers.interfaces[layers_info.layer_idx+1].surface)
                ns2 = gf.get_surface_ns(layers_info.diagram_id2, surface_idx)
                ns2_type = TopologyType.given         
            if layers_info.fracture_before is not None:
                regions = cfg.get_shapes_from_region(True, layers_info.layer_idx)
                gf.add_GL(layers_info.fracture_before.name, LayerType.fracture, regions, ns1_type, ns1)
            if layers_info.is_shadow:
                regions = [[], [], []]
                gf.add_GL("shadow", LayerType.shadow, regions, None, None)
            else:
                regions = cfg.get_shapes_from_region(False, layers_info.layer_idx)
                gf.add_GL(cfg.layers.layers[layers_info.layer_idx].name, LayerType.stratum, regions, ns1_type, ns1, ns2_type, ns2)
            if layers_info.fracture_after is not None:
                regions = cfg.get_shapes_from_region(True, layers_info.layer_idx+1)
                gf.add_GL(layers_info.fracture_after.name, LayerType.fracture, regions, ns2_type, ns2)
            if layers_info.fracture_own is not None:
                gf.add_topologies_to_count(layers_info.block_idx+1)
                if layers_info.fracture_own.fracture_diagram_id>last_ns_idx:
                    last_ns_idx += 1
                    ns_idx = gf.add_node_set(tp_idx+1)
                    self._write_ns(cfg, ns_idx, gf)
                surface_idx = gf.add_plane_surface(cfg.layers.interfaces[layers_info.layer_idx+1].surface)
                ns = gf.get_surface_ns(layers_info.fracture_own.fracture_diagram_id, surface_idx)
                regions = cfg.get_shapes_from_region(True, layers_info.layer_idx+1)
                gf.add_GL(layers_info.fracture_own.name, LayerType.fracture, regions, TopologyType.given, ns)
                layers_info.block_idx += 1
            layers_info = cfg.layers.get_next_layer_info(layers_info)
        gf.geometry.supplement.last_node_set = cfg.get_curr_diagram()
        Diagram.delete_map()
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
            gf.add_node(ns_idx, point.x, -point.y)
        if cfg.diagrams[ns_idx].topology_owner:
            for line in cfg.diagrams[ns_idx].lines:
                gf.add_segment( ns.topology_id, cfg.diagrams[ns_idx].points.index(line.p1),
                    cfg.diagrams[ns_idx].points.index(line.p2)) 
            for polygon in cfg.diagrams[ns_idx].polygons:
                p_idxs = []
                for line in polygon.lines:
                    p_idxs.append(cfg.diagrams[ns_idx].lines.index(line))                
                gf.add_polygon(ns.topology_id, p_idxs)
    
    def load(self, cfg, path):
        """Load diagram data from set file"""
        cfg.release_all()
        cfg.diagrams = []
        cfg.layers.delete()
        
        curr_topology = 0
        curr_block = 0
        # curr_topology and curr_block is for mapping topology to consistent line
        reader = GeometrySer(path)
        self.geometry =  reader.read()
        gf = GeometryFactory(self.geometry)
        errors = gf.check_file_consistency()        
        if len(errors)>0:
            raise LESerializerException(
                "Some file consistency errors occure in {0}".format(self.diagram.path), errors)
        for region in gf.get_regions():
            cfg.diagram.add_region(region.color, region.name, region.topo_dim, region.mesh_step,
                region.boundary, region.not_used)
        for i in range(0, len(gf.geometry.node_sets)):
            new_top = gf.geometry.node_sets[i].topology_id
            if new_top != curr_topology:
                new_top == curr_topology
                curr_block += 1                
            cfg.diagrams.append(Diagram(curr_block, cfg.history))
            self._read_ns(cfg, i, gf)  
        Diagram.make_revert_map()
        for i in range(0, len(gf.geometry.node_sets)):
            self._fix_polygon_map(cfg, i, gf)        
        ns_idx = 0   
        last_fracture = None
        last_stratum = None
        layer_id=0
        for i in range(0, len(gf.geometry.layers)):
            layer = gf.geometry.layers[i]
            regions = gf.get_GL_regions(i)
            if layer.layer_type is LayerType.shadow:
                cfg.add_shapes_to_region(False, layer_id, layer.name, -1, regions)
            else:
                cfg.add_shapes_to_region(layer.layer_type == LayerType.fracture, 
                    layer_id, layer.name, gf.get_gl_topology(layer), regions)            
            if layer.layer_type == LayerType.fracture:
                last_fracture = layer
                continue
            layer_id += 1
            # add interface
            surface_ = gf.geometry.surfaces[layer.top.surface_id]
            surface = Surface(surface_.depth, surface_.transform_xy, 
                surface_.transform_z, surface_.grid_file)
            if last_stratum is None:
                # first surface
                name = None
                id1 = None
                if last_fracture is not None:
                    name = last_fracture.name
                    last_fracture = None
                if layer.top_type is TopologyType.given:                
                    id1 = layer.top.nodeset_id
                cfg.layers.add_interface(surface, False, name, id1)
            elif last_stratum.bottom_type is TopologyType.interpolated and \
                layer.top_type is TopologyType.interpolated:                
                # interpolated non splitted interface
                if gf.get_gl_topology(last_stratum) == gf.get_gl_topology(layer):                    
                    if last_fracture is not None:
                        cfg.layers.add_interface(surface, False, last_fracture.name)
                        last_fracture = None
                    else:
                        cfg.layers.add_interface(surface, False)
                else:
                    if last_fracture is not None:
                        if last_fracture.top_type is TopologyType.interpolated:
                            if gf.get_gl_topology(last_stratum) == gf.get_gl_topology(last_fracture):
                                cfg.layers.add_interface(surface, True, last_fracture.name, None, None, FractureInterface.top)   
                            else:
                                cfg.layers.add_interface(surface, True, last_fracture.name, None, None, FractureInterface.bottom)   
                        else:
                            cfg.layers.add_interface(surface, True, last_fracture.name, None, None, FractureInterface.own, 
                                last_fracture.top.nodeset_id)
                        last_fracture = None    
                    else:
                        cfg.layers.add_interface(surface, True, last_fracture.name)
            elif last_stratum.bottom_type is TopologyType.given and \
                layer.top_type is TopologyType.given and \
                last_stratum.bottom.nodeset_id == layer.top.nodeset_id:
                # given non splitted interface
                if last_fracture is not None:
                    cfg.layers.add_interface(surface, False, last_fracture.name, layer.top.nodeset_id)
                    last_fracture = None
                else:
                    cfg.layers.add_interface(surface, False, None, layer.top.nodeset_id)
            else:
                # splitted surface
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
                        if last_stratum.bottom_type is TopologyType.given and \
                            last_fracture.top.nodeset_id == last_stratum.bottom.nodeset_id:
                            fracture_type = FractureInterface.top
                        elif layer.top_type is TopologyType.given and \
                            last_fracture.top.nodeset_id == layer.top.nodeset_id:
                            fracture_type = FractureInterface.bottom
                        else:
                            fracture_id = last_fracture.top.nodeset_id
                            fracture_type = FractureInterface.own
                    last_fracture = None
                id1 = None
                id2 = None
                if last_stratum.bottom_type is TopologyType.given:
                    id1 = last_stratum.bottom.nodeset_id
                if layer.top_type is TopologyType.given:    
                    id2 = layer.top.nodeset_id
                cfg.layers.add_interface(surface, True, fracture_name, id1, id2, fracture_type, fracture_id)
            # add layer
            cfg.layers.add_layer(layer.name, layer.layer_type is LayerType.shadow) 
            last_stratum = layer
        #last interface
        surface_ = gf.geometry.surfaces[last_stratum.bottom.surface_id]
        surface = Surface(surface_.depth, surface_.transform_xy, 
                surface_.transform_z, surface_.grid_file)
        id1 = None
        if last_stratum.bottom_type is TopologyType.given:
            id1 = last_stratum.bottom.nodeset_id
        if last_fracture is not None:
            cfg.layers.add_interface(surface, False, last_fracture.name, id1)
        else:
            cfg.layers.add_interface(surface, False, None, id1)        
        if gf.geometry.supplement.last_node_set < len(gf.geometry.node_sets):
            ns_idx = gf.geometry.supplement.last_node_set
        Diagram.delete_map()
        cfg.diagram = cfg.diagrams[ns_idx]    
        cfg.diagram.fix_topologies(cfg.diagrams)
        cfg.layers.compute_composition()
        cfg.layers.set_edited_diagram(ns_idx)
                
    def _read_ns(self, cfg, ns_idx, gf):
        """read  one node set from geometry file structure to diagram structure"""        
        nodes = gf.get_nodes(ns_idx)
        for node in nodes:
            x, y = node
            cfg.diagrams[ns_idx].add_point(x, -y, 'Import point', None, True)
            
        segments = gf.get_segments(ns_idx)
        for segment in segments:
            n1_idx, n2_idx = segment.node_ids
            cfg.diagrams[ns_idx].join_line(cfg.diagrams[ns_idx].points[n1_idx],
                cfg.diagrams[ns_idx].points[n2_idx], "Import line", None, True)

    def _fix_polygon_map(self, cfg, ns_idx, gf):
        """read  one node set from geometry file structure to diagram structure"""        
        polygons = gf.get_polygons(ns_idx)
        for i, poly in enumerate(polygons):
            cfg.diagrams[ns_idx].fix_polygon_map(i, poly.segment_ids)
    
class LESerializerException(Exception):
    def __init__(self, message, errors):
        super(LESerializerException, self).__init__(message)
        self.errors = errors
