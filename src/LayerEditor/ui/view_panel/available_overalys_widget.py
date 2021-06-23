import typing
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem

from LayerEditor.ui.view_panel.overlay_tree_item import OverlayTreeItem


def get_children(parent):
    return [parent.child(row) for row in range(parent.childCount())]


def delete_invalid_rows(parent_item: QTreeWidgetItem, model_items: list):
    list_items = get_children(parent_item)
    for list_item in list_items:
        delete = True
        for model_item in model_items:
            if list_item.data_item is model_item:
                delete = False
                break
        if delete:
            parent_item.removeChild(list_item)

def add_new_rows(parent_item: QTreeWidgetItem, model_items: list):
    list_items = get_children(parent_item)
    for row, model_item in enumerate(model_items):
        if len(list_items) == 0 or model_item is not list_items[0].data_item:
            block_item = OverlayTreeItem(model_item)
            parent_item.insertChild(row, block_item)
        else:
            list_items[0].setText(0, model_item.overlay_name)
            del list_items[0]

class AvailableOverlaysWidget(QTreeWidget):
    def __init__(self, blocks_model, surfaces_model, shapes_model, parent=None):
        super(AvailableOverlaysWidget, self).__init__(parent)
        self.blocks_model = blocks_model
        self.surfaces_model = surfaces_model
        self.shapes_model = shapes_model

        self.setColumnCount(1)
        self.setHeaderHidden(True)

        self.setDragEnabled(True)
        self.setDragDropMode(QTreeWidget.DragOnly)

        self.geometry_item = QTreeWidgetItem(["Geometry"])
        self.geometry_item.setFlags(self.geometry_item.flags() & ~Qt.ItemIsSelectable)
        self.addTopLevelItem(self.geometry_item)

        self.surfaces_item = QTreeWidgetItem(["Surfaces"])
        self.surfaces_item.setFlags(self.surfaces_item.flags() & ~Qt.ItemIsSelectable)
        self.addTopLevelItem(self.surfaces_item)

        self.shpfiles_item = QTreeWidgetItem(["Shpfiles"])
        self.shpfiles_item.setFlags(self.shpfiles_item.flags() & ~Qt.ItemIsSelectable)
        self.addTopLevelItem(self.shpfiles_item)

        self.init_overlays_items()

    def startDrag(self, supportedActions: typing.Union[QtCore.Qt.DropActions, QtCore.Qt.DropAction]) -> None:
        self.dragged_item = self.selectedItems()[0]
        super(AvailableOverlaysWidget, self).startDrag(supportedActions)
        self.dragged_item = None


    def init_overlays_items(self):
        delete_invalid_rows(self.geometry_item, self.blocks_model.items())
        add_new_rows(self.geometry_item, self.blocks_model.get_sorted_blocks())
        for row, block in enumerate(self.blocks_model.get_sorted_blocks()):
            self.geometry_item.child(row).setFlags(self.geometry_item.child(row).flags() & ~Qt.ItemIsSelectable)
            delete_invalid_rows(self.geometry_item.child(row), block.items())
            add_new_rows(self.geometry_item.child(row), block.get_sorted_layers())

        delete_invalid_rows(self.surfaces_item, self.surfaces_model.items())
        add_new_rows(self.surfaces_item, self.surfaces_model.items())

        delete_invalid_rows(self.shpfiles_item, self.shapes_model.shapes)
        add_new_rows(self.shpfiles_item, self.shapes_model.shapes)



