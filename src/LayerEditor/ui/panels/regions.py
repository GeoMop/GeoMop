from contextlib import contextmanager
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
import gm_base.icon as icon
from gm_base.geomop_dialogs import GMErrorDialog
from ..dialogs.regions import AddRegionDlg


@contextmanager
def nosignal(qt_obj):
    """
    Context manager for blocking signals inside some signal handlers.
    TODO: move to some common module
    """
    qt_obj.blockSignals(True)
    yield qt_obj
    qt_obj.blockSignals(False)


class LayerHeads(QtCore.QObject):
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


    def __init__(self, layers_geometry):
        """
        Constructor.
        :param layers_geometry: LEConfig class.
        """
        super().__init__()

        self.lc = layers_geometry
        # Data object used to retrieve data
        self._selected_layers = {0: 0}
        # Selected layer tab in topology. Map { topology_id : layer_id}.
        self._selected_regions = {0: 0}
        # Selected region for each layer including layers in other topologies/blocks.
        # { layer_id: region_id }

    def reinit_regions_map(self):
        """ Update _selected_regions according to the layers."""
        for layer_id, name in self.layer_names:
            self._selected_regions.setdefault(layer_id, 0)

    def select_regions(self, region_dict):
        """
        Update dictionary assigning selected region id to the layer id.
        :param region_dict:
        :return:
        """
        # assert layer_id in self._selected_regions
        self._selected_regions.update(region_dict)
        self.region_changed.emit()

    def select_layer(self, layer_id):
        """ Select actual layer tab."""
        self._selected_layers[self.current_topology_id] = layer_id

    def add_region(self, name, dim, color):
        """ Add new region according to the provided data from the current tab and select it."""
        region = self.regions.add_new_region(color, name, dim, True, "Add Region")
        self._selected_regions[self.current_layer_id] = region.reg_id
        self.region_list_changed.emit()
        return region

    def remove_region(self, reg_id):
        """Remove the region."""
        shapes = self.regions.get_shapes_of_region(reg_id)
        if not shapes:
            self.regions.delete_region(reg_id)
            self.region_list_changed.emit()
        else:
            print("List is not empty! Oops, this button should have been disabled.")

    @property
    def max_selected_dim(self):
        """Maximal object dimension within the current selection.
        TODO: better check for the fracture layer.
        """
        max_selected_dim = self.lc.main_window.diagramScene.selection.max_selected_dim()
        if self.current_layer_id >= 0:
            max_selected_dim += 1
        return max(max_selected_dim, 0)

    @property
    def region_names(self):
        """ List of unique region names."""
        return {reg.name for reg in self.lc.diagram.regions.regions.values()}

    @property
    def regions(self):
        """ Regions object. """
        return self.lc.diagram.regions

    @property
    def current_topology_id(self):
        return self.lc.diagram.topology_idx

    @property
    def selected_region_id(self):
        """ Region ID of the current region of the current layer. """
        return self._selected_regions[self.current_layer_id]

    @property
    def selected_region(self):
        """ Current region of the current layer."""
        region_id = self._selected_regions[self.current_layer_id]
        return self.regions.regions[region_id]

    @property
    def current_layer_id(self):
        """ Layer ID for current teb in Region Panel."""
        return self._selected_layers[self.current_topology_id]

    @property
    def layer_names(self):
        """
        Return list of
        :return: [ (layer_id, layer_name), .. ]
        """
        return self.regions.get_layers(self.current_topology_id)

    @property
    def selected_regions(self):
        """
        Return list of selected region IDs.
        :return: [ (layer_id, region_id), ... ]
        """
        return self._selected_regions


class Regions(QtWidgets.QToolBox):
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
    color_changed = QtCore.pyqtSignal()

    # Emitted when color of some region has changed.

    def __init__(self, layer_heads, parent=None):
        """
        Inicialize window

        Args:
            parent (QWidget): parent window ( empty is None)
        """
        super().__init__(parent)

        self.layer_heads = layer_heads
        # Reference to adaptor for tab data.
        self.layer_id_to_idx = {}
        # Map layer_id to tab index.
        self.tabs = []
        #  Tab widgets.
        self.update_tabs()

        self.currentChanged.connect(self._layer_changed)

    @property
    def regions(self):
        """ Regions data object. """
        return self.layer_heads.regions

    def update_tabs(self):
        """
        Update tabs and its contents according to layer heads adaptor.
        :return:
        """
        # Update number of tabs and their layers.
        self.layer_heads.reinit_regions_map()
        i_tab = 0
        names = self.layer_heads.layer_names
        self.layer_id_to_idx = {}
        for layer_id, layer_name in names:
            self.layer_id_to_idx[layer_id] = i_tab
            if i_tab >= self.count():
                tab_widget = RegionLayerTab(self.layer_heads, i_tab, layer_id, layer_name, self)
                self.tabs.append(tab_widget)
                self.addItem(tab_widget, "")
                self._update_tab_head(tab_widget)
            i_tab += 1
        while i_tab < self.count():
            self.removeItem(i_tab)
            self.tabs.pop(-1)
            i_tab += 1
        # Update content.
        self.setCurrentIndex(self.layer_id_to_idx[self.layer_heads.current_layer_id])

    def _update_tab_head(self, tab):
        """
        Update tab head, called by tab itself after change of region.
        :param i:
        :return:
        """
        color = tab.region_color
        item_idx = self.layer_id_to_idx[tab.layer_id]
        pixmap = QtGui.QPixmap(16, 16)
        pixmap.fill(color)
        iconPix = QtGui.QIcon(pixmap)
        self.setItemIcon(item_idx, iconPix)
        self.setItemText(item_idx, "{} ({})".format(tab._layer_name, tab.region.name))

    def add_region(self):
        """
        Add new region to all combo and select it in current tab.
        Handle combo changed signal in current tab.
        """
        dialog = AddRegionDlg(self.layer_heads.max_selected_dim, self.layer_heads.region_names, self)
        dialog_result = dialog.exec_()
        if dialog_result == QtWidgets.QDialog.Accepted:
            name = dialog.region_name.text()
            dim = dialog.region_dim.currentData()
            color = dialog.get_some_color(self.layer_heads.regions._get_available_reg_id() - 1).name()
            region = self.layer_heads.add_region(name, dim, color)
            self.current_tab._combo_set_region(region.reg_id)
            self.update_tabs()
            self.color_changed.emit()

    def remove_region(self):
        """Remove region if it is not assigned to any no shapes"""
        reg_id = self.layer_heads.selected_region_id
        self.layer_heads.remove_region(reg_id)

    @property
    def current_tab(self):
        """ Current Tab widget. """
        return self.tabs[self.currentIndex()]

    def _layer_changed(self):
        """item Changed handler"""
        self.layer_heads.select_layer(self.current_tab.layer_id)
        self.color_changed.emit()


