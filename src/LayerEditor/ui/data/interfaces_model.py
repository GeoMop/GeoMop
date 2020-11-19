from LayerEditor.ui.tools import undo

from LayerEditor.ui.data.interface_item import InterfaceItem

class InterfacesModel:
    def __init__(self, le_model, interfaces_data: list):
        self.interfaces = []
        for itf in interfaces_data:
            surface = le_model.surfaces_model.surfaces[itf.surface_id] if itf.surface_id is not None else None
            self.interfaces.append(InterfaceItem(itf.elevation, itf.transform_z, surface,))

    def save(self):
        interfaces_data = []
        for idx, interface in enumerate(self.interfaces):
            interfaces_data.append(interface.save())
            interface.index = idx
        return interfaces_data

    def clear_indexing(self):
        for interface in self.interfaces:
            interface.index = None

    @undo.undoable
    def insert_after(self, new_itf: InterfaceItem, after_itf: InterfaceItem):
        idx = self.interfaces.index(after_itf) + 1
        self.interfaces.insert(idx, new_itf)
        yield f"Add interface, elevation: {new_itf.elevation}"
        del self.interfaces[idx]

    @undo.undoable
    def delete_itf(self, itf):
        idx = self.interfaces.index(itf)
        del self.interfaces[idx]
        yield "Delete Interface"
        self.interfaces.insert(idx, itf)

