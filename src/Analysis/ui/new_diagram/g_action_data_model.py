from PyQt5 import QtCore
from .tree_model import TreeModel


class GActionData:
    NAME = 0
    X = 1
    Y = 2
    WIDTH = 3
    HEIGHT = 4


class GActionDataModel(TreeModel):
    def __init__(self, data="", parent=None):
        super(GActionDataModel, self).__init__(['object_name', 'x', 'y', 'width', 'height'], data, parent)
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
            if child.data(GActionData.NAME) == action_name:
                return True
            if self.exists(action_name, self.index(child.child_number(), GActionData.NAME, parent)):
                return True
        return False

    def move(self, item, x, y):
        if x is not None:
            index_x = self.index(item.child_number(), GActionData.X)
            self.setData(index_x, x)
        if y is not None:
            index_y = self.index(item.child_number(), GActionData.Y)
            self.setData(index_y, y)

    def name_changed(self, item, name):
        index = self.index(item.child_number(), GActionData.NAME)
        self.setData(index, name)

    def width_changed(self, item, width):
        index = self.index(item.child_number(), GActionData.WIDTH)
        self.setData(index, width)

    def height_changed(self, item, height):
        index = self.index(item.child_number(), GActionData.HEIGHT)
        self.setData(index, height)