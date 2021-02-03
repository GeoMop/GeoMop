from PyQt5.QtCore import QObject, pyqtSignal

from LayerEditor.ui.data.block_item import BlockItem
from LayerEditor.ui.tools import undo
from LayerEditor.ui.tools.id_map import IdMap
from gm_base.geometry_files.format_last import InterpolatedNodeSet


class BlocksModel(QObject):
    layers_changed = pyqtSignal()
    def __init__(self, geo_model, le_model):
        super(BlocksModel, self).__init__()
        self.le_model = le_model
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
            block.gui_selected_layer = block.get_sorted_layers()[0]

    @property
    def layers(self):
        """Returns all layer across all blocks sorted by elevation"""
        layers = []
        for block in self.blocks.values():
            layers.extend(block.get_sorted_layers())
        layers.sort(key=lambda x: (x.top_in.interface.elevation +
                                   x.bottom_in.interface.elevation) / 2 if x.is_stratum else x.top_in.interface.elevation,
                    reverse=True)
        return layers

    def save(self):
        layers = []
        for layer in self.layers:
            layers.append(layer.save())
        return layers

    @undo.undoable
    def delete_block(self, block):
        self.blocks.remove(block)
        if self.le_model.gui_curr_block is block:
            self.le_model.gui_curr_block = list(self.blocks.values())[0]
        yield "Remove Block"
        self.blocks.add(block)

    @undo.undoable
    def add_block(self, block):
        self.blocks.add(block)
        yield "Add Block"
        self.blocks.remove(block)
