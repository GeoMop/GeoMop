from LayerEditor.ui.data.abstract_item import AbstractItem
from LayerEditor.ui.data.abstract_model import AbstractModel
from LayerEditor.ui.data.interface_node_set_item import InterfaceNodeSetItem
from LayerEditor.ui.data.interpolated_node_set_item import InterpolatedNodeSetItem
from LayerEditor.ui.data.layer_item import LayerItem
from LayerEditor.ui.data.region_item import RegionItem
from LayerEditor.ui.data.tools.selector import Selector

from LayerEditor.ui.tools import undo
from LayerEditor.ui.tools.id_map import IdMap, IdObject
from LayerEditor.ui.tools.selection import Selection

from gm_base.geometry_files.format_last import InterfaceNodeSet, NodeSet, InterpolatedNodeSet, StratumLayer, \
    FractureLayer


class BlockLayersModel(AbstractModel, AbstractItem):
    """Holds common data for a block of layers"""
    def __init__(self, regions_model):
        super(BlockLayersModel, self).__init__()
        """Reference for LEData."""
        self.regions_model = regions_model
        """Reference to object which manages regions."""

        self.selection = Selection()
        """Selection is common for all layers in this block."""

        self.gui_layer_selector = Selector(None)
        """Currently active layer. Region changes are made on this layer."""

    @property
    def overlay_name(self):
        return f"Block {self.id}"

    def __repr__(self):
        return f"BlockId {self.id}"

    def get_sorted_layers(self):
        return self.sorted_items(key=lambda x: x.get_average_elevation(), reverse=True)

    def get_interface_node_sets(self):
        """Returns all InterfaceNodeSetItems which hold decompositions (neat ;) )"""
        node_sets = []
        for layer in self.items():
            if not layer.top_in.is_interpolated and layer.top_in not in node_sets:
                node_sets.append(layer.top_in)
        if layer.is_stratum and not layer.bottom_in.is_interpolated and layer.bottom_in not in node_sets:
            node_sets.append(layer.bottom_in)
        return node_sets

    @property
    def decomposition(self):
        # This is going to be problem in future when there will be more editable layers in one block
        return self.get_interface_node_sets()[0].decomposition

    @property
    def layer_names(self):
        """Return unordered set of layer names in block."""
        for layer in self.items():
            yield layer.name

    def init_add_layer(self, layer_data: [StratumLayer, FractureLayer], le_model):
        """Add layer while initializing (isn't undoable)."""
        layer = LayerItem.create_from_data(layer_data, le_model)
        self.add(layer)
        return layer

    def init_regions_for_new_shape(self, shape_dim, shape_id):
        for layer in self.items():
            if shape_id in layer.shape_regions[shape_dim]:
                return
            else:
                region = layer.gui_region_selector.value
                dim = shape_dim
                if layer.is_stratum:
                    dim += 1
                if region.dim == dim:
                    layer.set_region_to_shape(shape_dim, shape_id, layer.gui_region_selector.value)
                else:
                    layer.set_region_to_shape(shape_dim, shape_id, RegionItem.none)

    def validate_selectors(self):
        self.gui_layer_selector.make_valid(self.get_sorted_layers())

        regions = list(self.regions_model.items())
        for layer in self.items():
            layer.gui_region_selector.make_valid(regions)

    @undo.undoable
    def add(self, new_layer: LayerItem):
        new_layer = self.collection.add(new_layer)
        print(f"add layer {new_layer.id} to block {self.id}")
        yield "Add Layer"
        self.remove(new_layer)

    @undo.undoable
    def remove(self, layer):
        print(f"remove layer {layer.id} from block {self.id}")
        self.collection.remove(layer)
        self.gui_layer_selector.make_valid(list(self.items()))
        yield "Delete Layer"
        self.add(layer)

