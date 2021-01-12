from LayerEditor.ui.tools import undo
from LayerEditor.ui.tools.id_map import IdMap, IdObject


class AbstractModel(IdMap):
    def __init__(self):
        super(AbstractModel, self).__init__()

    @staticmethod
    def initialize(data):
        assert False, "Abstract function! Must be overridden by child class!"

    def save(self):
        items = []
        for idx, item in enumerate(self.values()):
            items.append(item.save())
            item.index = idx
        return items

    def clear_indexing(self):
        for item in self.values():
            item.index = None

    @undo.undoable
    def add(self, item: IdObject):
        self.add(item)
        yield "Add Item"
        self.delete(item)

    @undo.undoable
    def delete(self, item: IdObject):
        self.remove(item)
        yield "Delete Item"
        self.add(item)

