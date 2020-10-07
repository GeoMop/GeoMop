from LayerEditor.ui.tools.id_map import IdObject
from gm_base.geometry_files.format_last import Surface


class SurfaceItem(IdObject):
    def __init__(self, surf_data: Surface):
        self.surf_data = surf_data