from LayerEditor.ui.data.region import Region
from LayerEditor.ui.tools.id_map import IdMap


class RegionsModel:
    """Class for managing all regions"""
    NONE = None
    def __init__(self, le_data, regions_data):
        self.regions = IdMap() # {region: Region}
        self.le_data = le_data
        """Needed for checking if some region is used in any shape in any decomposition"""


        for data in regions_data:
            self.add_region_from_data(data)
        Region.none = self.regions.get(0)

    def add_region_from_data(self, region_data):
        Region( self.regions,
                region_data.color,
                region_data.name,
                region_data.dim,
                region_data.mesh_step,
                region_data.boundary)

    #TODO: Make undoable, maybe?
    def add_region(self, name="", dim=0, color=None):
        reg = Region(self.regions, color=color, name=name, dim=dim)
        return reg

    # TODO: Make undoable, maybe?
    def delete_region(self, reg):
        for block in self.le_data.blocks.values():
            for layer in block.layers:
                if layer.gui_selected_region == reg:
                    layer.gui_selected_region = Region.none
        del self.regions[reg]

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

    def is_region_used(self, reg):
        dim = self.regions[reg].dim
        for block in self.le_data.blocks.values():
            for layer in block.layers:
                if not layer.is_fracture:
                    dim -= 1
                    if dim < 0:
                        continue
                if reg in layer.shape_regions[dim].values():
                    return True
        return False

    def save(self, geo_model):
        regions_data = []
        id_to_idx = {}
        for idx, region in enumerate(self.regions.values()):
            regions_data.append(region.convert_to_data())
            id_to_idx[region.id] = idx
        geo_model.geometry.regions = regions_data
        return id_to_idx

