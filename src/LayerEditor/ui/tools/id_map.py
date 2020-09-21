"""Copied from bgem and modified"""

class IdObject:

    def __init__(self):
        self.id = None

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return "{}: Id {}".format(self.__class__.__name__, self.id)


class IdSource:
    pass

class IdMap():
    def __init__(self):
        self._dict = {}
        self._next_id = -1
        # Source of new object IDs. The last used ID.
        self._free_ids = []
        # List of free ids
        super().__init__()


    def get_new_id(self):
        if self._free_ids:
            return self._free_ids.pop()
        self._next_id += 1
        return self._next_id

    def add(self, obj):
        id = self.get_new_id()
        obj.id = id
        self._dict[obj.id] = obj
        return obj

    def remove(self, obj):
        del self._dict[obj.id]
        self._free_ids.append(obj.id)

    def get(self, id):
        return self._dict[id]

    def values(self):
        return self._dict.values()

    def __getitem__(self, item):
        return self.get(item.id)

    def __delitem__(self, key):
        self.remove(key)