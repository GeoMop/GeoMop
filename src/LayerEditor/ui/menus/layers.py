"""Layers panel contex menus"""

from PyQt5.QtWidgets import QMenu, QAction
from leconfig import cfg

class LayersLayerMenu(QMenu):
    """
    Contex Menu with layer actions
    """

    def __init__(self, layers_panel, layer_idx):
        """Initializes the class."""
        super(LayersLayerMenu, self).__init__(layers_panel)
        self.layers_panel = layers_panel
        """Layers panel"""
        self.layer_idx = layer_idx
        """Selected layer index"""
        
        self._add_interface_action = QAction('Add Interface ...', self)
        self._add_interface_action.setStatusTip('Split lyaer by new interface')
        self._add_interface_action.triggered.connect(self._add_interface)
        self.addAction(self._add_interface_action)

        self._rename_action = QAction('Rename ...', self)
        self._rename_action.setStatusTip('Rename this lyaer')
        self._rename_action.triggered.connect(self._rename)
        self.addAction(self._rename_action)

        self._remove_action = QAction('Remove', self)
        self._remove_action.setStatusTip('Remove this lyaer and add shadow block instead')
        self._remove_action.triggered.connect(self._remove)
        self.addAction(self._remove_action)
 
    def _add_interface(self):
        """Split layer by new interface"""
        self.layers_panel.add_interface(self.layer_idx)

    def _rename(self):
        """Rename layer"""
        self.layers_panel.rename_layer(self.layer_idx)
        
    def _remove(self):
        """Remove layer and add shadow block instead"""
        self.layers_panel.remove_layer(self.layer_idx)
        
class LayersInterfaceMenu(QMenu):
    """
    Contex Menu with interface actions. 
    """

    def __init__(self, layers_panel, interface_idx):
        """Initializes the class."""
        super(LayersInterfaceMenu, self).__init__(layers_panel)
        self.layers_panel = layers_panel
        """Layers panel"""
        self.interface_idx = interface_idx
        """Selected interface index"""
        
        d = cfg.layers
        
        self._add_fracture_action = QAction('Add Fracture ...', self)
        self._add_fracture_action.setStatusTip('Add fracture to this interface')
        self._add_fracture_action.triggered.connect(self._add_fracture)
        self.addAction(self._add_fracture_action)
        
        self._change_type_action = QAction('Change Type ...', self)
        self._change_type_action.setStatusTip('Change interface type')
        self._change_type_action.triggered.connect(self._change_type)
        self.addAction(self._change_type_action)

        self._set_depth_action = QAction('Set Depth ...', self)
        self._set_depth_action.setStatusTip('Set interface depth')
        self._set_depth_action.triggered.connect(self._set_depth)
        self.addAction(self._set_depth_action)
        
        if interface_idx==len(d.interfaces)-1:
            self._append_layer_action = QAction('Append Layer ...', self)
            self._append_layer_action.setStatusTip('Append lyaer to the end')
            self._append_layer_action.triggered.connect(self._append_layer)
            self.addAction(self._append_layer_action)
        
        self._remove_interface_action = QAction('Remove Interface', self)
        self._remove_interface_action.setStatusTip('Remove this interface')
        self._remove_interface_action.triggered.connect(self._remove_interface)
        self.addAction(self._remove_interface_action)
        
        self._remove_fracture_action = QAction('Remove Fracture', self)
        self._remove_fracture_action.setStatusTip('Remove fracture from this interface')
        self._remove_fracture_action.triggered.connect(self._remove_fracture)
        self.addAction(self._remove_fracture_action)
        
    def _add_fracture(self):
        """Add fracture to interface"""
        self.layers_panel.remove_interface(self.interface_idx)
        
    def _change_type(self):
        """Change interface type"""
        self.layers_panel.change_interface_type(self.interface_idx)
        
    def _set_depth(self):
        """Change interface type"""
        self.layers_panel.set_interface_depth(self.interface_idx)
        
    def _append_layer(self):
        """Append layer to the end"""
        self.layers_panel.append_layer()    
        
    def _remove_interface(self):
        """Remove interface and merge layers"""
        self.layers_panel.remove_interface(self.interface_idx)
        
    def _remove_fracture(self):
        """Remove layer and add shadow block instead"""
        self.layers_panel.remove_fracture(self.interface_idx)
        
class LayersFractuceMenu(QMenu):
    """
    Contex Menu with fracture actions. 
    """

    def __init__(self, layers_panel, interface_idx):
        """Initializes the class."""
        super(LayersInterfaceMenu, self).__init__(layers_panel)
        self.layers_panel = layers_panel
        """Layers panel"""
        self.interface_idx = interface_idx
        """Selected interface index"""
        
        self._rename_fracture_action = QAction('Rename Fracture ...', self)
        self._rename_fracture_action.setStatusTip('Rename this fracture')
        self._rename_fracture_action.triggered.connect(self._rename_fracture)
        self.addAction(self._rename_fracture_action)
        
        self._remove_fracture_action = QAction('Remove Fracture', self)
        self._remove_fracture_action.setStatusTip('Remove this fracture')
        self._remove_fracture_action.triggered.connect(self._remove_fracture)
        self.addAction(self._remove_fracture_action)
        
    def _rename_fracture(self):
        """Rename fracture to interface"""
        self.layers_panel.remove_interface(self.interface_idx)
        
    def _remove_fracture(self):
        """Remove layer and add shadow block instead"""
        self.layers_panel.remove_fracture(self.interface_idx)
