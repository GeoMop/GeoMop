from enum import Enum

from PyQt5.QtWidgets import QTreeWidgetItem

from LayerEditor.ui.data.block_layers_model import BlockLayersModel
from LayerEditor.ui.data.layer_item import LayerItem
from LayerEditor.ui.data.shp_structures import ShapeItem
from LayerEditor.ui.data.surface_item import SurfaceItem
from LayerEditor.ui.tools.id_map import IdObject


class OverlayTreeItem(QTreeWidgetItem):
    def __init__(self, data_item):
        super(OverlayTreeItem, self).__init__([data_item.overlay_name])
        self.data_item = data_item
