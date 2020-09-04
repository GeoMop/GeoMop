from LayerEditor.data.layer_geometry_serializer import LayerGeometrySerializer
from LayerEditor.ui.data.layer_model import LayerModel

from LayerEditor.ui.diagram_editor.diagram_scene import DiagramScene
from LayerEditor.ui.tools.selection import Selection

import gm_base.polygons.polygons_io as polygons_io
from gm_base.geometry_files.format_last import InterfaceNodeSet


class BlockModel:
    """Holds common data for a block of layers"""
    def __init__(self, le_data):
        self.le_data = le_data
        """Reference for LEData."""
        self.regions = self.le_data.regions
        """Reference to object which manages regions."""
        self.layers = []
        """list of layer in this block"""

        self.decomposition = None

        self.selection = Selection()
        """Selection is common for all layers in this block."""


    def init_add_layer(self, layer_data, geo_model):
        """Add layer while initializing (isn't undoable)."""
        self.layers.append(LayerModel(layer_data))

    def save(self, geo_model: LayerGeometrySerializer):
        """Save data from this block to LayerGeometryModel"""
        nodes, topology = polygons_io.serialize(self.decomposition)
        top_idx = geo_model.add_topology(topology)
        geo_model.add_node_set(top_idx, nodes)
        for layer in self.layers:
            geo_model.copy_GL(layer)
