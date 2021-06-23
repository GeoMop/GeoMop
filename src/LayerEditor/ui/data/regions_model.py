from LayerEditor.ui.data.abstract_model import AbstractModel
from LayerEditor.ui.tools import undo

from LayerEditor.ui.data.region_item import RegionItem
from LayerEditor.ui.tools.id_map import IdMap


class RegionsModel(AbstractModel):
    """Class for managing all regions"""
    def deserialize(self, data):
        with undo.pause_undo():
            for reg_data in data:
                reg = RegionItem.create_from_data(reg_data)
                self.add(reg)
            RegionItem.none = self.collection.get(0)

    def get_region_names(self):
        return [reg.name for reg in self.items()]