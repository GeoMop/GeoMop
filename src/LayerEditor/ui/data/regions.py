from LayerEditor.ui.data.region import Region


class Regions:
    def __init__(self):
        self.regions = {Region.none.id: Region.none}

    def add_region(self, color=None, name="", dim=0):
        reg = Region(id=None, color=color, name=name, dim=dim)
        self.regions[reg.id] = reg
        return reg.id

    def delete_region(self, id):
        del self.regions[id]

    def get_region_names(self):
        return [reg.name for reg in self.regions.values()]


    # def get_common_region(self):
    #     selected = self._diagram.selection._selected
    #     r_id = Region.none.id
    #     if selected:
    #         r_id = self.get_shape_region(self._diagram.get_shape_key(selected[0]))
    #         for item in selected[1:]:
    #             if self.get_shape_region(self._diagram.get_shape_key(item)) != r_id:
    #                 r_id = Region.none.id
    #     return r_id

    # def set_region(self, dim, shape_id, reg_id):
    #     if dim != self.regions[reg_id].dim:
    #         return False
    #
    #     if reg_id is None:
    #         reg_id = Region.none.id
    #
    #     if dim == 1:
    #         self._diagram.decomposition.points[shape_id].attr = reg_id
    #     elif dim == 2:
    #         self._diagram.decomposition.segments[shape_id].attr = reg_id
    #     elif dim == 3:
    #         self._diagram.decomposition.polygons[shape_id].attr = reg_id
    #
    #     return True

    # def is_region_used(self, reg_id):
    #     dim = self.regions[reg_id].dim
    #     elements = []
    #     if dim == 1:
    #         elements = self._diagram.decomposition.points.values()
    #     elif dim == 2:
    #         elements = self._diagram.decomposition.segments.values()
    #     elif dim == 3:
    #         elements = self._diagram.decomposition.polygons.values()
    #
    #     for el in elements:
    #         if reg_id == el.attr:
    #             return True
    #
    #     return False
