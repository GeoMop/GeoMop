from contextlib import contextmanager
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
from bgem.external import undo

import gm_base.icon as icon
from gm_base.geomop_dialogs import GMErrorDialog
from ..data.region_item import RegionItem
from ..dialogs.regions import AddRegionDlg
from ..helpers.combo_box import ComboBox


@contextmanager
def nosignal(qt_obj):
    """
    Context manager for blocking signals inside some signal handlers.
    TODO: move to some common module
    """
    qt_obj.blockSignals(True)
    yield qt_obj
    qt_obj.blockSignals(False)


class BlockLayerHeads(QtCore.QObject):
    """
    Adaptor to access layer names and
    to store currently selected regions and layers.
    TODO: refactor to the class for supplement GUI states.
    """

    region_changed = QtCore.pyqtSignal()
    # current region in current tab has changed
    selected_layer_changed = QtCore.pyqtSignal()
    # current tab in RegionPanel has changed.
    region_list_changed = QtCore.pyqtSignal()


    def __init__(self, block):
        """
        Constructor.
        :param layers_geometry: LEConfig class.
        """
        super(BlockLayerHeads, self).__init__()

        self.block = block
        """Data object used to retrieve data"""

    def select_regions(self, region_dict):
        """
        Update dictionary assigning selected region id to the layer id.
        :param region_dict:
        :return:
        """
        # assert layer_id in self._selected_regions
        assert False, "Not refactored"
        self._selected_regions.update(region_dict)
        self.region_changed.emit()

    def select_layer(self, layer):
        """ Select actual layer tab."""
        self.block.gui_selected_layer = layer

    def add_region(self, name, dim):
        """ Add new region according to the provided data from the current tab and select it."""
        with undo.group("Add new region"):
            reg = self.regions_model.add_region(name, dim)
            self.block.gui_selected_layer.set_gui_selected_region(reg)
        self.region_list_changed.emit()
        self.region_changed.emit()
        return reg

    def remove_region(self, reg):
        """Remove the region."""
        self.regions_model.delete_region(reg)
        self.region_list_changed.emit()

    def max_selected_dim(self):
        """Maximal object dimension within the current selection.
        TODO: better check for the fracture layer.
        """
        max_selected_dim = self.block.selection.max_selected_dim()
        if self.block.gui_selected_layer.is_stratum:
            max_selected_dim += 1
        return max(max_selected_dim, 0)

    @property
    def region_names(self):
        """ List of unique region names."""
        return [reg.name for reg in self.block.regions_model.regions.values()]

    @property
    def regions_model(self):
        """ Regions object. """
        return self.block.regions_model

    @property
    def selected_region(self):
        """ Current region of the current layer."""
        assert False, "Not refactored"
        region_id = self._selected_regions[self.current_layer_id]
        return self.regions_model.regions_model[region_id]

    @property
    def current_layer_idx(self):
        """ Layer ID for current teb in Region Panel."""
        return self.block.layers.index(self.block.gui_selected_layer)

    @property
    def layer_names(self):
        """
        Return list of layer names
        :return: [ layer_name,...]
        """
        return self.block.layer_names

    @property
    def selected_regions(self):
        """
        Return list of selected region IDs.
        :return: [ (layer_id, region_id), ... ]
        """
        assert False, "Not refactored"
        return self._selected_regions


