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
    def add_region(self, reg):
        self.regions.add(reg)
        yield "Add new Region"
        self.delete_region(reg)

    @undo.undoable
    def delete_region(self, reg):
        del self.regions[reg]
        yield "Delete Region"
        self.add_region(reg)

    def get_region_names(self):
        return [reg.name for reg in self.regions.values()]

    def save(self):
        regions_data = []
        for idx, region in enumerate(self.regions.values()):
            regions_data.append(region.save())
            region.index = idx
        return regions_data

    def clear_indexing(self):
        for region in self.regions.values():
            region.index = None