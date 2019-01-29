import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
import gm_base.icon as icon
from gm_base.geomop_dialogs import GMErrorDialog
from ..dialogs.regions import AddRegionDlg
from gm_base.geometry_files.format_last import RegionDim


class LayerHeads(QtCore.QObject):
    """
    TODO: refactor to the class for supplement GUI states.
    Adaptor to access layer names and
    to store currently selected regions.
    """

    regionChanged = QtCore.pyqtSignal(int)
    # emitted when selected regions have been changed
    layersChanged = QtCore.pyqtSignal()
    # emitted when topology (block of layers) has been changed

    def __init__(self, layers_geometry):
        super().__init__()

        self.lc = layers_geometry
        # Data object used to retrieve data

        self._selected_regions = {}
        # Current regions in region panel { layer_id: region_id }

        self._current_layer_id = None


    def reset(self):
        self._selected_regions = {}
        self._current_layer_id = None

    def select_region(self, layer_id, region_id):
        # assert layer_id in self._selected_regions
        self._selected_regions[layer_id] = region_id
        self.regionChanged.emit(layer_id)

    def select_layer(self, layer_id):
        self._current_layer_id = layer_id

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
        print("region laryers: ", list(self._selected_regions.keys()), "clayer: ", self._current_layer_id)
        print("laryers: ", self.layer_names)

        return self._current_layer_id

    @property
    def layer_names(self):
        """
        Return list of
        :return: [ (layer_id, layer_name), .. ]
        """
        return self.lc.diagram.regions.get_layers(self.current_topology_id)

    @property
    def selected_regions(self):
        """
        Return list of selected region IDs.
        :return: [ (layer_id, region_id), ... ]
        """
        return self._selected_regions.items()

    @selected_regions.setter
    def selected_regions(self, selected_dict):
        self._selected_regions = selected_dict
        self.regionChanged.emit(-1)




