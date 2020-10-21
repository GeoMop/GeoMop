from LayerEditor.ui.data.interface_node_set_item import InterfaceNodeSetItem
from LayerEditor.ui.data.interpolated_node_set_item import InterpolatedNodeSetItem
from LayerEditor.ui.data.layer_item import LayerItem
from LayerEditor.ui.data.region_item import RegionItem
from LayerEditor.ui.diagram_editor.graphics_items.gs_point import GsPoint
from LayerEditor.ui.diagram_editor.graphics_items.gs_polygon import GsPolygon
from LayerEditor.ui.diagram_editor.graphics_items.gs_segment import GsSegment

from LayerEditor.ui.tools.id_map import IdMap, IdObject
from LayerEditor.ui.tools.selection import Selection

from gm_base.geometry_files.format_last import InterfaceNodeSet, NodeSet, InterpolatedNodeSet, StratumLayer, \
    FractureLayer


class BlockItem(IdObject):
    """Holds common data for a block of layers"""
    def __init__(self, regions_model):
        super(BlockItem, self).__init__()
        """Reference for LEData."""
        self.regions_model = regions_model
        """Reference to object which manages regions."""
        self.layers = []
        """list of layer in this block"""
        self.layers_dict = IdMap()

        self.selection = Selection()
        """Selection is common for all layers in this block."""

        self.gui_selected_layer = None
        """Currently active layer. Region changes are made on this layer."""


    @property
    def decomposition(self):
        # This is going to be problem in future when there will be more editable layers in one block
        for layer in self.layers:
            if isinstance(layer.top_top, InterfaceNodeSetItem):
                return layer.top_top.decomposition

    @property
    def layer_names(self):
        for layer in self.layers:
            yield layer.name

    def make_node_set_from_data(self, le_model, node_set: [InterfaceNodeSet, InterpolatedNodeSet]):
        if isinstance(node_set, InterfaceNodeSet):
            le_model.decompositions_model.decomps[node_set.nodeset_id].helper_attr_block = self
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
        top_top = self.make_node_set_from_data(le_model, layer_data.top)
        if hasattr(layer_data, "bottom"):
            bottom_top = self.make_node_set_from_data(le_model, layer_data.bottom)
        else:
            bottom_top = None

        shape_regions = [{}, {}, {}]

        for shape_id, region_id in enumerate(layer_data.node_region_ids):
            shape_regions[0][shape_id] = self.regions_model.regions.get(region_id)

        for shape_id, region_id in enumerate(layer_data.segment_region_ids):
            shape_regions[1][shape_id] = self.regions_model.regions.get(region_id)

        for shape_id, region_id in enumerate(layer_data.polygon_region_ids):
            shape_regions[2][shape_id] = self.regions_model.regions.get(region_id)

        layer = LayerItem(self.selection,
                          layer_data.name,
                          top_top,
                          bottom_top,
                          shape_regions)
        self.layers.append(layer)
        self.layers_dict.add(layer)

        return layer

    def init_regions_for_new_shape(self, shape_dim, shape_id):
        for layer in self.layers:
            if shape_id in layer.shape_regions[shape_dim]:
                return
            else:
                region = layer.gui_selected_region
                dim = shape_dim
                if layer.is_stratum:
                    dim += 1
                if region.dim == dim:
                    layer.set_region_to_shape(shape_dim, shape_id, layer.gui_selected_region)
                else:
                    layer.set_region_to_shape(shape_dim, shape_id, RegionItem.none)

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

    def save(self):
        """Save data from this block to LayerGeometryModel"""
        layers = []
        for layer in self.layers:
            layers.append(layer.save())
        return layers