class RegionsPanel(QtWidgets.QToolBox):
    """
    GeoMop regions panel.

    Panel provides access to two sort of data:
    1. Data about individual regions shared by whole geometry.
    2. Data about currently selected regions and layer names for individual layers.

    RegionPanel react to external changes:
    - selected region
    - current block/topology
    - change in available regions to select

    RegionPanel initiated changes:
    - set regions of selection
    - region color -> repaint shapes


    pyqtSignals:
        * :py:attr:`regionChanged() <regionChanged>`
    """
    regions_changed = QtCore.pyqtSignal()

    # Emitted when color of some region has changed.

    def __init__(self, le_data, parent=None):
        """
        Inicialize window

        Args:
            parent (QWidget): parent window ( empty is None)
        """
        super().__init__(parent)

        self.layer_heads = BlockLayerHeads(le_data.gui_curr_block)
        # Reference to adaptor for tab data.
        self.tabs = []
        #  Tab widgets.
        self.update_tabs()

        self.currentChanged.connect(self._layer_changed)
        self.layer_heads.block.selection.selection_changed.connect(self.selection_changed)

    @property
    def regions(self):
        """ Regions data object. """
        assert False, "Not refactored"
        return self.layer_heads.regions_model

    def update_tabs(self):
        """
        Update tabs and its contents according to layer heads adaptor.
        :return:
        """
        with nosignal(self):
            while self.count() > 0:
                self.removeItem(0)
            names = self.layer_heads.layer_names
            for idx, layer_name in enumerate(names):
                tab_widget = RegionLayerTab(self.layer_heads, self.layer_heads.block.layers[idx], self)
                self.addItem(tab_widget, "")
                tab_widget.reinit(layer_name)
            # Update content.
        self.setCurrentIndex(self.layer_heads.current_layer_idx)

    def _update_tab_head(self, tab):
        """
        Update tab head, called by tab itself after change of region.
        :param tab:
        :return:
        """
        color = tab.region_color
        item_idx = self.layer_heads.block.layers.index(tab.layer)
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
        dialog = AddRegionDlg(self.layer_heads.max_selected_dim(), self.layer_heads.region_names, self)
        dialog_result = dialog.exec_()
        if dialog_result == QtWidgets.QDialog.Accepted:
            name = dialog.region_name.text()
            dim = dialog.region_dim.currentData()
            region = self.layer_heads.add_region(name, dim)
            self.current_tab._combo_set_region(self.current_tab._combo_id_to_idx[region.id])

    def remove_region(self):
        """Remove region if it is not assigned to any no shapes"""
        reg = self.current_tab.curr_region
        self.layer_heads.remove_region(reg)

    @property
    def current_tab(self):
        """ Current Tab widget. """
        return self.widget(self.currentIndex())

    def _layer_changed(self):
        """item Changed handler"""
        self.layer_heads.select_layer(self.current_tab.layer)
        self.regions_changed.emit()

    def selection_changed(self):
        selected = self.layer_heads.block.selection._selected
        if selected:
            for layer in self.layer_heads.block.layers:
                region = layer.get_shape_region(selected[0])
                is_region_same = True
                for g_item in selected:
                    if region != layer.get_shape_region(g_item):
                        is_region_same = False
                        break
                if is_region_same:
                    layer.gui_selected_region = region
                else:
                    layer.gui_selected_region = RegionItem.none
            self.update_tabs()



