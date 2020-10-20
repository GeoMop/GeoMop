from bgem.external import undo

from LayerEditor.ui.data.region_item import RegionItem
from LayerEditor.ui.tools.id_map import IdMap


class RegionsModel:
    """Class for managing all regions"""
    NONE = None
    def __init__(self, regions_data):
        self.regions = IdMap()  # {region_id: Region}
        """Needed for checking if some region is used in any shape in any decomposition"""

        for data in regions_data:
            self.copy_region_from_data(data)
        RegionItem.none = self.regions.get(0)

    def copy_region_from_data(self, region_data):
        reg = RegionItem(region_data.color,
                         region_data.name,
                         region_data.dim,
                         region_data.mesh_step,
                         region_data.not_used,
                         region_data.boundary,
                         region_data.brep_shape_ids)
        self.regions.add(reg)

    @undo.undoable
    def add_region(self, name="", dim=0, color=None):
        reg = RegionItem(color=color, name=name, dim=dim)
        self.regions.add(reg)
        yield "Add new Region", reg
        self.delete_region(reg)

    @undo.undoable
    def delete_region(self, reg: RegionItem):
        del self.regions[reg]
        yield "Delete Region"
        self.copy_region_from_data(reg)

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

    def save(self):
        regions_data = []
        for idx, region in enumerate(self.regions.values()):
            regions_data.append(region.save())
            region.index = idx
        return regions_data

    def clear_indexing(self):
        for region in self.regions.values():
            region.index = None