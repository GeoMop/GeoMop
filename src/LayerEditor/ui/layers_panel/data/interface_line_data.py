from LayerEditor.ui.data.interpolated_node_set_item import InterpolatedNodeSetItem
from LayerEditor.ui.layers_panel.wg_interface import InterfaceType


class InterfaceLineData:
    """Helper data object for better readability of LayersPanel initialization"""
    def __init__(self, interface, fracture=None):
        self.i_node_set = interface
        self.fracture = fracture
        self.type = InterfaceType.NONE
        self.interpolated = isinstance(interface, InterpolatedNodeSetItem)



