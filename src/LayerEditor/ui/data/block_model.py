from LayerEditor.ui.data.layer_model import LayerModel
from LayerEditor.ui.data.region import Region

from LayerEditor.ui.diagram_editor.diagram_scene import DiagramScene
from LayerEditor.ui.tools.id_map import IdMap, IdObject
from LayerEditor.ui.tools.selection import Selection

import gm_base.polygons.polygons_io as polygons_io
from gm_base.geometry_files.format_last import InterfaceNodeSet, NodeSet


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

    def init_regions_for_new_shape(self, shape):
        for layer in self.layers:
            if shape.shape_id in layer.shape_regions[shape.dim]:
                return
            else:
                region = layer.gui_selected_region
                dim = shape.dim
                if not layer.is_fracture:
                    dim += 1
                if region.dim == dim:
                    layer.set_region_to_shape(shape, layer.gui_selected_region)
                else:
                    layer.set_region_to_shape(shape, Region.none)

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

    def save(self, region_id_to_idx: dict):
        """Save data from this block to LayerGeometryModel"""
        nodes, topology = polygons_io.serialize(self.decomposition)

        layers = []
        for layer in self.layers:
            layers.append(layer.save(region_id_to_idx))
        return (nodes, topology, layers)

    # def set_region_to_selected_shapes(self, region: Region):
    #     """Sets regions of shapes for all layers in block."""
    #     for layer in self.layers:
    #         layer.set_region_to_selected_shapes(region)

