from LayerEditor.ui.data.block_item import BlockItem
from LayerEditor.ui.tools.id_map import IdMap
from gm_base.geometry_files.format_last import InterpolatedNodeSet


class BlocksModel:
    def __init__(self, geo_model, le_model):
        self.blocks = IdMap()

        for top in geo_model.topologies:
            self.blocks.add(BlockItem(le_model.regions_model))

        for layer in geo_model.layers:
            if isinstance(layer.top, InterpolatedNodeSet):
                top_id = geo_model.node_sets[layer.top.surf_nodesets[0].nodeset_id].topology_id

            else:
                top_id = geo_model.node_sets[layer.top.nodeset_id].topology_id
            block = self.blocks.get(top_id)
            block.init_add_layer(layer, le_model)

        for block in self.blocks.values():
            block.gui_selected_layer = block.layers[0]

    def save(self):
        layers = []
        for block in self.blocks.values():
            layers.extend(block.save())
        return layers