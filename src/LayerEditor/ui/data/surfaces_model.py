from LayerEditor.ui.data.surface_item import SurfaceItem
from LayerEditor.ui.tools import undo
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

    @undo.undoable
    def add_surface(self, surf):
        self.surfaces.append(surf)
        yield "Add Surface"
        self.surfaces.remove(surf)

    @undo.undoable
    def replace_surface(self, idx, surf):
        old_surf = self.surfaces[idx]
        self.surfaces[idx] = surf
        yield "Replace Surface"
        self.surfaces[idx] = old_surf
