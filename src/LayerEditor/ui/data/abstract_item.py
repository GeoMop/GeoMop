from LayerEditor.ui.tools.id_map import IdObject


class AbstractItem(IdObject):
    def __init__(self):
        super(AbstractItem, self).__init__()
        self.index = None
        """Reserved for referencing by index while saving. Should be cleared back to None after saving is finished"""

    def save(self):
        assert False, "Abstract function! Must be overridden by child class!"

