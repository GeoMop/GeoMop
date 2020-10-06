from LayerEditor.data.layer_geometry_serializer import LayerGeometrySerializer
from LayerEditor.ui.data.layer_model import LayerModel
from LayerEditor.ui.data.region import Region

from LayerEditor.ui.diagram_editor.diagram_scene import DiagramScene
from LayerEditor.ui.tools.id_map import IdMap, IdObject
from LayerEditor.ui.tools.selection import Selection

import gm_base.polygons.polygons_io as polygons_io
from gm_base.geometry_files.format_last import InterfaceNodeSet


class BlockModel(IdObject):
    """Holds common data for a block of layers"""
    def __init__(self, regions_model):
        super(BlockModel, self).__init__()
        """Reference for LEData."""
        self.regions_model = regions_model
        """Reference to object which manages regions."""
        self.layers = []
        """list of layer in this block"""
        self.layers_dict = IdMap()

        self._decomposition = None

        self.selection = Selection()
        """Selection is common for all layers in this block."""


        self.gui_selected_layer = None
        """Currently active layer. Region changes are made on this layer."""


    @property
    def decomposition(self):
        return self._decomposition

    def init_decomposition(self, decomp):
        self._decomposition = decomp
        for layer in self.layers:
            layer.decomposition = decomp

    @property
    def layer_names(self):
        for layer in self.layers:
            yield layer.name

    def init_add_layer(self, layer_data):
        """Add layer while initializing (isn't undoable)."""
        layer = LayerModel(self, self.regions_model.regions, layer_data)
        self.layers.append(layer)
        self.layers_dict.add(layer)

        self.gui_selected_layer = self.layers[0]

    #TODO: make this undoable
    def insert_layer(self, layer_data, index):
        pass
        # layer = LayerModel(self.decomposition, self.regions_model.regions)
        # self.layers.insert(layer)
        # self.layers_dict.add(layer)
        #
        #
        #
        # if len(self.layers) == 1:
        #     for shape in [*self.decomposition.points,
        #                   *self.decomposition.segments,
        #                   *self.decomposition.polygons]:
        #         shape.attr[layer] = shape.attr[self.layers[-2]]
        # else:
        #     for shape in [*self.decomposition.points,
        #                   *self.decomposition.segments,
        #                   *self.decomposition.polygons]:
        #         shape.attr[layer] = 0
        #
        # self.gui_selected_layer = self.layers[0]

    def save(self, geo_model: LayerGeometrySerializer, region_id_to_idx: dict):
        """Save data from this block to LayerGeometryModel"""
        nodes, topology = polygons_io.serialize(self.decomposition)
        top_idx = geo_model.add_topology(topology)
        geo_model.add_node_set(top_idx, nodes)
        for layer in self.layers:
            layer.save(geo_model, region_id_to_idx)

    # def set_region_to_selected_shapes(self, region: Region):
    #     """Sets regions of shapes for all layers in block."""
    #     for layer in self.layers:
    #         layer.set_region_to_selected_shapes(region)

