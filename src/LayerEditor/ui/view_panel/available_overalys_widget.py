import typing
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem

from LayerEditor.ui.view_panel.overlay_item import OverlayItem


class AvailableOverlaysWidget(QTreeWidget):
    def __init__(self, blocks_model, surfaces_model, shapes_model, parent=None):
        super(AvailableOverlaysWidget, self).__init__(parent)
        self.blocks_model = blocks_model
        self.surfaces_model = surfaces_model
        self.shapes_model = shapes_model

        self.setColumnCount(1)

        self.setDragEnabled(True)
        self.setDragDropMode(QTreeWidget.DragOnly)

        self.init_overlays_items()

    def startDrag(self, supportedActions: typing.Union[QtCore.Qt.DropActions, QtCore.Qt.DropAction]) -> None:
        self.dragged_item = self.selectedItems()[0]
        super(AvailableOverlaysWidget, self).startDrag(supportedActions)
        self.dragged_item = None

    def init_overlays_items(self):
        geometry_item = QTreeWidgetItem(["Geometry"])
        geometry_item.setFlags(geometry_item.flags() & ~Qt.ItemIsSelectable)
        self.addTopLevelItem(geometry_item)
        index = 1
        for block in self.blocks_model.get_sorted_blocks():
            block_item = OverlayItem(f"Block {index}", block, self)
            geometry_item.addChild(block_item)
            index += 1
            for layer in block.items():
                block_item.addChild(OverlayItem(layer.name, layer, self))

        surfaces_item = QTreeWidgetItem(["Surfaces"])
        surfaces_item.setFlags(surfaces_item.flags() & ~Qt.ItemIsSelectable)
        self.addTopLevelItem(surfaces_item)
        for surface in self.surfaces_model.items():
            surfaces_item.addChild(OverlayItem(surface.name, surface, self))

        shpfiles_item = QTreeWidgetItem(["Shpfiles"])
        shpfiles_item.setFlags(shpfiles_item.flags() & ~Qt.ItemIsSelectable)
        self.addTopLevelItem(shpfiles_item)
        for shpfile in self.shapes_model.shapes:
            shpfiles_item.addChild(OverlayItem(shpfile.file_name, shpfile, self))