class Regions(QtWidgets.QToolBox):
    """
    GeoMop regions panel

    pyqtSignals:
        * :py:attr:`regionChanged() <regionChanged>`
    """
    regionChanged = QtCore.pyqtSignal()
    """Signal is sent when region in combobox has changed."""
    colorChanged = QtCore.pyqtSignal()
    # Emitted when color of some region has changed.

    def __init__(self, layer_heads, parent=None):
        """
        Inicialize window

        Args:
            parent (QWidget): parent window ( empty is None)
        """
        super(Regions, self).__init__(parent)
        self.layer_heads = layer_heads

        self.layer_idx = 0
        """Current layer idx"""
        self.last_layer = {}
        """Last edited layer in topology (topology_id:layer_name)"""        
        self.last_region = {}
        """Last edited region in topology (layer_id:region_name)"""
        self.removing_items = False
        """Items is during removing"""
        self.update_region_data = False
        """Region data are during updating"""
        self._show_layers()        
        self.currentChanged.connect(self._layer_changed)
        self._emit_regionChanged = True
        """If True regionChanged is emitted"""



    @property
    def regions_data(self):
        return self.layer_heads.regions


    def update_regions_panel(self):
        """Refresh the region panel based upon data layer"""
        # TODO: Rewrite whole region panel to utilize this function. When any change occurs outside of this scope, this function should be called as well.

        reg_idx = self.get_current_region()
        shapes = self.regions_data.get_shapes_of_region(reg_idx)
        # cannot remove default or utilized region
        topology_layers = self.regions_data.layers_topology[self.layer_heads.current_topology_id]
        if reg_idx == 0:
            for layer_id in topology_layers:
                self.remove_button[layer_id].setEnabled(False)
                self.remove_button[layer_id].setToolTip('Default region cannot be removed!')
        elif shapes:
            for layer_id in topology_layers:
                self.remove_button[layer_id].setEnabled(False)
                self.remove_button[layer_id].setToolTip('Region is still in use!')
        else:
            for layer_id in topology_layers:
                self.remove_button[layer_id].setEnabled(True)
                self.remove_button[layer_id].setToolTip('Remove selected region')

    def release_all(self):
        """Remove all items"""
        self.removing_items = True
        for i in range(self.count()-1, -1, -1):
            widget = self.widget(i)
            self.removeItem(i)            
            widget.setParent(None)
        self.removing_items = False
    
    def set_topology(self):
        """Set current topology, and refresh layer view"""
        self.release_all()
        self._show_layers()

    # def select_current_regions(self, regions):
    #     """Select current regions in topology"""
    #     region_data = cfg.diagram.regions
    #     self._emit_regionChanged = False
    #     for i in range(0, len(regions)):
    #         layer_id = region_data.layers_topology[self.topology_idx][i]
    #         new_index = self.regions[layer_id].findData(regions[i])
    #         self.regions[layer_id].setCurrentIndex(new_index)
    #     self._emit_regionChanged = True
        
    def _show_layers(self):
        """Refresh layers view"""
        self.regions = {}
        self.dims = {}
        self.dim_label = {}
        self.add_button = {}
        self.remove_button = {}
        self.color_label = {}
        self.color_button = {}
        self.name = {}
        self.boundary = {}
        self.boundary_label = {}
        self.notused = {}
        self.notused_label = {}
        self.mesh_step_label = {}
        self.mesh_step = {}
        self.layers_id = []
        self.layer_heads.reset()
        for layer_id, layer_name in self.layer_heads.layer_names:
            self.layers_id.append(layer_id) 
            widget = self._add_region_panel(layer_id, self._get_last_region(layer_id))            
            i = self.addItem(widget, "")
            self._set_box_title(i, layer_id, layer_name)
        index = self._get_last_layer()
        self.setCurrentIndex(index)
        self.layer_heads.select_layer(self.layers_id[self.currentIndex()])
        
    def _get_last_layer(self):
        """Return last layer_id"""
        topology_id = self.layer_heads.current_topology_id
        if not topology_id in self.last_layer:
            self.last_layer[topology_id] = 0
        if self.last_layer[topology_id] in self.layers_id:
            index = self.last_layer[topology_id]
        else:
            index = 0
            self.last_layer[topology_id] = self.layers_id[0]
        return index
        
    def _get_last_region(self, layer_id):
        """Return last region_id"""
        if layer_id in self.last_region:
            region_name = self.last_region[layer_id]
        else:
            self.last_region[layer_id] = self.regions_data.regions[0].name
            return self.regions_data.regions[0]
        for region in self.regions_data.regions.values():
            if region.name == region_name:
                return region
        self.last_region[layer_id] =  self.regions_data.regions[0].name
        return self.regions_data.regions[0]

            
    def _add_region_panel(self, layer_id, region):
        """add one region panel to tool box and set region data"""

        grid = QtWidgets.QGridLayout()             
        # select and add region
        pom_lambda = lambda ii: lambda: self._region_set(ii)
        self.regions[layer_id] = QtWidgets.QComboBox()
        for i in range(0, len(self.regions_data.regions)):
            label = self.regions_data.regions[i].name + " (" + AddRegionDlg.REGION_DESCRIPTION_DIM[self.regions_data.regions[i].dim] + ")"
            self.regions[layer_id].addItem(label,  i)
            self.layer_heads.select_region(layer_id, region.reg_id)

        curr_index = self.regions[layer_id].findData([key for key, value in self.regions_data.regions.items() if value == region][0])
        self._emit_regionChanged = False
        self.regions[layer_id].setCurrentIndex(curr_index)
        self._emit_regionChanged = True
        self.regions[layer_id].currentIndexChanged.connect(pom_lambda(layer_id))
        self.add_button[layer_id] = QtWidgets.QPushButton()
        self.add_button[layer_id].setIcon(icon.get_app_icon("add"))
        self.add_button[layer_id].setToolTip('Create new region')
        self.add_button[layer_id].clicked.connect(self._add_region)

        self.remove_button[layer_id] = QtWidgets.QPushButton()
        self.remove_button[layer_id].setIcon(icon.get_app_icon("remove"))
        self.remove_button[layer_id].clicked.connect(self._remove_region)
        self.remove_button[layer_id].setEnabled(False)
        self.remove_button[layer_id].setToolTip('Default region cannot be removed!')

        grid.addWidget(self.regions[layer_id], 0, 0)
        grid.addWidget(self.add_button[layer_id], 0, 1)
        grid.addWidget(self.remove_button[layer_id], 0, 2)
        
        # name
        pom_lamda = lambda ii: lambda: self._name_set(ii)
        name_label = QtWidgets.QLabel("Name:", self)            
        self.name[layer_id] = QtWidgets.QLineEdit()
        self.name[layer_id].setText(region.name)
        self.name[layer_id].editingFinished.connect(pom_lamda(layer_id))        
        grid.addWidget(name_label, 1, 0)
        grid.addWidget(self.name[layer_id], 1, 1, 1, 2)
        
        #color button
        self.color_label[layer_id] = QtWidgets.QLabel("Color:", self)
        pom_lamda = lambda ii: lambda: self._color_set(ii)
        self.color_button[layer_id] = QtWidgets.QPushButton()
        pixmap = QtGui.QPixmap(25, 25)
        pixmap.fill(QtGui.QColor(region.color))
        iconPix = QtGui.QIcon(pixmap)
        self.color_button[layer_id].setIcon(iconPix)
        self.color_button[layer_id].setFixedSize( 25, 25 )
        self.color_button[layer_id].clicked.connect(pom_lamda(layer_id))
        grid.addWidget(self.color_label[layer_id], 2, 0)
        grid.addWidget(self.color_button[layer_id], 2, 1)
        
        # dimension
        self.dim_label[layer_id] = QtWidgets.QLabel("Dimension:", self)
        self.dims[layer_id] = QtWidgets.QLabel(AddRegionDlg.REGION_DESCRIPTION_DIM[region.dim], self)
        grid.addWidget(self.dim_label[layer_id], 3, 0)
        grid.addWidget(self.dims[layer_id], 3, 1)
        
        # boundary
        pom_lamda = lambda ii: lambda: self._boundary_set(ii)
        self.boundary_label[layer_id] = QtWidgets.QLabel("Boundary:", self)
        self.boundary[layer_id] = QtWidgets.QCheckBox()
        self.boundary[layer_id].setChecked(region.boundary)
        self.boundary[layer_id].stateChanged.connect(pom_lamda(layer_id)) 
        grid.addWidget(self.boundary_label[layer_id], 4, 0)
        grid.addWidget(self.boundary[layer_id], 4, 1)
        
        # not use
        pom_lamda = lambda ii: lambda: self._not_used_set(ii)
        self.notused_label[layer_id] = QtWidgets.QLabel("Not Use:", self)
        self.notused[layer_id] = QtWidgets.QCheckBox()
        self.notused[layer_id].setChecked(region.not_used)
        self.notused[layer_id].stateChanged.connect(pom_lamda(layer_id)) 
        grid.addWidget(self.notused_label[layer_id], 5, 0)
        grid.addWidget(self.notused[layer_id], 5, 1)

        # mesh step
        action = lambda l_id: lambda: self._mesh_step_set(l_id)
        mesh_step_label = QtWidgets.QLabel("Mesh step:", self)
        mesh_step_edit = QtWidgets.QLineEdit()
        mesh_step_edit.setMinimumWidth(80)
        mesh_step_edit.setMaximumWidth(80)

        mesh_step_edit.setText(str(region.mesh_step))
        validator = QtGui.QDoubleValidator()
        validator.setRange(0.0, 1e+7, 7)     # assuming unit in meters and dimesion fo the whole earth :-)
        mesh_step_edit.setValidator(validator)
        mesh_step_edit.editingFinished.connect(action(layer_id))
        self.mesh_step_label[layer_id] = mesh_step_label
        self.mesh_step[layer_id] = mesh_step_edit
        grid.addWidget(mesh_step_label, 6, 0)
        grid.addWidget(mesh_step_edit, 6, 1)



        self._set_visibility(layer_id, region.dim!=RegionDim.none)
        sp1 =  QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Expanding)
        sp2 =  QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Expanding)
        grid.addItem(sp1, 7, 0)
        grid.addItem(sp2, 7, 1)
        
        widget = QtWidgets.QWidget(self)        
        widget.setLayout(grid)
        
        return widget

    def _set_visibility(self, layer_id, visible):
        """Set visibility for not NONE items"""
        self.name[layer_id].setReadOnly(not visible)
        self.color_label[layer_id].setVisible(visible)
        self.color_button[layer_id].setVisible(visible)
        self.dim_label[layer_id].setVisible(visible)
        self.dims[layer_id].setVisible(visible)
        self.boundary_label[layer_id].setVisible(visible)
        self.boundary[layer_id].setVisible(visible)
        self.notused_label[layer_id].setVisible(visible)
        self.notused[layer_id].setVisible(visible)
        self.mesh_step_label[layer_id].setVisible(visible)
        self.mesh_step[layer_id].setVisible(visible)

    def _add_disply_region(self, region):
        """Add new region to all combo and display it"""
        label = region.name + " (" + AddRegionDlg.REGION_DESCRIPTION_DIM[region.dim] + ")"
        for region_widget in self.regions.values():
            region_widget.addItem(label, region.reg_id)
        layer_id = self.layers_id[self.currentIndex()]
        self._update_layer_controls(region, layer_id)
        self.last_region[layer_id] = region.name
        
    def _update_layer_controls(self, region, layer_id):
        """Update set region data in layers controls"""

        region_id = region.reg_id
        curr_index = self.regions[layer_id].findData(region_id)

        # old_emit_regionChanged is used due to recursive call of _update_layer_controls
        old_emit_regionChanged = self._emit_regionChanged
        self._emit_regionChanged = False
        self.regions[layer_id].setCurrentIndex(curr_index)
        self._emit_regionChanged = old_emit_regionChanged

        self.name[layer_id].setText(region.name)
        self.dims[layer_id].setText(str(region.dim.value) + "D")
        pixmap = QtGui.QPixmap(25, 25)
        pixmap.fill(QtGui.QColor(region.color))
        iconPix = QtGui.QIcon(pixmap)
        self.update_region_data = True
        self.color_button[layer_id].setIcon(iconPix)
        self.boundary[layer_id].setChecked(region.boundary)
        self.notused[layer_id].setChecked(region.not_used)
        self.mesh_step[layer_id].setText(str(region.mesh_step))
        self.update_region_data = False
        self._set_visibility(layer_id, region.dim!=RegionDim.none)
            
    def _add_region(self):
        """Add new region to all combo and select it in current layer"""

        dlg = AddRegionDlg(self.layer_heads.max_selected_dim, self.layer_heads.region_names, self)
        ret = dlg.exec_()
        if ret==QtWidgets.QDialog.Accepted:
            name = dlg.region_name.text()
            dim = dlg.region_dim.currentData()
            color = dlg.get_some_color(self.regions_data._get_available_reg_id()-1).name()
            region = self.regions_data.add_new_region(color, name, dim, True, "Add Region")
            self._add_disply_region(region)
            layer_id = self.layers_id[self.currentIndex()]
            self._region_set(layer_id)




    def _remove_region(self):
        """Remove region if it is not assigned to any no shapes"""
        reg_idx = self.get_current_region()
        shapes = self.regions_data.get_shapes_of_region(reg_idx)
        if not shapes:
            self.regions_data.delete_region(reg_idx)
            for layer_id in self.regions_data.layers_topology[self.regions_data.current_topology_id]:
                self.regions[layer_id].removeItem(reg_idx)
                reg_id = self.regions[layer_id].currentData()
                self._update_layer_controls(self.regions_data.regions[reg_id], layer_id)
        else:
            print("List is not empty! Oops, this button should have been disabled.")

    def _name_set(self, layer_id):
        """Name is changed"""
        if self.update_region_data:
            return
        region_id = self.regions[layer_id].currentData()
        region = self.regions_data.regions[region_id]
        error = None
        for reg in self.regions_data.regions.values():
            if reg != region:
                if self.name[layer_id].text() == reg.name:
                    error = "Region name already exist"
                    break
            else:
                if self.name[layer_id].text() == reg.name:
                    return
        if len(self.name[layer_id].text())==0 or self.name[layer_id].text().isspace():
            error = "Region name is empty"
        if error is not None:
            err_dialog = GMErrorDialog(self)
            err_dialog.open_error_dialog(error)
            self.name[layer_id].selectAll()
        else:
            self.regions_data.set_region_name([key for key, item in self.regions_data.regions.items() if item == region][0],
                self.name[layer_id].text(), True, "Set region name")
            combo_text = self.name[layer_id].text()+" ("+str(self.regions_data.regions[region_id].dim.value)+"D)"
            self.regions[layer_id].setItemText(
                self.regions[layer_id].currentIndex(), combo_text)
                
    def _set_box_title(self, id, layer_id, layer_name):
        region_id = self.regions[layer_id].currentData()
        region = self.regions_data.regions[region_id]
        pixmap = QtGui.QPixmap(16, 16)
        color = QtGui.QColor("#f0f0e8")
        if region.color!="##":
            color = QtGui.QColor(region.color)
        pixmap.fill(color)
        iconPix = QtGui.QIcon(pixmap)
        self.setItemText(id, layer_name + " (" + region.name + ")")
        self.setItemIcon(id, iconPix)
            
    def _color_set(self, layer_id):
        """Region color is changed, refresh diagram"""
        if self.update_region_data:
            return
        region_id = self.regions[layer_id].currentData()
        region = self.regions_data.regions[region_id]
        color_dia = QtWidgets.QColorDialog(QtGui.QColor(region.color))
        i = 0
        for color in AddRegionDlg.BACKGROUND_COLORS:
            color_dia.setCustomColor(i,  color)            
            i += 1
        selected_color = color_dia.getColor() 
        if selected_color.isValid():
            pixmap = QtGui.QPixmap(16, 16)
            pixmap.fill(selected_color)
            iconPix = QtGui.QIcon(pixmap)
            self.color_button[layer_id].setIcon(iconPix)
            
            self.regions_data.regions.set_region_color(region_id,
                selected_color.name(), True, "Set Color")
            self.colorChanged.emit()
            self._set_box_title(self.currentIndex(), layer_id)
            
    def _region_set(self, layer_id):
        """Region in combo box was changed"""
        regions = self.regions_data
        region_id = self.regions[layer_id].currentData()
        region = regions.regions[region_id]
        self._update_layer_controls(region, layer_id)
        self.last_region[layer_id] = region.name

        self.layer_heads.select_region(layer_id, region_id)
        tab_id = self.layers_id.index(layer_id)
        layer_name = dict(self.layer_heads.layer_names)[layer_id]
        self._set_box_title(tab_id, layer_id, layer_name)
        if self._emit_regionChanged:
            self.regionChanged.emit()
        self.update_regions_panel()
        
    def _not_used_set(self, layer_id):
        """Region not used property is changed"""
        if self.update_region_data:
            return
        region_id = self.regions[layer_id].currentData()
        self.regions_data.set_region_not_used(region_id, self.notused[layer_id].isChecked(),
            True, "Set region usage")

    def _boundary_set(self, layer_id):
        """Region boundary property is changed"""
        if self.update_region_data:
            False
        region_id = self.regions[layer_id].currentData()
        self.regions_data.set_region_boundary(region_id, self.boundary[layer_id].isChecked(),
            True, "Set region boundary")

    def _mesh_step_set(self, layer_id):
        if self.update_region_data:
            return
        step_value = float(self.mesh_step[layer_id].text())
        region_id = self.regions[layer_id].currentData()
        self.regions_data.set_region_mesh_step(region_id, step_value,
            True, "Set region mesh step")


    def _layer_changed(self):
        """Next layer tab is selected"""
        if self.removing_items:
            return
        index = self.currentIndex()
        if index == -1:
           return 
        layer_id = self.layers_id[index]
        self.layer_heads.select_layer(layer_id)
        self.last_layer[self.layer_heads.current_topology_id] = index
        self.regionChanged.emit()

    def get_current_region(self):
        """Return current region id"""
        index = self.currentIndex()
        layer_id = self.layers_id[index]
        return self.regions[layer_id].currentData()
