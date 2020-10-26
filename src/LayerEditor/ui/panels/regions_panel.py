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
        self.update_tabs()

        self.currentChanged.connect(self._layer_changed)
        self.le_model.gui_curr_block.selection.selection_changed.connect(self.selection_changed)

    def update_tabs(self):
        """
        Update tabs and its contents according to layer heads adaptor.
        :return:
        """
        with nosignal(self):
            while self.count() > 0:
                self.removeItem(0)
            names = self.le_model.gui_curr_block.layer_names
            for idx, layer_name in enumerate(names):
                tab_widget = RegionLayerTab(self.le_model, self.le_model.gui_curr_block.layers[idx], self)
                self.addItem(tab_widget, "")
                self._update_tab_head(tab_widget)
            # Update content.
        self.setCurrentIndex(self.le_model.get_curr_layer_index())

    def _update_tab_head(self, tab):
        """
        Update tab head, called by tab itself after change of region.
        :param tab:
        :return:
        """
        color = tab.region_color
        item_idx = self.le_model.gui_curr_block.layers.index(tab.layer)
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
        max_selected_dim = self.le_model.gui_curr_block.selection.max_selected_dim()
        if self.le_model.gui_curr_block.gui_selected_layer.is_stratum:
            max_selected_dim += 1
        dialog = AddRegionDlg(max_selected_dim, self.le_model.regions_model.get_region_names(), self)
        dialog_result = dialog.exec_()
        if dialog_result == QtWidgets.QDialog.Accepted:
            name = dialog.region_name.text()
            dim = dialog.region_dim.currentData()
            region = self.le_model.add_region(name, dim)
            self.current_tab._set_region_to_selected_shapes(region)

    def remove_region(self):
        """Remove region if it is not assigned to any no shapes"""
        reg = self.current_tab.curr_region
        self.le_model.delete_region(reg)

    @property
    def current_tab(self):
        """ Current Tab widget. """
        return self.widget(self.currentIndex())

    def _layer_changed(self):
        """item Changed handler"""
        self.le_model.gui_curr_block.gui_selected_layer = self.current_tab.layer
        self.le_model.invalidate_scene.emit()

    def selection_changed(self):
        selected = self.le_model.gui_curr_block.selection._selected
        if selected:
            for layer in self.le_model.gui_curr_block.layers:
                region = layer.get_shape_region(selected[0].dim, selected[0].shape_id)
                is_region_same = True
                for g_item in selected:
                    if region != layer.get_shape_region(g_item.dim, g_item.shape_id):
                        is_region_same = False
                        break
                if is_region_same:
                    layer.gui_selected_region = region
                else:
                    layer.gui_selected_region = RegionItem.none
            self.update_tabs()

