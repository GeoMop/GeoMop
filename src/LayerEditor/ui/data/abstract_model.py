from LayerEditor.ui.tools import undo
from LayerEditor.ui.tools.id_map import IdMap, IdObject


class AbstractModel:
    def __init__(self):
        super(AbstractModel, self).__init__()
        self.collection = IdMap()

    @classmethod
    def create_from_data(cls, *args):
        model = cls()
        model.deserialize(*args)
        return model

    def deserialize(self, *data):
        assert False, "Abstract function! Must be overridden by child class!"

    def serialize(self):
        items = []
        for idx, item in enumerate(self.items()):
            items.append(item.serialize())
            item.index = idx
        return items

    def clear_indexing(self):
        for item in self.items():
            item.index = None

    def sorted_items(self, key=lambda x: x, reverse=False):
        r = list(self.items())
        r.sort(key=key, reverse=reverse)
        return r

    def items(self):
        return self.collection.values()

    @undo.undoable
    def add(self, item: IdObject):
        self.collection.add(item)
        yield "Add Item"
        self.collection.remove(item)

    @undo.undoable
    def remove(self, item: IdObject):
        self.collection.remove(item)
        yield "Delete Item"
        self.collection.add(item)

    def __len__(self):
        return len(self.collection)

    def __getitem__(self, key):
        return self.collection.get(key)





