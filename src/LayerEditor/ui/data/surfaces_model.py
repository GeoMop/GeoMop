from LayerEditor.ui.data.surface_item import SurfaceItem
from LayerEditor.ui.tools.id_map import IdMap


class SurfacesModel:
    def __init__(self, surfaces_list):
        self.surfaces = []
        for surface in surfaces_list:
            self.surfaces.append(SurfaceItem(surface))

    def save(self):
        surfaces = []
        for idx, surface in enumerate(self.surfaces):
            surfaces.append(surface.save())
            surface.index = idx
        return surfaces

    def clear_indexing(self):
        for surface in self.surfaces:
            surface.index = None