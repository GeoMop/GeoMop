from PyQt5.QtCore import QObject, pyqtSignal

from LayerEditor.ui.data.abstract_model import AbstractModel
from LayerEditor.ui.data.block_layers_model import BlockLayersModel
from LayerEditor.ui.data.layer_item import LayerItem
from LayerEditor.ui.data.tools.selector import Selector
from LayerEditor.ui.tools import undo
from LayerEditor.ui.tools.id_map import IdMap
from gm_base.geometry_files.format_last import InterpolatedNodeSet


class BlocksModel(AbstractModel):
    def __init__(self):
        super(BlocksModel, self).__init__()
        self.gui_block_selector = None
        """ helper attribute, holds currently active block
            if curr_block was changed, signal value_changed is emitted in Selector"""

    @property
    def layers(self):
        """Returns all layer across all blocks sorted by elevation"""
        layers = []
        for block in self.items():
            layers.extend(block.get_sorted_layers())
        layers.sort(key=lambda x: (x.top_in.interface.elevation +
                                   x.bottom_in.interface.elevation) / 2 if x.is_stratum else x.top_in.interface.elevation,
                    reverse=True)
        return layers

    def deserialize(self, topologies, regions_model):
        with undo.pause_undo():
            for top in topologies:
                self.add(BlockLayersModel(regions_model))

    def deserialize_layers(self, geo_model, le_model):
        with undo.pause_undo():
            curr_decomp = le_model.decompositions_model[geo_model.supplement.last_node_set]
            for layer in geo_model.layers:
                LayerItem.create_from_data(layer, le_model)
                # layer is automatically added to its block

            for block in self.items():
                block.gui_layer_selector.value = block.get_sorted_layers()[0]

            self.gui_block_selector = Selector(curr_decomp.block)

    def get_sorted_blocks(self):
        return self.sorted_items(key=lambda x: x.get_sorted_layers()[0].top_in.interface.elevation,
                                 reverse=True)

    def validate_selectors(self):
        for block in self.items():
            block.validate_selectors()

        self.gui_block_selector.validate(self.get_sorted_blocks())

    def serialize(self):
        items = []
        for idx, item in enumerate(self.items()):
            items.extend(item.serialize())
            item.index = idx
        return items

    def remove(self, block):
        super(BlocksModel, self).remove(block)
        self.gui_block_selector.validate(self.get_sorted_blocks())