class RegionLayerTab(QtWidgets.QWidget):
    """
    Single Tab of the Region panel. One tab for every layer in the current topology block.
    """

    def __init__(self, layer_heads, i_tab, layer_id, layer_name, parent):
        """

        :param regions:
        :param region_id:
        :param parent:
        """
        super().__init__(parent)
        self._parent = parent

        # === Data
        self.layer_heads = layer_heads
        # Reference model for region panel
        self._i_tab = i_tab
        # Set index of tab in the toolbox (used for callback to set header).
        self.layer_id = layer_id
        # ID of the layer to which this Tab is related.
        self._layer_name = layer_name
        # Name of the layer.
        self._combo_id_to_idx = {0: 0}
        # auxiliary map from region ID to index in the combo box.

        self.layer_heads.region_changed.connect(self._update_region_content)
        self.layer_heads.region_list_changed.connect(self._update_region_list)
        self._make_widgets()

    @property
    def region_id(self):
        """ Current region id. """
        return self.layer_heads.selected_regions[self.layer_id]

    @property
    def region(self):
        """ Current region. """
        return self.layer_heads.regions.regions[self.region_id]

    @property
    def region_color(self):
        """ QColor of current region.
            TODO: make this a property of the  Region.
            (with optional parameter object_dim for the None region)
        """
        return QtGui.QColor(self.region.color)

    def _make_widgets(self):
        """Make grid of widget of the single region tab."""
        grid = QtWidgets.QGridLayout()

        self.wg_region_combo = QtWidgets.QComboBox()
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
        self._update_region_list()

    def _update_region_list(self):
        """
        Update combobox according to the region list.
        :return:
        """
        with nosignal(self.wg_region_combo) as combo:
            # self.wg_region_combo.setUpdatesEnabled(False) # Disable repainting until combobox is filled.
            combo.clear()
            self._combo_id_to_idx = {}
            sorted_regions = self.layer_heads.regions.regions.values()
            for idx, reg in enumerate(sorted_regions):
                self._combo_id_to_idx[reg.reg_id] = idx
                combo.addItem(self.make_combo_label(reg), reg.reg_id)
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
            o.setCurrentIndex(self._combo_id_to_idx[self.region_id])
        region = self.region

        shapes = self.layer_heads.regions.get_shapes_of_region(self.region_id)
        is_default = (self.region_id == 0)
        if is_default:
            self.wg_remove_button.setEnabled(False)
            self.wg_remove_button.setToolTip('Default region cannot be removed!')
            self.wg_boundary.setEnabled(False)
            self.wg_mesh_step_edit.setEnabled(False)
        if shapes:
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
        self.wg_mesh_step_edit.setText("{:8.4g}".format(region.mesh_step))

        none_widgets = [self.wg_boundary, self.wg_color_button, self.wg_name, self.wg_notused, self.wg_mesh_step_edit]
        if is_default:
            for wg in none_widgets:
                wg.setEnabled(False)
        else:
            for wg in none_widgets:
                wg.setEnabled(True)

        self.update()


    # ======= Internal signal handlers
    def _combo_set_region(self, region_id):
        """
        Handle change in region combo box.
        """
        self._region_id = region_id
        self.layer_heads.select_regions({self.layer_id: region_id})
        # self._update_region_content() # update called through connected signal layer_heads.region_changed

    def _name_editing_finished(self):
        """
        Handler of region name change.
        :return:
        """
        new_name = self.wg_name.text().strip()
        if new_name in self.layer_heads.region_names:
            error = "Region name already exist"
        elif not new_name:
            error = "Region name is empty"
        else:
            error = None
            self.region.name = new_name
            self.layer_heads.regions.set_region_name(self.region.reg_id, new_name, True, "Set region name")

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
            self.layer_heads.regions.set_region_color(self.region_id,
                                                      selected_color.name(), True, "Set Color")

            # self.region.set_color(selected_color)
        self._update_region_content()
        self._parent.update_tabs()
        self._parent.color_changed.emit()

    def _boundary_changed(self):
        self.layer_heads.regions.set_region_boundary(self.region_id, self.wg_boundary.isChecked(),
                                                     True, "Set region boundary")

    def _not_used_checked(self):
        """
        Region not used property is changed
        TODO: make as region type : [regular, boundary, not used]
        """
        self.layer_heads.regions.set_region_not_used(self.region_id, self.wg_notused.isChecked(),
                                                     True, "Set region usage")

    def _set_mesh_step(self, value):
        step_value = float(self.wg_mesh_step.text())
        self.region.set_region_mesh_step(self.region_id, step_value,
                                         True, "Set region mesh step")
