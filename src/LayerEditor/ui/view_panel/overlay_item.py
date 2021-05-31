from enum import Enum

from PyQt5.QtWidgets import QTreeWidgetItem

from LayerEditor.ui.data.block_layers_model import BlockLayersModel
from LayerEditor.ui.data.layer_item import LayerItem
from LayerEditor.ui.data.shp_structures import ShapeItem
from LayerEditor.ui.data.surface_item import SurfaceItem
from LayerEditor.ui.tools.id_map import IdObject


class OverlayItem(QTreeWidgetItem):
    def __init__(self, label: str, data_item: IdObject, parent_widget):
        super(OverlayItem, self).__init__([label])
        self.data_item = data_item
        self.parent_widget = parent_widget

    def get_full_name(self):
        if isinstance(self.data_item, SurfaceItem):
            return f"Surf: {self.data_item.name}"
        elif isinstance(self.data_item, ShapeItem):
            return f"Shp: {self.data_item.file_name}"
        elif isinstance(self.data_item, BlockLayersModel):
            return f"Block {self.parent_widget.blocks_model.get_sorted_blocks().index(self.data_item)}"
        elif isinstance(self.data_item, LayerItem):
            self.parent().get_full_name()
            return f"{self.parent().get_full_name()} -> {self.data_item.name}"