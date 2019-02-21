
class TreeItem:
    def __init__(self, data, parent_item=None):
        self._child_items = []
        self._item_data = data
        self._parent_item = parent_item

    def column_count(self):
        len(self._item_data)

    def child(self, number):
        return self._child_items[number]

    def child_count(self):
        return len(self._child_items)

    def data(self, column):
        return self._item_data[column]

    def insert_children(self, position, count):
        if position < 0 or position > len(self._child_items):
            return False

        for row in range(count):
            data = [None]*4
            self._child_items.insert(position, TreeItem(data, self))
        return True

    def insert_columns(self, position, columns):
        if position < 0 or position > len(self._item_data):
            return False

        for column in range(columns):
            self._item_data.insert(position, None)

        for child in self._child_items:
            child.insert_columns(position, columns)

        return True

    def parent(self):
        return self._parent_item

    def remove_children(self, position, count):
        if position < 0 or position + count > len(self._child_items):
            return False

        del self._child_items[position:position + count]
        return True

    def remove_columns(self, position, columns):
        if position < 0 or position + columns > len(self._item_data):
            return False

        del self._item_data[position, position + columns]

        for child in self._child_items:
            child.remove_columns(position, columns)

        return True

    def child_number(self):
        if self._parent_item:
            return self._parent_item._child_items.index(self)
        else:
            return 0

    def set_data(self, column, value):
        if column < 0 or column >= len(self._item_data):
            return False
        self._item_data[column] = value
        return True

