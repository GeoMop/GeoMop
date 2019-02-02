from contextlib import contextmanager
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
import gm_base.icon as icon
from gm_base.geomop_dialogs import GMErrorDialog
from ..dialogs.regions import AddRegionDlg
from gm_base.geometry_files.format_last import RegionDim


@contextmanager
def nosignal(qt_obj):
    qt_obj.blockSignals(True)
    yield qt_obj
    qt_obj.blockSignals(False)


class LayerHeads(QtCore.QObject):
    """
    TODO: refactor to the class for supplement GUI states.
    Adaptor to access layer names and
    to store currently selected regions.
    """

    region_changed = QtCore.pyqtSignal()
    # current region in current tab has changed
    selected_layer_changed = QtCore.pyqtSignal()
    # current tab in RegionPanel has changed.
    region_list_changed = QtCore.pyqtSignal()
    # added or removed region

    #layers_changed = QtCore.pyqtSignal()
    # topology (block of layers) has changed

    def __init__(self, layers_geometry):
        super().__init__()

        self.lc = layers_geometry
        # Data object used to retrieve data

        self._selected_regions = { 0: 0}
        # Selected region for each layer including layers in other topologies/blocks.
        # { layer_id: region_id }
        self._selected_layers = { 0: 0}
        # Selected layer tab in topology. Map { topology_id : layer_id}.


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
        self._selected_layers[self.current_topology_id] = layer_id
        self.layer_changed.emit()

    def add_region(self, name, dim, color):
        self.regions.add_new_region(color, name, dim, True, "Add Region")
        self.region_list_changed.emit()

    def remove_region(self, reg_id):
        shapes = self.regions.get_shapes_of_region(reg_id)
        if not shapes:
            self.regions.delete_region(reg_id)
            self.region_list_changed.emit()
        else:
            print("List is not empty! Oops, this button should have been disabled.")


    @property
    def max_selected_dim(self):
        max_selected_dim = self.lc.main_window.diagramScene.selection.max_selected_dim()
        if self.current_layer_id >= 0:
            max_selected_dim += 1
        return max(max_selected_dim, 0)

    @property
    def region_names(self):
        rn = [reg.name for reg in self.lc.diagram.regions.regions.values()]
        return rn

    @property
    def regions(self):
        return self.lc.diagram.regions

    @property
    def current_topology_id(self):
        return self.lc.diagram.topology_idx

    @property
    def selected_region_id(self):
        return self._selected_regions[self.current_layer_id]

    @property
    def selected_region(self):
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



        # self.topology_idx = 0
        # """Current topology idx"""
        # self.layer_idx = 0
        # """Current layer idx"""
        # self.last_layer = {}
        # """Last edited layer in topology (topology_id:layer_name)"""
        # self.last_region = {}
        # """Last edited region in topology (layer_name:region_name)"""
        # self.removing_items = False
        # """Items is during removing"""
        # self.update_region_data = False
        # """Region data are during updating"""
        # self._show_layers()

        self.currentChanged.connect(self._layer_changed)
        # self._emit_regionChanged = True
        # """If True regionChanged is emitted"""

    @property
    def regions(self):
        return self.layer_heads.regions

    def update_tabs(self):
        """
        Update tabs and its contents according to layer heads adaptor.
        :return:
        """
        # Update number of tabs and their layers.
        i_tab = 0
        names = self.layer_heads.layer_names
        self.layer_id_to_idx = {}
        for layer_id, layer_name in names:
            self.layer_id_to_idx[layer_id] = i_tab
            if i_tab >= self.count():

                tab_widget = RegionLayerTab(self.layer_heads, i_tab, layer_id, layer_name, self)
                self.tabs.append(tab_widget)
                self.addItem(tab_widget, "")
            i_tab += 1
        while i_tab < self.count():
            self.removeItem(i_tab)
            self.tabs.pop(-1)
            i_tab += 1
        # Update content.
        self.update_tabs_content()
        self.setCurrentIndex(self.layer_id_to_idx[self.layer_heads.current_layer_id])

    def update_tabs_content(self):
        """
        Update regions in tabs including heads, not tabs itself.
        """
        assert len(self.layer_id_to_idx) == self.count()
        for layer_id, i_tab  in self.layer_id_to_idx.items():
            self.tabs[i_tab]._update_region_content()
            self._update_tab_head(i_tab)

    def _update_tab_head(self, i):
        """
        Update tab head, called by tab itself after change of region.
        :param i:
        :return:
        """
        tab = self.tabs[i]
        color = QtGui.QColor(QtGui.QColor(tab.region.color))
        #if color == "##":
        #    color = QtGui.QColor("#f0f0e8")
        pixmap = QtGui.QPixmap(16, 16)
        pixmap.fill(color)
        iconPix = QtGui.QIcon(pixmap)
        self.setItemIcon(i, iconPix)
        self.setItemText(i, "{} ({})".format(tab._layer_name, tab.region.name))



    # def _show_layers(self):
    #     """Refresh layers view"""
    #     self.layers = self.regions.get_layers(self.topology_idx)
    #     regions.current_topology_id = self.topology_idx
    #     self.wg_region_combo = {}
    #     self.dims = {}
    #     self.dim_label = {}
    #     self.wg_add_button = {}
    #     self.remove_button = {}
    #     self.color_label = {}
    #     self.color_button = {}
    #     self.name = {}
    #     self.boundary = {}
    #     self.wg_boundary_label = {}
    #     self.notused = {}
    #     self.notused_label = {}
    #     self.mesh_step_label = {}
    #     self.mesh_step = {}
    #     self.layers_id = []
    #     regions.current_regions = {}
    #     for layer_id in self.layers:
    #         self.layers_id.append(layer_id)
    #         widget = self._add_region_panel(layer_id, self._get_last_region(layer_id))
    #         i = self.addItem(widget, self.layers[layer_id])
    #         self._set_box_title(i, layer_id)
    #     index = self._get_last_layer()
    #     self.setCurrentIndex(index)
    #     regions.current_layer_id = self.layers_id[self.currentIndex()]
        
    # def _get_last_layer(self):
    #     """Return last layer_id"""
    #     if not self.topology_idx in self.last_layer:
    #         self.last_layer[self.topology_idx] = 0
    #     if self.last_layer[self.topology_idx] in self.layers_id:
    #         index = self.last_layer[self.topology_idx]
    #     else:
    #         index = 0
    #         self.last_layer[self.topology_idx] = self.layers_id[0]
    #     return index
    #
    # def _get_last_region(self, layer_id):
    #     """Return last region_id"""
    #     data = cfg.diagram.regions
    #     if self.layers[layer_id] in self.last_region:
    #         region_name = self.last_region[self.layers[layer_id]]
    #     else:
    #         self.last_region[self.layers[layer_id]] = data.regions[0].name
    #         return data.regions[0]
    #     for region in data.regions.values():
    #         if region.name == region_name:
    #             return region
    #     self.last_region[self.layers[layer_id]] =  data.regions[0].name
    #     return data.regions[0]

            



    # def _add_disply_region(self, region):
    #     """Add new region to all combo and display it"""
    #     label = region.name + " (" + AddRegionDlg.REGION_DESCRIPTION_DIM[region.dim] + ")"
    #     for layer_id in self.layers:
    #         self.wg_region_combo[layer_id].addItem(label, region.reg_id)
    #     layer_id = self.layers_id[self.currentIndex()]
    #     self._update_layer_controls(region, layer_id)
    #     self.last_region[self.layers[layer_id]] = region.name



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
            #color = dialog.get_some_color(data._get_available_reg_id()-1).name()
            self.layer_heads.add_region(name, dim, color)

            #region = self.regions.add_new_region(color, name, dim, True, "Add Region")



    def remove_region(self):
        """Remove region if it is not assigned to any no shapes"""
        reg_id = self.layer_heads.selected_region_id
        self.layer_heads.remove_region(reg_id)





    # def _not_used_set(self, layer_id):
    #     """Region not used property is changed"""
    #     if self.update_region_data:
    #         return
    #     data = cfg.diagram.regions
    #     region_id = self.wg_region_combo[layer_id].currentData()
    #     data.set_region_not_used(region_id, self.wg_notused.isChecked(),
    #         True, "Set region usage")
    #
    # def _boundary_set(self, layer_id):
    #     """Region boundary property is changed"""
    #     if self.update_region_data:
    #         False
    #     data = cfg.diagram.regions
    #     region_id = self.wg_region_combo[layer_id].currentData()
    #     data.set_region_boundary(region_id, self.boundary.isChecked(),
    #         True, "Set region boundary")
    #
    # def _mesh_step_set(self, layer_id):
    #     if self.update_region_data:
    #         return
    #     step_value = float(self.mesh_step[layer_id].text())
    #     data = cfg.diagram.regions
    #     region_id = self.wg_region_combo[layer_id].currentData()
    #     data.set_region_mesh_step(region_id, step_value,
    #         True, "Set region mesh step")
    #
    #
    def _layer_changed(self):
        """item Changed handler"""
        index = self.currentIndex()
        assert 0 <= index < self.count()
        tab = self.item(index)
        layer_id = tab.layer_id
        self.layer_heads.select_layer(layer_id)
    #
    #
    #
    #
    # def get_current_region(self):
    #     """Return current region id"""
    #     index = self.currentIndex()
    #     layer_id = self.layers_id[index]
    #     return self.tabs[layer_id].region_id



