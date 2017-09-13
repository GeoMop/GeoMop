import PyQt5.QtWidgets as QtWidgets
from leconfig import cfg
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui

from ui.dialogs.regions import AddRegionDlg


class Regions(QtWidgets.QToolBox):
    """
    GeoMop regions panel
    
    pyqtSignals:
        * :py:attr:`regionColorChanged(int) <regionColorChanged>`
    """
    
    regionColorChanged = QtCore.pyqtSignal(int)
    """Signal is sent when region collor is changes.
    
    :param int idx: changed region index"""

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
        self._show_layers()
        
    def set_topology(self, top_idx):
        """Set current topology, and refresh layer view"""
        self.topology_idx = top_idx
        self._show_layers()
        
    def _show_layers(self):
        """Refresh layers view"""
        data = cfg.diagram.regions
        layers = data.get_layers(self.topology_idx)
        self.regions = {}
        self.add_button = {}
        self.color_button = {}
        self.name = {}
        self.boundary = {}
        self.notuse = {}
        
        for layer_id in layers:
            grid = QtWidgets.QGridLayout(self)             
            # select and add region
            self.regions[layer_id] = QtWidgets.QComboBox()            
            for i in range(0, len(data.regions)):
                label = data.regions[i].name + " (" + str(data.regions[i].dim.value) + "D)"
                self.regions[layer_id].addItem( label,  i)
            curr_index = 0
            self.regions[layer_id].setCurrentIndex(curr_index) 
            
            pom_lamda = lambda ii: lambda: self.add_Region(ii)      
            self.add_button[layer_id] = QtWidgets.QPushButton("Add Region")
            self.add_button[layer_id].clicked.connect(pom_lamda(i))            
                  
            grid.addWidget(self.regions[layer_id], 0, 0)
            grid.addWidget(self.add_button[layer_id], 0, 1)
            
            # name
            name_label = QtWidgets.QLabel("Name:", self)            
            self.name[layer_id] = QtWidgets.QLineEdit()
            self.name[layer_id].setText(data.regions[curr_index].name)            
            grid.addWidget(name_label, 1, 0)
            grid.addWidget(self.name[layer_id], 1, 1)
            
            #color button
            color_label = QtWidgets.QLabel("Color:", self)
            pom_lamda = lambda ii, button: lambda: self.color_set(ii, button)
            self.color_button[layer_id] = QtWidgets.QPushButton()
            pixmap = QtGui.QPixmap(25, 25)
            pixmap.fill(QtGui.QColor(data.regions[curr_index].color))
            icon = QtGui.QIcon(pixmap)
            self.color_button[layer_id].setIcon(icon)
            self.color_button[layer_id].setFixedSize( 25, 25 )
            self.color_button[layer_id]
            self.color_button[layer_id].clicked.connect(pom_lamda(i, self.color_button[layer_id]))
            grid.addWidget(color_label, 2, 0)
            grid.addWidget(self.color_button[layer_id], 2, 1)
            
            # dimension
            dim_label = QtWidgets.QLabel("Dimension:", self)
            dim = QtWidgets.QLabel(str(data.regions[curr_index].dim.value) + "D", self)
            grid.addWidget(dim_label, 3, 0)
            grid.addWidget(dim, 3, 1)
            
            # boundary
            boundary_label = QtWidgets.QLabel("Boundary:", self)
            self.boundary[layer_id] = QtWidgets.QCheckBox()            
            grid.addWidget(boundary_label, 4, 0)
            grid.addWidget(self.boundary[layer_id], 4, 1)
            
            # not use
            notuse_label = QtWidgets.QLabel("Not Use:", self)
            self.notuse[layer_id] = QtWidgets.QCheckBox()            
            grid.addWidget(notuse_label, 5, 0)
            grid.addWidget(self.notuse[layer_id], 5, 1)
            
            widget = QtWidgets.QWidget(self)
            widget.setLayout(grid);
            self.addItem(widget, layers[layer_id])
            
    def add_Region(self, i):
        """Add new region to all combo and select it in layer i"""
        dlg = AddRegionDlg(cfg.main_window)
        ret = dlg.exec_()
        if ret==QtWidgets.QDialog.Accepted:
            name = dlg.region_name.text()
            dim = dlg.region_dim.currentData()
            color = dlg.get_some_color(i)
        
        
            
    def color_set(self, region_idx, color_button):
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
        self.regionColorChanged.emit()