class RegionLayerTab(QtWidgets.QWidget):
    """
    Single Tab of the Region panel. One tab for every layer in the current topology block.
    """

    def __init__(self, layer_heads, layer, parent):
        """
        Constructor, just make widgets and set reference to parent and layer_heads.
        Reinit must be called explicitely to fill the widget content.
        """
        super().__init__(parent)
        self._parent = parent

        # === Data
        self.layer_heads = layer_heads
        # Reference model for region panel
        self.layer = layer
        # Layer to which this Tab is related.
        self._layer_name = None
        # Name of the layer.
        self._combo_id_to_idx = {RegionItem.none.id: 0}
        # auxiliary map from region ID to index in the combo box.

        self.layer_heads.region_changed.connect(self._update_region_content)
        self.layer_heads.region_list_changed.connect(self._update_region_list)
        self._make_widgets()

    def reinit(self, layer_name):
        self._layer_name = layer_name
        self._update_region_list()

    @property
    def curr_region(self):
        """ Current region. """
        return self.layer.gui_selected_region

    @property
    def region_color(self):
        return QtGui.QColor(self.curr_region.color)

    def _make_widgets(self):
        """Make grid of widgets of the single region tab.
           Do not fill the content.
        """
        grid = QtWidgets.QGridLayout()

        self.wg_region_combo = ComboBox()
        self.wg_region_combo.currentIndexChanged.connect(self._combo_set_region)
        grid.addWidget(self.wg_region_combo, 0, 0)

        self.wg_add_button = QtWidgets.QPushButton()
        self.wg_add_button.setIcon(icon.get_app_icon("add"))
        self.wg_add_button.setToolTip('Create new region')
        self.wg_add_button.clicked.connect(self._parent.add_region)
        grid.addWidget(self.wg_add_button, 0, 1)

        self.wg_remove_button = QtWidgets.QPushButton()
        self.wg_remove_button.setIcon(icon.get_app_icon("remove"))
        self.wg_remove_button.clicked.connect(self._parent.remove_region)
        grid.addWidget(self.wg_remove_button, 0, 2)

        # name
        self.wg_name = QtWidgets.QLineEdit()
        self.wg_name.editingFinished.connect(self._name_editing_finished)
        grid.addWidget(self.wg_name, 1, 1, 1, 2)
        name_label = QtWidgets.QLabel("Name:", self)
        name_label.setToolTip("Name of the region.")
        name_label.setBuddy(self.wg_name)
        grid.addWidget(name_label, 1, 0)

        # color button
        self.wg_color_button = QtWidgets.QPushButton()
        self.wg_color_button.setFixedSize(25, 25)
        self.wg_color_button.clicked.connect(self._set_color)
        grid.addWidget(self.wg_color_button, 2, 1)
        color_label = QtWidgets.QLabel("Color:", self)
        color_label.setBuddy(self.wg_color_button)
        grid.addWidget(color_label, 2, 0)

        # dimension (just label)
        wg_dim_label = QtWidgets.QLabel("Dimension:", self)
        grid.addWidget(wg_dim_label, 3, 0)
        self.wg_dims = QtWidgets.QLabel("", self)
        grid.addWidget(self.wg_dims, 3, 1)

        # boundary
        self.wg_boundary = QtWidgets.QCheckBox()
        self.wg_boundary.clicked.connect(self._boundary_changed)
        grid.addWidget(self.wg_boundary, 4, 1)
        wg_boundary_label = QtWidgets.QLabel("Boundary:", self)
        wg_boundary_label.setBuddy(self.wg_boundary)
        grid.addWidget(wg_boundary_label, 4, 0)

        # not use
        self.wg_notused = QtWidgets.QCheckBox()
        self.wg_notused.clicked.connect(self._not_used_checked)
        grid.addWidget(self.wg_notused, 5, 1)
        wg_notused_label = QtWidgets.QLabel("Inactive:", self)
        wg_notused_label.setBuddy(self.wg_notused)
        grid.addWidget(wg_notused_label, 5, 0)

        # mesh step
        self.wg_mesh_step_edit = QtWidgets.QLineEdit()
        self.wg_mesh_step_edit.setMinimumWidth(80)
        self.wg_mesh_step_edit.setMaximumWidth(80)
        validator = QtGui.QDoubleValidator()
        validator.setRange(0.0, 1e+7, 7)  # assuming unit in meters and dimesion fo the whole earth :-)
        self.wg_mesh_step_edit.setValidator(validator)
        self.wg_mesh_step_edit.editingFinished.connect(self._set_mesh_step)
        grid.addWidget(self.wg_mesh_step_edit, 6, 1)

        wg_mesh_step_label = QtWidgets.QLabel("Mesh step:", self)
        wg_mesh_step_label.setBuddy(self.wg_mesh_step_edit)
        grid.addWidget(wg_mesh_step_label, 6, 0)

        # self._set_visibility(layer_id, region.dim != RegionDim.none)
        sp1 = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Expanding)
        sp2 = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Expanding)
        grid.addItem(sp1, 7, 0)
        grid.addItem(sp2, 7, 1)

        self.setLayout(grid)

    def _update_region_list(self):
        """
        Update combobox according to the region list.
        :return:
        """
        with nosignal(self.wg_region_combo) as combo:
            # self.wg_region_combo.setUpdatesEnabled(False) # Disable repainting until combobox is filled.
            combo.clear()
            self._combo_id_to_idx = {}
            sorted_regions = self.layer_heads.regions_model.regions.values()
            for idx, reg in enumerate(sorted_regions):
                self._combo_id_to_idx[reg.id] = idx
                combo.addItem(self.make_combo_label(reg), reg.id)
            # self.wg_region_combo.setUpdatesEnabled(True)
        self._update_region_content()


    def make_combo_label(self, region):
        """Region label for the combo box."""
        return region.name + " (" + AddRegionDlg.REGION_DESCRIPTION_DIM[region.dim] + ")"


    def _update_region_content(self):
        """
        Update widgets according to selected region.
        :return:
        """
        with nosignal(self.wg_region_combo) as o:
            o.setCurrentIndex(self._combo_id_to_idx[self.curr_region.id])
        region = self.curr_region

        region_used = self.layer_heads.regions_model.is_region_used(self.curr_region)
        is_default = self.curr_region == RegionItem.none
        if is_default:
            self.wg_remove_button.setEnabled(False)
            self.wg_remove_button.setToolTip('Default region cannot be removed!')
            self.wg_boundary.setEnabled(False)
            self.wg_mesh_step_edit.setEnabled(False)
        elif region_used:
            self.wg_remove_button.setEnabled(False)
            self.wg_remove_button.setToolTip('Region is still in use!')
        else:
            self.wg_remove_button.setEnabled(True)
            self.wg_remove_button.setToolTip('Remove selected region')

        self.wg_name.setText(region.name)

        pixmap = QtGui.QPixmap(16, 16)
        pixmap.fill(self.region_color)
        self.wg_color_button.setIcon(QtGui.QIcon(pixmap))
        self._parent._update_tab_head(self)

        self.wg_dims.setText(AddRegionDlg.REGION_DESCRIPTION_DIM[region.dim])
        self.wg_boundary.setChecked(region.boundary)
        self.wg_notused.setChecked(region.not_used)
        self.wg_mesh_step_edit.setText("{:8.4g}".format(region.mesh_step).replace(" ", ""))

        none_widgets = [self.wg_boundary, self.wg_color_button, self.wg_name, self.wg_notused, self.wg_mesh_step_edit]
        if is_default:
            for wg in none_widgets:
                wg.setEnabled(False)
        else:
            for wg in none_widgets:
                wg.setEnabled(True)

        self.update()


    # ======= Internal signal handlers
    def _combo_set_region(self, combo_id):
        """
        Handle change in region combo box.
        """
        for reg_id, idx in self._combo_id_to_idx.items():
            if idx == combo_id:
                break
        region = self.layer_heads.regions_model.regions.get(reg_id)
        self.layer.gui_selected_region = region
        self.layer.set_region_to_selected_shapes(region)
        self._parent.regions_changed.emit()
        self._parent.update_tabs()
        # self._update_region_content() # update called through connected signal layer_heads.region_changed

    def _name_editing_finished(self):
        """
        Handler of region name change.
        :return:
        """
        new_name = self.wg_name.text().strip()
        if new_name == self.curr_region.name:
            return
        elif  new_name in self.layer_heads.region_names:
            error = "Region name already exist"
        elif not new_name:
            error = "Region name is empty"
        else:
            error = None
            with undo.group("Set Name"):
                self.curr_region.set_name(new_name)
                self.layer.set_gui_selected_region(self.curr_region)


        if error:
            err_dialog = GMErrorDialog(self)
            err_dialog.open_error_dialog(error)
            self.wg_name.selectAll()

        self._update_region_content()

    def _set_color(self):
        """Region color is changed, refresh diagram"""
        color_dialog = QtWidgets.QColorDialog(self.region_color)
        for icol, color in enumerate(AddRegionDlg.BACKGROUND_COLORS):
            color_dialog.setCustomColor(icol, color)
        selected_color = color_dialog.getColor()

        if selected_color.isValid():
            with undo.group("Set Color"):
                self.curr_region.set_color(selected_color.name())
                self.layer.set_gui_selected_region(self.curr_region)

        self._update_region_content()
        self._parent.update_tabs()
        self._parent.regions_changed.emit()

    def _boundary_changed(self):
        with undo.group("Change regions boundary setting"):
            self.curr_region.set_boundary(self.wg_boundary.isChecked())
            self.layer.set_gui_selected_region(self.curr_region)

    def _not_used_checked(self):
        """
        Region not used property is changed
        TODO: possibly make as region type : [regular, boundary, not used]
        """
        with undo.group("Change regions not used setting"):
            self.curr_region.set_not_used(self.wg_notused.isChecked())
            self.layer.set_gui_selected_region(self.curr_region)

    def _set_mesh_step(self):
        step_value = float(self.wg_mesh_step_edit.text())
        if step_value != self.curr_region.mesh_step:
            with undo.group("Set Mesh Step"):
                self.curr_region.set_region_mesh_step(step_value)
                self.layer.set_gui_selected_region(self.curr_region)

