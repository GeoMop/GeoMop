import PyQt5.QtWidgets as QtWidgets
from leconfig import cfg
import PyQt5.QtGui as QtGui
from geomop_dialogs import GMErrorDialog
from ui.dialogs.regions import AddRegionDlg


class Regions(QtWidgets.QToolBox):
    """
    GeoMop regions panel
    """

    def __init__(self, parent=None):
        """
        Inicialize window

        Args:
            parent (QWidget): parent window ( empty is None)
        """
        super(Regions, self).__init__(parent)
        self.topology_idx = 0
        """Current topology idx"""
        self.layer_idx = 0
        """Current topology idx"""
        self.last_layer = {}
        """Last edited layer in topology (topology_id:layer_name)"""        
        self.last_region = {}
        """Last edited region in topology (layer_name:region_name)"""
        self._show_layers()        
        self.currentChanged.connect(self._layer_changed)
        
    def release_all(self):
        """Remove all items"""
        for i in range(self.count()-1, -1, -1):
            widget = self.widget(i)
            self.removeItem(i)            
            widget.setParent(None)            
    
    def set_topology(self, top_idx):
        """Set current topology, and refresh layer view"""
        self.release_all()
        self.topology_idx = top_idx
        self._show_layers()
        data = cfg.diagram.regions
        data.current_layer_id
        
    def select_current_regions(self, regions):
        """Select current regions in topology"""
        data = cfg.diagram.regions
        for i in range(0, len(regions)):
            layer_id = data.layers_topology[self.topology_idx][i]
            new_index = self.regions[layer_id].findData(data.regions.index(regions[i]))            
            self.regions[layer_id].setCurrentIndex(new_index)
        
    def _show_layers(self):
        """Refresh layers view"""
        data = cfg.diagram.regions                
        self.layers = data.get_layers(self.topology_idx)
        data.current_topology_id = self.topology_idx
        self.regions = {}
        self.dims = {}
        self.add_button = {}
        self.color_button = {}
        self.name = {}
        self.boundary = {}
        self.notused = {}
        self.layers_id = []
        for layer_id in self.layers:
            self.layers_id.append(layer_id) 
            widget = self._add_region_panel(layer_id, self._get_last_region(layer_id))
            self.addItem(widget, self.layers[layer_id])
        layer_id = self._get_last_layer()
        self.setCurrentIndex(layer_id)
        data.current_layer_id = layer_id
        
    def _get_last_layer(self):
        """Return last layer_id"""
        data = cfg.diagram.regions
        if not self.topology_idx in self.last_layer:
            self.last_layer[self.topology_idx] = \
                self.last_layer[self.topology_idx] = data.layers[data.layers_topology[self.topology_idx][0]]
        if self.last_layer[self.topology_idx] in self.layers_id:
            index = self.last_layer[self.topology_idx]
        else:
            index = 0
            self.last_layer[self.topology_idx] = self.layers_id[0]
        return index
        
    def _get_last_region(self, layer_id):
        """Return last region_id"""
        data = cfg.diagram.regions
        if self.layers[layer_id] in self.last_region:
            region_name = self.last_region[self.layers[layer_id]]
        else:
            self.last_region[self.layers[layer_id]] =  data.regions[2].name
            return data.regions[2]
        for region in data.regions:
            if region.name == region_name:
                return region
        self.last_region[self.layers[layer_id]] =  data.regions[2].name
        return data.regions[2]

            
    def _add_region_panel(self, layer_id, region):
        """add one region panel to tool box and set regin data"""
        data = cfg.diagram.regions
        data.current_regions = {}
        grid = QtWidgets.QGridLayout()             
        # select and add region
        pom_lamda = lambda ii: lambda: self._region_set(ii)
        self.regions[layer_id] = QtWidgets.QComboBox()            
        for i in range(0, len(data.regions)):            
            label = region.name + " (" + str(data.regions[i].dim.value) + "D)"
            self.regions[layer_id].addItem( label,  i) 
            data.current_regions[layer_id] = region
        curr_index = self.regions[layer_id].findData(data.regions.index(region))    
        self.regions[layer_id].setCurrentIndex(curr_index) 
        self.regions[layer_id].currentIndexChanged.connect(pom_lamda(layer_id))
        read_only =  region.name[0:5] == "NONE_"
        
        self.add_button[layer_id] = QtWidgets.QPushButton("Add Region")
        self.add_button[layer_id].clicked.connect(self._add_region)            
              
        grid.addWidget(self.regions[layer_id], 0, 0)
        grid.addWidget(self.add_button[layer_id], 0, 1)
        
        # name
        pom_lamda = lambda ii: lambda: self._name_set(ii)
        name_label = QtWidgets.QLabel("Name:", self)            
        self.name[layer_id] = QtWidgets.QLineEdit()
        self.name[layer_id].setText(region.name)
        self.name[layer_id].setReadOnly(read_only)
        self.name[layer_id].editingFinished.connect(pom_lamda(layer_id))
        grid.addWidget(name_label, 1, 0)
        grid.addWidget(self.name[layer_id], 1, 1)
        
        #color button
        color_label = QtWidgets.QLabel("Color:", self)
        pom_lamda = lambda ii, button: lambda: self._color_set(ii, button)
        self.color_button[layer_id] = QtWidgets.QPushButton()
        pixmap = QtGui.QPixmap(25, 25)
        pixmap.fill(QtGui.QColor(region.color))
        icon = QtGui.QIcon(pixmap)
        self.color_button[layer_id].setIcon(icon)
        self.color_button[layer_id].setFixedSize( 25, 25 )
        self.color_button[layer_id].clicked.connect(pom_lamda(i, self.color_button[layer_id]))
        grid.addWidget(color_label, 2, 0)
        grid.addWidget(self.color_button[layer_id], 2, 1)
        
        # dimension
        dim_label = QtWidgets.QLabel("Dimension:", self)
        self.dims[layer_id] = QtWidgets.QLabel(str(region.dim.value) + "D", self)
        grid.addWidget(dim_label, 3, 0)
        grid.addWidget(self.dims[layer_id], 3, 1)
        
        # boundary
        pom_lamda = lambda ii: lambda: self._boundary_set(ii)
        boundary_label = QtWidgets.QLabel("Boundary:", self)
        self.boundary[layer_id] = QtWidgets.QCheckBox()
        self.boundary[layer_id].setEnabled(not read_only)
        self.boundary[layer_id].setChecked(region.boundary)
        self.boundary[layer_id].stateChanged.connect(pom_lamda(layer_id)) 
        grid.addWidget(boundary_label, 4, 0)
        grid.addWidget(self.boundary[layer_id], 4, 1)
        
        # not use
        pom_lamda = lambda ii: lambda: self._not_used_set(ii)
        notuse_label = QtWidgets.QLabel("Not Use:", self)
        self.notused[layer_id] = QtWidgets.QCheckBox()
        self.notused[layer_id].setEnabled(not read_only)
        self.notused[layer_id].setChecked(region.not_used)
        self.notused[layer_id].stateChanged.connect(pom_lamda(layer_id)) 
        grid.addWidget(notuse_label, 5, 0)
        grid.addWidget(self.notused[layer_id], 5, 1)
        sp1 =  QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Expanding)
        sp2 =  QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Expanding)
        grid.addItem(sp1, 6, 0)
        grid.addItem(sp2, 6, 1)
        
        widget = QtWidgets.QWidget(self)        
        widget.setLayout(grid)
        
        return widget
        
    def _update_layer_controls(self, region):
        """Update set region data in layers controls"""
        data = cfg.diagram.regions
        layer_id = self.layers_id[self.currentIndex()]        
        region_id = data.regions.index(region)
        curr_index = self.regions[layer_id].findData(region_id)
        self.regions[layer_id].setCurrentIndex(curr_index) 

        read_only =  data.regions[region_id].name[0:5] == "NONE_"
            
        self.name[layer_id].setText(region.name)
        self.name[layer_id].setReadOnly(read_only)
        self.dims[layer_id].setText(str(region.dim.value) + "D")
        pixmap = QtGui.QPixmap(25, 25)
        pixmap.fill(QtGui.QColor(region.color))
        icon = QtGui.QIcon(pixmap)
        self.color_button[layer_id].setIcon(icon)
        self.boundary[layer_id].setChecked(region.boundary) 
        self.boundary[layer_id].setEnabled(not read_only)
        self.notused[layer_id].setChecked(region.not_used)
        self.notused[layer_id].setEnabled(not read_only)
        
    def _add_disply_region(self, region):
        """Add new region to all combo and display it"""
        data = cfg.diagram.regions
        label = region.name + " (" + str(region.dim.value) + "D)"
        region_len = len(data.regions)
        for layer_id in self.layers:
            self.regions[layer_id].addItem( label, region_len-1)  
        self._update_layer_controls(region)
        layer_id = self.layers_id[self.currentIndex()]
        self.last_region[self.layers[layer_id]] = region.name        
            
    def _add_region(self):
        """Add new region to all combo and select it in current layer"""
        data = cfg.diagram.regions
        dlg = AddRegionDlg(cfg.main_window)
        ret = dlg.exec_()
        if ret==QtWidgets.QDialog.Accepted:
            name = dlg.region_name.text()
            dim = dlg.region_dim.currentData()
            color = dlg.get_some_color(len(data.regions))
            region = data.add_new_region(color, name, dim)
            self._add_disply_region(region)
            
    def _name_set(self, layer_id):
        """Name is changed"""
        data = cfg.diagram.regions
        region_id = self.regions[layer_id].currentData()
        region = data.regions[region_id]        
        error = None
        for reg in data.regions:
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
            data.set_region_name(data.regions.index(region), self.name[layer_id].text())
            combo_text = self.name[layer_id].text()+" ("+str(data.regions[region_id].dim.value)+"D)"
            self.regions[layer_id].setItemText(
                self.regions[layer_id].currentIndex(), combo_text)
            
    def _color_set(self, region_idx, color_button):
        """Region color is changed, refresh diagram"""
        region = cfg.diagram.regions.regions[region_idx]
        color_dia = QtWidgets.QColorDialog(QtGui.QColor(region.color))
        i = 0
        for color in AddRegionDlg.BACKGROUND_COLORS:
            color_dia.setCustomColor(i,  color)            
            i += 1
        selected_color = color_dia.getColor()        
        
        pixmap = QtGui.QPixmap(16, 16)
        pixmap.fill(selected_color)
        icon = QtGui.QIcon(pixmap)
        color_button.setIcon(icon)
        
        region.color = selected_color.name()
        cfg.diagram.region_color_changed(region_idx)
        
    def _region_set(self, layer_id):
        """Region in combo box was changed"""
        data = cfg.diagram.regions
        region_id = self.regions[layer_id].currentData()
        region = data.regions[region_id]
        self._update_layer_controls(region)
        self.last_region[self.layers[layer_id]] = region.name
        data.current_regions[layer_id] = region
        
    def _not_used_set(self, layer_id):
        """Region not used property is changed"""
        data = cfg.diagram.regions
        region_id = self.regions[layer_id].currentData()
        data.set_region_not_used(region_id, self.notused[layer_id].isChecked())

    def _boundary_set(self, layer_id):
        """Region boundary property is changed"""
        data = cfg.diagram.regions
        region_id = self.regions[layer_id].currentData()
        data.set_region_boundary(region_id, self.boundary[layer_id].isChecked())
        
    def _layer_changed(self):
        """Next layer tab is selected"""
        data = cfg.diagram.regions
        layer_id = self.layers_id[self.currentIndex()]
        data.current_layer_id = layer_id
