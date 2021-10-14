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


class BlockLayersModel(IdObject):
    """Holds common data for a block of layers"""
    def __init__(self, regions_model):
        super(BlockLayersModel, self).__init__()
        """Reference for LEData."""
        self.regions_model = regions_model
        """Reference to object which manages regions."""
        self.layers_dict = IdMap()
        """All layer in this block"""

        self.selection = Selection()
        """Selection is common for all layers in this block."""

        self.gui_layer_selector = Selector(None)
        """Currently active layer. Region changes are made on this layer."""

    def __repr__(self):
        return f"BlockId {self.id}"

    def get_sorted_layers(self):
        return sorted(list(self.layers_dict.values()), key=lambda x: x.get_average_elevation(), reverse=True)

    def get_interface_node_sets(self):
        """Returns all InterfaceNodeSetItems which hold decompositions (neat ;) )"""
        node_sets = []
        for layer in self.layers_dict.values():
            if not layer.top_in.is_interpolated and layer.top_in not in node_sets:
                node_sets.append(layer.top_in)
        if layer.is_stratum and not layer.bottom_in.is_interpolated and layer.bottom_in not in node_sets:
            node_sets.append(layer.bottom_in)
        return node_sets

    @property
    def decomposition(self):
        # This is going to be problem in future when there will be more editable layers in one block
        for layer in self.layers_dict.values():
            if isinstance(layer.top_in, InterfaceNodeSetItem):
                return layer.top_in.decomposition

    @property
    def layer_names(self):
        for layer in self.get_sorted_layers():
            yield layer.name

    def make_node_set_from_data(self, le_model, node_set: [InterfaceNodeSet, InterpolatedNodeSet]):
        if isinstance(node_set, InterfaceNodeSet):
            le_model.decompositions_model.decomps[node_set.nodeset_id].block = self
            # I don't have any other sensible idea how to keep track of topology_id inside decomposition
            return InterfaceNodeSetItem(le_model.decompositions_model.decomps[node_set.nodeset_id],
                                        le_model.interfaces_model.interfaces[node_set.interface_id])
        else:
            interfaces = le_model.interfaces_model.interfaces
            decomp = le_model.decompositions_model.decomps[node_set.surf_nodesets[0].nodeset_id]
            itf = interfaces[node_set.surf_nodesets[0].interface_id]
            itf_node_set1 = InterfaceNodeSetItem(decomp, itf)
            decomp = le_model.decompositions_model.decomps[node_set.surf_nodesets[1].nodeset_id]
            itf = interfaces[node_set.surf_nodesets[1].interface_id]
            itf_node_set2 = InterfaceNodeSetItem(decomp, itf)

            itf = interfaces[node_set.interface_id]

            return InterpolatedNodeSetItem(itf_node_set1, itf_node_set2, itf)

    def init_add_layer(self, layer_data: [StratumLayer, FractureLayer], le_model):
        """Add layer while initializing (isn't undoable)."""
        top_in = self.make_node_set_from_data(le_model, layer_data.top)
        if hasattr(layer_data, "bottom"):
            bottom_in = self.make_node_set_from_data(le_model, layer_data.bottom)
        else:
            bottom_in = None

        shape_regions = [{}, {}, {}]

        for shape_id, region_id in enumerate(layer_data.node_region_ids):
            shape_regions[0][shape_id] = self.regions_model.regions.get(region_id)

        for shape_id, region_id in enumerate(layer_data.segment_region_ids):
            shape_regions[1][shape_id] = self.regions_model.regions.get(region_id)

        for shape_id, region_id in enumerate(layer_data.polygon_region_ids):
            shape_regions[2][shape_id] = self.regions_model.regions.get(region_id)

        layer = LayerItem(self,
                          layer_data.name,
                          top_in,
                          bottom_in,
                          shape_regions)
        self.layers_dict.add(layer)

        return layer

    def init_regions_for_new_shape(self, shape_dim, shape_id):
        for layer in self.layers_dict.values():
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
        self.gui_layer_selector.validate(self.get_sorted_layers())

        regions = list(self.regions_model.regions.values())
        for layer in self.layers_dict.values():
            layer.gui_region_selector.validate(regions)

    @undo.undoable
    def add_layer(self, new_layer: LayerItem):
        assert new_layer.block is None, f"Cannot add layer which belongs to block {new_layer.block}"
        new_layer.block = self
        self.layers_dict.add(new_layer)
        new_layer.block = self
        yield "Add Layer"
        self.delete_layer(new_layer)

    @undo.undoable
    def delete_layer(self, layer):
        old_block = layer.block
        assert layer.block is self, f'Trying to delete layer in block {str(layer.block)} from block {str(self)}'
        layer.block = None
        self.layers_dict.remove(layer)
        self.gui_layer_selector.validate(self.layers_dict.values())
        yield "Delete Layer"
        layer.block = old_block
        self.add_layer(layer)

