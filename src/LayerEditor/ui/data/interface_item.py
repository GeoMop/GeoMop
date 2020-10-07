from LayerEditor.ui.tools.id_map import IdObject
from gm_base.geometry_files.format_last import Interface


class InterfaceItem(IdObject):
    def __init__(self, itf_data: Interface):
        super(InterfaceItem, self).__init__()
        self.itf_data = itf_data

