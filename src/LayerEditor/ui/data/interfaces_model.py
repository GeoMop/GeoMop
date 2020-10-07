from bgem.external import undo

from LayerEditor.ui.data.interface_item import InterfaceItem
from LayerEditor.ui.tools.id_map import IdMap


class InterfacesModel:
    def __init__(self, interfaces_data: list):
        self.interfaces = IdMap()
        for itf in interfaces_data:
            self.interfaces.add(InterfaceItem(itf))



