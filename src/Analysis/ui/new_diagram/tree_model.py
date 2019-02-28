from PyQt5 import QtCore
from .tree_item import TreeItem


class TreeModel(QtCore.QAbstractItemModel):
    def __init__(self, headers, data="", parent=None):
        super(TreeModel, self).__init__(parent)
        self._root_item = TreeItem(headers)
        self.setup_model_data(data.split("\n"), self._root_item)
        self._columns = len(headers)

    def get_item(self, index):
        if index.isValid():
            item = index.internal_pointer()
            if item:
                return item

        return self._root_item

    def column_count(self):
        return self._root_item.column_count()

    def data(self, index, role = QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        if role != QtCore.Qt.DisplayRole and role != QtCore.Qt.EditRole:
            return None

        item = self.get_item(index)
        return item.data(index.column())

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._root_item.data(section)

        return None

    def index(self, row, column, parent=QtCore.QModelIndex()):
        if not parent.isValid() and parent.column() != 0:
            return QtCore.QModelIndex()

        parent_item = self.get_item(parent)
        child_item = parent_item.child(row)
        if child_item:
            return self.createIndex(row, column, child_item)
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        child_item = self.get_item(index)
        parent_item = child_item.parent()
        if parent_item == self._root_item:
            return QtCore.QModelIndex()
        return self.createIndex(parent_item.child_number(), 0, parent_item)

    def rowCount(self, parent=QtCore.QModelIndex()):
        parent_item = self.get_item(parent)
        return parent_item.child_count()

    def columnCount(self, parent=QtCore.QModelIndex()):
        return self._root_item.column_count()

    def flags(self, index):
        if index.isValid():
            return QtCore.Qt.ItemIsEditable | QtCore.QAbstractItemModel.flags(index)
        else:
            return QtCore.Qt.NoItemFlags

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role != QtCore.Qt.EditRole:
            return False

        item = self.get_item(index)
        result = item.set_data(index.column(), value)

        if result:
            self.dataChanged.emit(index, index, [role])

        return result

    def setHeaderData(self, section, orientation, value, role=QtCore.Qt.EditRole):
        if role != QtCore.Qt.EditRole or orientation != QtCore.Qt.Horizontal:
            return False

        result = self._root_item.set_data(section, value)

        if result:
            self.headerDataChanged.emit(orientation, section, section)

        return result

    def insertColumns(self, position, columns, parent=QtCore.QModelIndex()):
        self.beginInsertColumns(parent, position, position + columns - 1)
        success = self._root_item.insert_columns(position, columns)
        self.endInsertColumns()

        return success

    def removeColumns(self, position, columns, parent=QtCore.QModelIndex()):
        self.beginRemoveColumns(position, columns, parent)
        success = self._root_item.remove_columns(position, columns)
        self.endRemoveColumns()

        if self._root_item.column_count() == 0:
            self.removeRows(0, self.rowCount())

        return success

    def insertRows(self, position, rows, parent=QtCore.QModelIndex()):
        parent_item = self.get_item(parent)

        self.beginInsertRows(parent, position, position + rows - 1)
        success = parent_item.insert_children(position, rows, self._root_item.column_count())
        self.endInsertRows()

        return success

    def removeRows(self, position, rows, parent=QtCore.QModelIndex()):
        parent_item = self.get_item(parent)
        self.beginRemoveRows(parent, position, position + rows - 1)
        success = parent_item.remove_children(position, rows)
        self.endRemoveRows()

        return success

    def setup_model_data(self, lines, parent):
        parents = [parent]
        indentation = [0]

        number = 0

        while number < len(lines):
            position = 0
            while position < len(lines[number]):
                if lines[number][position] != ' ':
                    break
                position += 1

            line_data = lines[number][position:].strip()

            if line_data:
                # Read the column data from the rest of the line.
                column_string = list(filter(bool, line_data.split('\t')))
                column_data = []
                for column in range(len(column_string)):
                    column_data.append(column_string[column])

                if position > indentation[-1]:
                    # The last child of the current parent is now the new parent
                    # unless the current parent has no children.
                    if parents[-1].child_count() > 0:
                        parents.append(parents[-1].child(parents[-1].child_count() - 1))
                        indentation.append(position)
                else:
                    while position < indentation[-1] and len(parents) > 0:
                        del parents[-1]
                        del indentation[-1]

                # Append a new item to the current parent's list of children.
                parent = parents[-1]
                parent.insert_children(parent.child_count(), 1, self._root_item.column_count())
                for column in range(len(column_data)):
                    parent.child(parent.child_count() - 1).set_data(column, column_data[column])

            number += 1

if __name__ == "__main__":
    import sys
    from PyQt5 import QtWidgets
    app = QtWidgets.QApplication(sys.argv)
    with open("test.txt",'r') as file:
        text = file.read()
    print(text)
    model = TreeModel(['c1','c2','c3'], text)
    index = model.index(1, 1)
    model.insertRows(0, 2, index)

    w = QtWidgets.QTreeView()
    w.setModel(model)
    w.setWindowTitle('Simple')
    w.show()

    sys.exit(app.exec_())
