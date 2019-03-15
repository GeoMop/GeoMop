from PyQt5 import QtCore
from .tree_model import TreeModel


class ActionData:
    NAME = 0
    X = 1
    Y = 2
    WIDTH = 3
    HEIGHT = 4


class ActionDataModel(TreeModel):
    def __init__(self, data="", parent=None):
        super(ActionDataModel, self).__init__(['object_name', 'x', 'y', 'width', 'height'], data, parent)
        self._max_id = 0

    def add_item(self, x, y, width_hint, height_hint, action_name=None):
        action_name = "Action" if action_name is None else action_name
        if self.exists(action_name):
            append_number = 1
            while self.exists(action_name + str(append_number)):
                append_number += 1

            action_name = action_name + str(append_number)

        data = [action_name, x, y, width_hint, height_hint]
        self.insertRows(self.rowCount(), 1)
        item = self.get_item().child(self.rowCount() - 1)
        for column in range(self.column_count()):
            index = self.index(self.rowCount() - 1, column)
            self.setData(index, data[column])

    def exists(self, action_name, parent=QtCore.QModelIndex()):
        for child in self.get_item(parent).children():
            if child.data(ActionData.NAME) == action_name:
                return True
            if self.exists(action_name, self.index(child.child_number(),ActionData.NAME, parent)):
                return True
        return False

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
        index = self.index(item.child_number(), ActionData.HEIGHT)
        self.setData(index, height)


class ConnectionData:
    ID1 = 0
    PORT1 = 1
    ID2 = 2
    PORT2 = 3


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

    def action_name_changed(self, action_data, new_name, parent=QtCore.QModelIndex()):
        prev_name = action_data.data(ActionData.NAME)
        for child in self.get_item(parent).children():
            if child.data(ConnectionData.ID1) == prev_name:
                child.set_data(ConnectionData.ID1, new_name)
            if child.data(ConnectionData.ID2) == prev_name:
                child.set_data(ConnectionData.ID2, new_name)
            parent_index = self.index(child.child_number(), ConnectionData.ID1)
            self.action_name_changed(action_data, new_name, parent_index)