class RegionLayerTab(QtWidgets.QWidget):

    def __init__(self, layer_heads, i_tab, layer_id, layer_name,  parent):
        """

        :param regions:
        :param region_id:
        :param parent:
        """
        super().__init__(parent)
        
        # === Data
        self.layer_heads = layer_heads
        # Reference model for region panel
        self._i_tab = i_tab
        # Set index of tab in the toolbox (used for callback to set header).
        self._layer_id = layer_id
        # ID of the layer to which this Tab is related.
        self._layer_name = layer_name
        # Name of the layer.
        self._combo_id_to_idx = {0: 0}
        # auxiliary map from region ID to index in the combo box.

        self.layer_heads.region_changed.connect(self._update_region_content)
        self.layer_heads.region_list_changed.connect(self._update_region_list)
        self._make_widgets()

    # @property
    # def regions(self):
    #     return self.layer_heads.regions

    @property
    def region_id(self):
        return self.layer_heads.selected_regions[self._layer_id]

    @property
    def region(self):
        return self.layer_heads.regions.regions[self.region_id]

    def _make_widgets(self):
        """add one region panel to tool box and set region data"""
        grid = QtWidgets.QGridLayout()

        self.wg_region_combo = QtWidgets.QComboBox()
        self.wg_region_combo.currentIndexChanged.connect(self._combo_set_region)
        grid.addWidget(self.wg_region_combo, 0, 0)

        self.wg_add_button = QtWidgets.QPushButton()
        self.wg_add_button.setIcon(icon.get_app_icon("add"))
        self.wg_add_button.setToolTip('Create new region')
        self.wg_add_button.clicked.connect(self.parent().add_region)
        grid.addWidget(self.wg_add_button, 0, 1)

        self.wg_remove_button = QtWidgets.QPushButton()
        self.wg_remove_button.setIcon(icon.get_app_icon("remove"))
        self.wg_remove_button.clicked.connect(self.parent().remove_region)
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
        wg_notused_label = QtWidgets.QLabel("Not Use:", self)
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


        #self._set_visibility(layer_id, region.dim != RegionDim.none)
        #sp1 = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Expanding)
        #sp2 = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Expanding)
        #grid.addItem(sp1, 7, 0)
        #grid.addItem(sp2, 7, 1)


        self.setLayout(grid)
        self._update_region_list()


    # def set_region(self, layer_id, region_id):
    #     """
    #     Rather call this setter explicitly since setting region_id have a side effect.
    #     """
    #     if not self.layer_id:
    #         self.layer_id = layer_id
    #     assert self.layer_id == layer_id
    #     self._region_id = region_id
    #     self.wg_region_combo.setCurrentIndex(self._combo_id_to_idx[self.region_id])
    #     self._update_region_content()
    #     self.parent()._update_tab_head(self._i_tab)

    # @property
    # def region(self):
    #     """
    #     Selected region.
    #     """
    #     return self._regions[self.region_id]
    
    

    def _update_region_list(self):
        """
        Update combobox according to the region list.
        :return:
        """
        self.wg_region_combo.setUpdatesEnabled(False) # Disable repainting until combobox is filled.
        self.wg_region_combo.clear()
        self._combo_id_to_idx = {}
        sorted_regions = self.layer_heads.regions.regions.values()
        for idx, reg in enumerate(sorted_regions):
            self._combo_id_to_idx[reg.reg_id] = idx
            self.wg_region_combo.addItem(self.make_combo_label(reg), reg.reg_id)
        self.wg_region_combo.setCurrentIndex(self._combo_id_to_idx[self.region_id])
        self.wg_region_combo.setUpdatesEnabled(True)

    def make_combo_label(self, region):
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
        elif shapes:
            self.wg_remove_button.setEnabled(False)
            self.wg_remove_button.setToolTip('Region is still in use!')
        else:
            self.wg_remove_button.setEnabled(True)
            self.wg_remove_button.setToolTip('Remove selected region')

        self.wg_name.setText(region.name)

        pixmap = QtGui.QPixmap(16, 16)
        pixmap.fill(QtGui.QColor(region.color))
        self.wg_color_button.setIcon(QtGui.QIcon(pixmap))

        self.wg_dims.setText(AddRegionDlg.REGION_DESCRIPTION_DIM[region.dim])
        self.wg_boundary.setChecked(region.boundary)
        self.wg_notused.setChecked(region.not_used)
        self.wg_mesh_step_edit.setText("{:8.4g}".format(region.mesh_step))



    # def _set_visibility(self, layer_id, visible):
    #     """Set visibility for not NONE items"""
    #     self.wg_name.setReadOnly(not visible)
    #     self.color_label[layer_id].setVisible(visible)
    #     self.wg_color_button.setVisible(visible)
    #     self.wg_dim_label.setVisible(visible)
    #     self.dims[layer_id].setVisible(visible)
    #     self.wg_boundary_label[layer_id].setVisible(visible)
    #     self.boundary.setVisible(visible)
    #     self.notused_label[layer_id].setVisible(visible)
    #     self.wg_notused.setVisible(visible)
    #     self.mesh_step_label[layer_id].setVisible(visible)
    #     self.mesh_step[layer_id].setVisible(visible)



    # def _update_layer_controls(self, region, layer_id):
    #     """Update set region data in layers controls"""
    #     data = cfg.diagram.regions
    #     region_id = [key for key, item in data.regions.items() if item == region][0]
    #     curr_index = self.wg_region_combo[layer_id].findData(region_id)
    #
    #     # old_emit_regionChanged is used due to recursive call of _update_layer_controls
    #     old_emit_regionChanged = self._emit_regionChanged
    #     self._emit_regionChanged = False
    #     self.wg_region_combo[layer_id].setCurrentIndex(curr_index)
    #     self._emit_regionChanged = old_emit_regionChanged
    #
    #     self.wg_name.setText(region.name)
    #     self.dims[layer_id].setText(str(region.dim.value) + "D")
    #     pixmap = QtGui.QPixmap(25, 25)
    #     pixmap.fill(QtGui.QColor(region.color))
    #     iconPix = QtGui.QIcon(pixmap)
    #     self.update_region_data = True
    #     self.wg_color_button.setIcon(iconPix)
    #     self.boundary.setChecked(region.boundary)
    #     self.wg_notused.setChecked(region.not_used)
    #     self.mesh_step[layer_id].setText(str(region.mesh_step))
    #     self.update_region_data = False
    #     self._set_visibility(layer_id, region.dim!=RegionDim.none)







    # ======= Internal signal handlers
    def _combo_set_region(self, region_id):
        """
        Handle change in region combo box.
        """
        self._region_id = region_id
        self.layer_heads.select_regions( {self._layer_id: self.region_id} )
        self._update_region_content()

    def _name_editing_finished(self):
        """
        Handler of region name change.
        :return:
        """
        new_name = self.wg_name.text().strip()

        if new_name  in self.region.name_values:
            error = "Region name already exist"
        elif not new_name:
            error = "Region name is empty"
        else:
            self.region.set_name(new_name)
            #regions.set_region_name([key for key, item in regions.regions.items() if item == region][0],
            #    self.wg_name.text(), True, "Set region name")

        if error:
            err_dialog = GMErrorDialog(self)
            err_dialog.open_error_dialog(error)
            self.wg_name.selectAll()
            
        self.update_region_content()

    def _set_color(self):
        """Region color is changed, refresh diagram"""
        color_dialog = QtWidgets.QColorDialog(QtGui.QColor(self.region.color))
        for icol, color in enumerate(AddRegionDlg.BACKGROUND_COLORS):
            color_dialog.setCustomColor(icol, color)
        selected_color = color_dialog.getColor()

        if selected_color.isValid():
            self.layer_heads.regions.set_region_color(self.region_id,
                selected_color.name(), True, "Set Color")

            #self.region.set_color(selected_color)
        self.update_region_content()
        self.parent().update_tabs()
        self.parent().colorChanged.emit()

    def _boundary_changed(self):
        self.region.set_region_boundary(self.region_id, self.wg_boundary.isChecked(),
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
