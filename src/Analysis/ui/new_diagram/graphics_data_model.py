from .tree_model import TreeModel


class ActionData:
    NAME = 0
    ACTION_TYPE = 1
    X = 2
    Y = 3
    WIDTH = 4
    HEIGTH = 5


class ActionDataModel(TreeModel):
    def __init__(self, data="", parent=None):
        super(ActionDataModel, self).__init__(['object_name', 'action_type', 'x', 'y', 'width', 'height'], data, parent)
        self._max_id = 0

    def add_item(self, action_type, x, y, width_hint, height_hint, id=None):
        if id is None:
            self._max_id += 1
        elif id > self._max_id:
            self._max_id = id
        else:
            raise ValueError

        data = ["Action" + str(self._max_id), action_type, x, y, width_hint, height_hint]
        self.insertRows(self.rowCount(), 1)
        item = self.get_item().child(self.rowCount() - 1)
        for column in range(self.column_count()):
            index = self.index(self.rowCount() - 1, column)
            self.setData(index, data[column])

    def move(self, item, x, y):
        index_x = self.index(item.child_number(), ActionData.X)
        index_y = index_x.siblingAtColumn(ActionData.Y)

        self.setData(index_x, x)
        self.setData(index_y, y)

    def name_changed(self, item, name):
        index = self.index(item.child_number(), ActionData.NAME)
        self.setData(index, name)

    def width_changed(self, item, width):
        index = self.index(item.child_number(), ActionData.WIDTH)
        self.setData(index, width)

    def height_changed(self, item, height):
        index = self.index(item.child_number(), ActionData.HEIGTH)
        self.setData(index, height)


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

