from .tree_model import TreeModel


class ActionDataModel(TreeModel):
    def __init__(self, data="", parent=None):
        super(ActionDataModel, self).__init__(['id', 'action_type', 'x', 'y', 'width_hint', 'height_hint'], data, parent)
        self._max_id = 0

    def add_item(self, action_type, x, y, width_hint, height_hint, id=None):
        if id is None:
            self._max_id += 1
        elif id > self._max_id:
            self._max_id = id
        else:
            raise ValueError

        data = [self._max_id, action_type, x, y, width_hint, height_hint]
        self.insertRows(self.rowCount(), 1)
        item = self.get_item().child(self.rowCount() - 1)
        for column in range(self.column_count()):
            index = self.index(self.rowCount() - 1, column)
            self.setData(index, data[column])

    def move(self, item, x, y):
        index_x = self.index(item.child_number(), 2)
        index_y = index_x.siblingAtColumn(3)

        self.setData(index_x, x)
        self.setData(index_y, y)


class ConnectionDataModel(TreeModel):
    def __init__(self, data="", parent=None):
        super(ConnectionDataModel, self).__init__(['id1', 'port1', 'id2', 'port2'], data, parent)

    def add_item(self, id1, port1, id2, port2):
        data = [id1, port1, id2, port2]
        self.insertRows(self.rowCount(), 1)
        item = self.get_item().child(self.rowCount() - 1)
        for column in range(self.column_count()):
            index = self.index(self.rowCount() - 1, column)
            self.setData(index, data[column])

