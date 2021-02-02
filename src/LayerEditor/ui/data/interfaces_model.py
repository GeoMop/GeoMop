from LayerEditor.ui.data.abstract_model import AbstractModel
from LayerEditor.ui.tools import undo

from LayerEditor.ui.data.interface_item import InterfaceItem


class InterfacesModel(AbstractModel):
    def deserialize(self, interfaces, surfaces_model):
        """ Initializes model with data from format_last.py"""
        with undo.pause_undo():
            for itf in interfaces:
                surface = surfaces_model[itf.surface_id] if itf.surface_id is not None else None
                if itf.transform_z is not None and itf.elevation is not None and itf.elevation != itf.transform_z[1]:
                    print("Elevation inconsistency! Elevation doesn't match transform_z!" +
                          " Choosing elevation as correct value.")
                    itf.transform_z = (itf.transform_z[0], itf.elevation)
                self.add(InterfaceItem.create_from_data(itf.transform_z, surface))





