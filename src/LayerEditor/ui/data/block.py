from LayerEditor.data.geometry_model import LayerGeometryModel
from LayerEditor.ui.data.layer import Layer

from LayerEditor.ui.diagram_editor.diagram_scene import DiagramScene
from LayerEditor.ui.tools.selection import Selection

import gm_base.polygons.polygons_io as polygons_io
from gm_base.geometry_files.format_last import InterfaceNodeSet


class Block:
    """Holds common data for a block of layers"""
    def __init__(self, top_idx, le_data):
        self.le_data = le_data
        """Reference for LEData."""
        self.top_idx = top_idx
        """Index of topology for this block."""
        self.ns_idx = None
        """Index of node set for this block (later should be in layer, maybe)."""
        self.regions = self.le_data.regions
        """Reference to object which manages regions."""
        self.layers = []
        """list of layer in this block"""
        self.selection = Selection(self)
        """Selection is common for all layers in this block."""

        self.diagram_scene = None
        """Graphics scene is bound to ns_idx (for one node set there is one graphics scene)."""

    def init_scene(self, nodes, topology):
        """Initial setup of scene and PolygonDecomposition."""
        decomp = polygons_io.deserialize(nodes, topology)
        self.diagram_scene = DiagramScene(self.selection,
                                          self.regions,
                                          decomp,
                                          self.le_data.diagram_view)


    def init_add_layer(self, layer_data, geo_model):
        """Add layer while initializing (isn't undoable)."""
        if self.ns_idx is None:
            if isinstance(layer_data.top, InterfaceNodeSet):
                self.ns_idx = layer_data.top.nodeset_id
                node_set = geo_model.get_node_set(self.ns_idx).nodes
                topology = geo_model.get_topologies()[self.top_idx]
                self.init_scene(node_set, topology)
            else:
                # TODO: Finish later when needed
                raise NotImplemented("Not sure how InterpolatedNodeSet works")

        self.layers.append(Layer(layer_data))
        self.ns_idx = layer_data.top.nodeset_id

    def save(self, geo_model: LayerGeometryModel):
        """Save data from this block to LayerGeometryModel"""
        nodes, topology = polygons_io.serialize(self.diagram_scene.decomposition)
        geo_model.add_node_set(self.top_idx, nodes)
        geo_model.add_topology(topology)
        for layer in self.layers:
            geo_model.copy_GL(layer)
