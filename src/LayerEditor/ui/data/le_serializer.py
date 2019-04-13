import os
import json

from gm_base.geometry_files.format_last import  LayerType, TopologyType, InterpolatedNodeSet, InterfaceNodeSet
from gm_base.geometry_files.geometry_factory import GeometryFactory
from .diagram_structures import Diagram
from .layers_structures import FractureInterface
import gm_base.polygons.polygons_io as polygons_io
#import gm_base.geometry_files.format_last as gs
import gm_base.geometry_files.layers_io as layers_io


class LESerializer():
    """Class for diagram data serialization"""
  
    def __init__(self, cfg):
        self.set_new(cfg)
        """Geometry faktory"""

    def set_new(self, cfg):
        """Set new file"""
        first_geometry = self._get_first_geometry()
        Diagram.area.serialize(first_geometry.supplement.init_area)
        self.geometry_to_cfg("", first_geometry, cfg)

    def cfg_reset(self, cfg):
        #TODO: move definiftion and calls to cfg
        cfg.release_all()
        cfg.diagrams = []
        cfg.layers.delete()
        cfg.diagram = None

    def _get_first_geometry(self):
        lname = "Layer_1"
        gf = GeometryFactory(base_dir=None)
        gf.set_default()

        regions = ([], [], []) # No node, segment, polygon or regions.
        ns_top = gf.get_interface_ns(0, gf.add_interface_plane(0.0))
        ns_bot = gf.get_interpolated_ns(0, 0, gf.add_interface_plane(-100.0))
        gf.add_GL(lname, LayerType.stratum, regions,
                  TopologyType.given, ns_top,
                  TopologyType.interpolated, ns_bot)
        tp_idx = gf.add_topology()
        ns_idx = gf.add_node_set(tp_idx)
        gf.geometry.supplement.last_node_set = ns_idx
        return gf.geometry

    def load(self, cfg, path):
        geometry =  layers_io.read_geometry(path)
        self.geometry_to_cfg(path, geometry, cfg)

    def get_layer_nodesets(self, layer, top):
        """

        :param layer:
        :param side:
        :return:
        """
        if layer is None:
            return []
        else:
            if top:
                ns = layer.top
            else:
                ns = layer.bottom
            if type(ns) is InterfaceNodeSet:
                return [ns.nodeset_id]
            else:
                ns_ids = [ n.nodeset_id for n in ns.surf_nodesets]
                return ns_ids

    def eq_layer_topology(self, layer_a, layer_b):
        if layer_a is None or layer_b is None:
            return True
        return self.gf.get_gl_topology(layer_a) == self.gf.get_gl_topology(layer_b)

    def _get_ns_id(self, ns_set):
        if len(ns_set) == 1:
            return ns_set[0]
        else:
            return None

    def isec_ns(self, ns_a, ns_b):
        if not ns_a or not ns_b:
            return True
        return len(set(ns_a) & set(ns_b)) == 0

    def add_interface(self, gl_interface, top_layer, fracture,  bot_layer):
        fracture_name = None
        fracture_type = FractureInterface.none
        diagram_fr_id = None
        splitted = not self.eq_layer_topology(top_layer, bot_layer)


        top_nodesets = self.get_layer_nodesets(top_layer, top=False)
        top_diag_id = self._get_ns_id(top_nodesets)
        bot_nodesets = self.get_layer_nodesets(bot_layer, top=True)
        bot_diag_id = self._get_ns_id(bot_nodesets)

        # Topologies should be different iff layers have no common nodeset.
        have_isec = bool(top_nodesets) and bool(bot_nodesets) and self.isec_ns(top_nodesets, bot_nodesets)
        assert splitted == have_isec

        if fracture is not None:
            fracture_name = fracture.name
            if splitted:
                fr_nodesets = self.get_layer_nodesets(fracture, top=True)
                is_top_topology = self.isec_ns(fr_nodesets, top_nodesets)
                is_bot_topology = self.isec_ns(fr_nodesets, top_nodesets)

                assert is_top_topology == self.eq_layer_topology(fracture, top_layer)
                assert is_bot_topology == self.eq_layer_topology(fracture, bot_layer)
                assert not (is_top_topology  and is_bot_topology)
                if is_top_topology:
                    fracture_type = FractureInterface.top
                elif is_bot_topology:
                    fracture_type = FractureInterface.bottom
                else:
                    fracture_type = FractureInterface.own
                    diagram_fr_id = self._get_ns_id(fr_nodesets)
                    assert diagram_fr_id is not None

        # for add_interface single diagram ID must be always first one
        # TODO: Refactor data structures and have methods to add individual layers
        # then we can remove this complicated method.
        if not splitted and top_diag_id is None:
            top_diag_id = bot_diag_id
            bot_diag_id = None
        self.cfg.layers.add_interface(gl_interface, splitted,
                          fracture_name, top_diag_id, bot_diag_id, fracture_type, diagram_fr_id)

    def geometry_to_cfg(self, path, geometry, cfg):
        """Load diagram data from set file"""
        self.cfg_reset(cfg)
        self.cfg = cfg

        curr_topology = 0
        curr_block = 0
        # curr_topology and curr_block is for mapping topology to consistent line
        base_dir = os.path.dirname(path)
        gf = GeometryFactory(base_dir, geometry)
        self.gf = gf
        gf._base_dir = os.path.dirname(path)
        errors = gf.check_file_consistency()        
        if len(errors)>0:
            raise LESerializerException(
                "Some file consistency errors occure in {0}".format(geometry._base_file), errors)
        for reg_id, region in enumerate(gf.get_regions()):
            Diagram.add_region(region.color, region.name, reg_id, region.dim, region.mesh_step,
                region.boundary, region.not_used)

        cfg.layers.load_surfaces(gf.load_surfaces())

        for i in range(0, len(gf.geometry.node_sets)):
            new_top = gf.geometry.node_sets[i].topology_id
            if new_top != curr_topology:
                new_top == curr_topology
                curr_block += 1                
            cfg.diagrams.append(Diagram(curr_block, cfg.history))
            if len(cfg.diagrams)==1:
                cfg.diagram = cfg.diagrams[0]
            self._read_ns(cfg.diagrams[-1], i, gf)

        ns_idx = 0
        last_fracture = None
        last_stratum = None
        layer_id = 0

        for layer in gf.geometry.layers:
            regions = [
                layer.node_region_ids,
                layer.segment_region_ids,
                layer.polygon_region_ids]

            is_fracture_layer = layer.layer_type == LayerType.fracture
            topology_id = gf.get_gl_topology(layer)
            cfg.add_shapes_to_region(is_fracture_layer, layer_id, layer.name, topology_id, regions)

            if is_fracture_layer:
                last_fracture = layer
                continue
            layer_id += 1

            # add interface
            interface = gf.get_interface(layer.top.interface_id)
            self.add_interface(interface, last_stratum, last_fracture, layer)

            cfg.layers.add_layer(layer.name, layer.layer_type is LayerType.shadow)
            last_stratum = layer
            if last_fracture is not None:
                last_fracture = None


        if last_stratum:
            interface = gf.get_interface(last_stratum.bottom.interface_id)
            self.add_interface(interface, last_stratum, last_fracture, None)

        if gf.geometry.supplement.last_node_set < len(gf.geometry.node_sets):
            ns_idx = gf.geometry.supplement.last_node_set        
        Diagram.area.deserialize(gf.geometry.supplement.init_area)
        Diagram.zooming.deserialize(gf.geometry.supplement.zoom)
        Diagram.shp.deserialize(gf.get_shape_files())

        cfg.reload_surfaces(gf.geometry.supplement.surface_idx)
        cfg.diagram = cfg.diagrams[ns_idx]         
        cfg.diagram.fix_topologies(cfg.diagrams)
        cfg.layers.compute_composition()
        cfg.layers.set_edited_diagram(ns_idx)
                
    def _read_ns(self, diagram, ns_idx, gf):
        """read  one node set from geometry file structure to diagram structure"""
        geometry = gf.geometry
        ns = geometry.node_sets[ns_idx]
        nodes = ns.nodes
        topo_id = ns.topology_id
        topology = geometry.topologies[topo_id]

        for input_id, node in enumerate(nodes):
            x, y = node
            node_id = diagram.add_point_id(x, -y, input_id)
            assert node_id>=input_id

        decomp = polygons_io.deserialize(nodes, topology)
        diagram.import_decomposition(decomp)

    def save(self, cfg, path=""):
        lg = self.cfg_to_geometry(cfg, path)
        if path:
            with open(path, 'w') as f:
                json.dump(lg.serialize(), f, indent=4, sort_keys=True)
            return None
        else:
            return json.dumps(lg.serialize(), indent=4, sort_keys=True)


    def cfg_to_geometry(self, cfg, path):
        """Save diagram data to set file"""
        base_dir = os.path.dirname(path)
        gf = GeometryFactory(base_dir=base_dir)
        for reg in cfg.diagram.regions.regions.values():
            gf.add_region(reg.color, reg.name, reg.dim, reg.mesh_step, reg.boundary, reg.not_used)
        gf.save_surfaces(cfg.layers.surfaces)

            
        # layers
        layers_info = cfg.layers.get_first_layer_info()

        self._written_diagram_ids = set()
        self._tp_idx_to_out_tp_idx = {}
        while not layers_info.end:
            self._write_ns(layers_info.diag_top_id, cfg, gf)
            self._write_ns(layers_info.diag_bot_id, cfg, gf)

            if layers_info.stype1 is TopologyType.interpolated:
                interface_idx = gf.add_interface(cfg.layers.interfaces[layers_info.layer_idx])
                if layers_info.diag_bot_id is None:
                    id2 = layers_info.diag_top_id
                    surface2 = layers_info.surface1
                else:
                    id2 = layers_info.diag_bot_id
                    surface2 = layers_info.surface2
                ns1 = gf.get_interpolated_ns(layers_info.diag_top_id, id2, interface_idx,
                                             layers_info.surface1, surface2)
                ns1_type = TopologyType.interpolated
            else:
                interface_idx = gf.add_interface(cfg.layers.interfaces[layers_info.layer_idx])
                ns1 = gf.get_interface_ns(layers_info.diag_top_id, interface_idx)
                ns1_type = TopologyType.given

            if layers_info.stype2 is TopologyType.interpolated:
                interface_idx = gf.add_interface(cfg.layers.interfaces[layers_info.layer_idx + 1])
                if layers_info.diag_bot_id is None:
                    id2 = layers_info.diag_top_id
                    surface2 = layers_info.surface1
                else:
                    id2 = layers_info.diag_bot_id
                    surface2 = layers_info.surface2
                ns2 = gf.get_interpolated_ns(layers_info.diag_top_id, id2, interface_idx,
                                             layers_info.surface1, surface2)
                ns2_type = TopologyType.interpolated
            else:
                interface_idx = gf.add_interface(cfg.layers.interfaces[layers_info.layer_idx + 1])
                ns2 = gf.get_interface_ns(layers_info.diag_bot_id, interface_idx)
                ns2_type = TopologyType.given

            if layers_info.fracture_before is not None:
                regions = cfg.get_shapes_from_region(True, layers_info.layer_idx)
                gf.add_GL(layers_info.fracture_before.name, LayerType.fracture, regions, ns1_type, ns1)
            if layers_info.is_shadow:
                regions = [[], [], []]
                gf.add_GL("shadow", LayerType.shadow, regions, None, None)
            else:
                regions = cfg.get_shapes_from_region(False, layers_info.layer_idx)
                gf.add_GL(cfg.layers.layers[layers_info.layer_idx].name, LayerType.stratum, regions, ns1_type, ns1,
                          ns2_type, ns2)
            if layers_info.fracture_after is not None:
                regions = cfg.get_shapes_from_region(True, layers_info.layer_idx + 1)
                gf.add_GL(layers_info.fracture_after.name, LayerType.fracture, regions, ns2_type, ns2)
            if layers_info.fracture_own is not None:
                self._write_ns(layers_info.fracture_own.fracture_diagram_id, cfg, gf)
                interface_idx = gf.add_interface(cfg.layers.interfaces[layers_info.layer_idx + 1])
                ns = gf.get_interface_ns(layers_info.fracture_own.fracture_diagram_id, interface_idx)
                regions = cfg.get_shapes_from_region(True, layers_info.layer_idx + 1)
                gf.add_GL(layers_info.fracture_own.name, LayerType.fracture, regions, TopologyType.given, ns)
                layers_info.block_idx += 1
            layers_info = cfg.layers.get_next_layer_info(layers_info)
        gf.geometry.supplement.last_node_set = cfg.get_curr_diagram()
        gf.geometry.supplement.surface_idx = cfg.get_curr_surfaces()
        Diagram.area.serialize(gf.geometry.supplement.init_area)
        Diagram.zooming.serialize(gf.geometry.supplement.zoom)

        for shp in Diagram.shp.serialize():
            gf.add_shape_file(shp)

        errors = gf.check_file_consistency()
        if len(errors) > 0:
            raise LESerializerException("Some file consistency errors occure", errors)
        return gf.geometry

    def _write_ns(self, diagram_id, cfg, gf):
        """write one node set from diagram structure to geometry file structure"""
        if diagram_id is None or diagram_id in self._written_diagram_ids:
            return
        diagram = cfg.diagrams[diagram_id]
        self._written_diagram_ids.add(diagram_id)

        decomp = diagram.po.decomposition
        nodes, topology = polygons_io.serialize(decomp)
        if diagram.topology_owner:
            out_tp_idx = gf.add_topology(topology)
            self._tp_idx_to_out_tp_idx[diagram.topology_idx] = out_tp_idx
        else:
            out_tp_idx = self._tp_idx_to_out_tp_idx[diagram.topology_idx]
        gf.add_node_set(out_tp_idx, nodes)





class LESerializerException(Exception):
    def __init__(self, message, errors):
        super(LESerializerException, self).__init__(message)
        self.errors = errors
