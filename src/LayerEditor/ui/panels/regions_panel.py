import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui

from .region_panel_tab import RegionLayerTab, nosignal
from ..data.region_item import RegionItem
from ..dialogs.regions import AddRegionDlg

class RegionsPanel(QtWidgets.QToolBox):
    """
    GeoMop regions panel.

    RegionPanel react to external changes:
    - selected region
    - selected shapes in diagram
    - change in available regions to select

    RegionPanel initiated changes:
    - set regions of selection
    - region color -> repaint shapes
    """

    def __init__(self, le_model, parent=None):
        """
        Inicialize window

        Args:
            parent (QWidget): parent window ( empty is None)
        """
        super().__init__(parent)

        self.le_model = le_model
        # Reference to adaptor for tab data.
        self.tabs = []
        # Tab widgets.

        self.currentChanged.connect(self._curr_layer_changed)
        self.le_model.gui_block_selector.value.selection.selection_changed.connect(self.selection_changed)
        self.le_model.region_list_changed.connect(self._update_region_list)

        self.update_tabs()

    def update_tabs(self):
        """
        Update tabs and its contents according to layer heads adaptor.
        :return:
        """

        with nosignal(self):
            while self.count() > 0:
                self.removeItem(0)
            layers = self.le_model.gui_block_selector.value.get_sorted_layers()
            for layer in layers:
                tab_widget = RegionLayerTab(self.le_model, layer, self)
                self.addItem(tab_widget, "")
                self._update_tab_head(tab_widget)
            # Update content.
        curr_block = self.le_model.gui_block_selector.value
        idx = curr_block.get_sorted_layers().index(curr_block.gui_layer_selector.value)
        self.setCurrentIndex(idx)

    def _update_region_list(self):
        for idx in range(self.count()):
            self.widget(idx)._update_region_list()

    def _update_tab_head(self, tab):
        """
        Update tab head, called by tab itself after change of region.
        :param tab:
        :return:
        """
        color = tab.region_color
        item_idx = self.le_model.gui_block_selector.value.get_sorted_layers().index(tab.layer)
        pixmap = QtGui.QPixmap(16, 16)
        pixmap.fill(color)
        iconPix = QtGui.QIcon(pixmap)
        self.setItemIcon(item_idx, iconPix)
        self.setItemText(item_idx, "{} ({})".format(tab._layer_name, tab.curr_region.name))

    def add_region(self):
        """
        Add new region to all combo and select it in current tab.
        Handle combo changed signal in current tab.
        """
        max_selected_dim = self.le_model.gui_block_selector.value.selection.max_selected_dim()
        if self.le_model.gui_block_selector.value.gui_layer_selector.value.is_stratum:
            max_selected_dim += 1
        dialog = AddRegionDlg(max_selected_dim, self.le_model.regions_model.get_region_names(), self)
        dialog_result = dialog.exec_()
        if dialog_result == QtWidgets.QDialog.Accepted:
            name = dialog.region_name.text()
            dim = dialog.region_dim.currentData()
            region = self.le_model.add_region(RegionItem(name=name, dim=dim))
            self.current_tab._set_region_to_selected_shapes(region)

    def remove_region(self):
        """Remove region if it is not assigned to any no shapes"""
        reg = self.current_tab.curr_region
        self.le_model.delete_region(reg)

    @property
    def current_tab(self):
        """ Current Tab widget. """
        return self.widget(self.currentIndex())

    def _curr_layer_changed(self):
        """item Changed handler"""
        self.le_model.gui_block_selector.value.gui_layer_selector.value = self.current_tab.layer
        self.le_model.invalidate_scene.emit()

    def selection_changed(self):
        selected = self.le_model.gui_block_selector.value.selection._selected
        if selected:
            for layer in self.le_model.gui_block_selector.value.get_sorted_layers():
                layer.gui_region_selector.value = layer.get_region_of_selected_shapes()
            self.update_tabs()

