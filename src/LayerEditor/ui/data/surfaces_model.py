from LayerEditor.ui.data.abstract_model import AbstractModel
from LayerEditor.ui.data.surface_item import SurfaceItem
from LayerEditor.ui.tools import undo
from LayerEditor.ui.tools.id_map import IdMap


class SurfacesModel(AbstractModel):
    def __init__(self):
        super(SurfacesModel, self).__init__()


    def deserialize(self, data):
        with undo.pause_undo():
            for surface in data:
                self.add(SurfaceItem.create_from_data(surface))

    def sorted_items_elevation(self):
        return self.sorted_items(key=lambda x: x.elevation, reverse=True)

