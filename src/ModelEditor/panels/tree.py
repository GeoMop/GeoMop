"""Tree widget panel module"""
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
from data.meconfig import MEConfig as cfg
import data.data_node as dn

class TreeWidget(QtWidgets.QTreeView):
    """
    Tree widget for viewing yaml file tree structure

    Events:
        :ref:`item_selected <item_selected>`
    """
    itemSelected = QtCore.pyqtSignal(int, int, int, int)
    """
    .. _item_selected:
    Sgnal is sent when  tree item is clicked.
    """

    def __init__(self):
        QtWidgets.QTreeView.__init__(self)
        self.showColumn(2)
        self._model = TreeOfNodes(cfg.root)
        self.setModel(self._model)
        self.setMinimumSize(150, 450)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.clicked.connect(self._item_clicked)

    def reload(self):
        """start of reload data from config"""
        self._model = TreeOfNodes(cfg.root)
        self.setModel(self._model)

    def _item_clicked(self, model_index):
        """Function for itemSelected signal"""
        data = model_index.internalPointer()
        if(model_index.column() == 0 and
           data.key.section is not None):
            self.itemSelected.emit(data.key.section.start.column,
                                   data.key.section.start.line,
                                   data.key.section.end.column,
                                   data.key.section.end.line)
        else:
            self.itemSelected.emit(data.span.start.column, data.span.start.line,
                                   data.span.end.column, data.span.end.line)

class TreeOfNodes(QtCore.QAbstractItemModel):
    """tree model structure"""
    def __init__(self, root):
        super(TreeOfNodes, self).__init__(None)
        self.root = root
        self.headers = ["key", "value"]

    def index(self, row, column, parent):
        """
        The index is used to access data by the view
        This method overrides the base implementation, needs to be overridden
        @param row: The row to create the index for
        @param column: Not really relevant, the tree item handles this
        @param parent: The parent this index should be created under
        """
        if not parent.isValid():
            parent = self.root
        else:
            parent = parent.internalPointer()
        if parent is None:
            return QtCore.QModelIndex()
        child = Node. get_child(parent, row)
        if child is None:
            return QtCore.QModelIndex()
        return self.createIndex(row, column, child)

    def parent(self, child):
        """
        creates an index for a parent based on a child index, and binds the data
        used by the view to get a parent (from a child)
        @param childindex: the index of the child to get the parent from
        """
        if not child.isValid():
            return QtCore.QModelIndex()
        child = child.internalPointer()
        if child is None:
            return QtCore.QModelIndex()
        parent = Node.get_parent(child)
        if parent is None:
            return QtCore.QModelIndex()
        if Node.get_parent(parent) is None:
            return QtCore.QModelIndex()
        row = Node.row(parent)
        if row is None:
            return QtCore.QModelIndex()
        return self.createIndex(row, 0, parent)

    # virtual function
    # pylint: disable=R0201
    def data(self, node, role):
        """
        The view calls this to extract data for the row and column
        associated with the parent object
        @param parentindex: the parentindex to extract the data from
        @param role: the data accessing role the view requests from the model
        """
        if role == QtCore.Qt.DisplayRole:
            column = node.column()
            node = node.internalPointer()
            return Node.data(node, column)
        if role == QtCore.Qt.SizeHintRole:
            return QtCore.QSize(120, 20)

    # virtual function
    # pylint: disable=C0103
    def rowCount(self, parent):
        """
        Returns the amount of rows a parent has
        This comes down to the amount of children associated with the parent
        @param parentindex: the index of the parent
        """
        if not parent.isValid():
            parent = self.root
        else:
            parent = parent.internalPointer()
        if parent is None:
            return 0
        return Node.count_child_rows(parent)

    # virtual function
    # pylint: disable=W0613
    def columnCount(self, parent):
        """
        Amount of columns associated with the parent index
        @param parentindex: the parent index object
        """
        return 2

    def headerData(self, section, orientation, role):
        """set header parameters"""
        if(orientation == QtCore.Qt.Horizontal and
           role == QtCore.Qt.DisplayRole):
            if 0 <= section and section <= len(self.headers):
                return QtCore.QVariant(self.headers[section])
        return QtCore.QVariant()

class Node:
    """
    Helper static class for transformation cfg root structure
    to model format
    """
    def __init__(self):
        pass

    @staticmethod
    def get_parent(node):
        """get parent"""
        return node.parent

    @staticmethod
    def row(node):
        """return row index for node"""
        if node.parent is None:
            return None
        if type(node.parent) == dn.ArrayNode:
            for i in range(0, len(node.parent.children)):
                if node.key.value == node.parent.children[i].key.value:
                    return i
            return None
        if type(node.parent) == dn.RecordNode:
            i = 0
            for child in node.parent.children:
                if node.key.value == node.parent.children[child].key.value:
                    return i
                i += 1
        return None

    @staticmethod
    def count_child_rows(node):
        """return count of children for node"""
        if type(node) == dn.ArrayNode:
            return len(node.children)
        if type(node) == dn.RecordNode:
            return len(node.children)
        return 0

    @staticmethod
    def get_child(node, row):
        """return child in row row for node"""
        if type(node) == dn.ArrayNode:
            if len(node.children) > row:
                return node.children[row]
            return None
        if type(node) == dn.RecordNode:
            i = 0
            for child in node.children:
                if i == row:
                    return node.children[child]
                i += 1
        return None

    @staticmethod
    def data(node, column):
        """return text displyed in tree in set column for node"""
        if column == 0:
            return node.key.value
        if type(node) == dn.ScalarNode and column == 1:
            return str(node.value)
        return ""
