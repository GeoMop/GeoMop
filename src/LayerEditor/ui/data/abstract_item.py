from LayerEditor.ui.tools.id_map import IdObject


class AbstractItem(IdObject):
    def __init__(self):
        super(AbstractItem, self).__init__()
        self.index = None
        """Reserved for referencing by index while saving. Should be cleared back to None after saving is finished"""

    @classmethod
    def create_from_data(cls, *args):
        item = cls()
        item.deserialize(*args)
        return item

    def deserialize(self, *args):
        assert False, "Abstract function! Must be overridden by child class!"

    def serialize(self):
        assert False, "Abstract function! Must be overridden by child class!"
