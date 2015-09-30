"""Tree widget panel module"""
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
from PyQt5.QtGui import QColor
from data.meconfig import MEConfig as cfg
from data import ScalarNode, CompositeNode
import util


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

    def __init__(self, parent=None):
        super(TreeWidget, self).__init__(parent)
        self.showColumn(3)
        self._model = TreeOfNodes(cfg.root)
        self.setModel(self._model)
        self.setMinimumSize(350, 450)
        self.setColumnWidth(0, 190)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.clicked.connect(self._item_clicked)
        self.collapsed.connect(self._item_collapsed)
        self.expanded.connect(self._item_expanded)
        self._item_states = {}
        self.setRootIsDecorated(True)
        self.setIndentation(10)
        stylesheet = util.load_stylesheet('tree')
        self.setStyleSheet(stylesheet)

    def reload(self):
        """start of reload data from config"""
        self._model = TreeOfNodes(cfg.root)
        self.setModel(self._model)
        self._restore_expanded()

    def _restore_expanded(self, item=None):
        """restore expanded state after init"""
        if item is None:
            item = QtCore.QModelIndex()
        for i in range(0, self._model.rowCount(item)):
            child = self._model.index(i, 0, item)
            path = child.internalPointer().absolute_path
            if path in self._item_states:
                if self._item_states[path]:
                    self.expand(child)
                else:
                    self.collapse(child)
            else:
                self.expand(child)
                self._item_states[path] = True
            self._restore_expanded(child)

    def _item_collapsed(self, model_index):
        """Function for itemColapsed signal"""
        path = model_index.internalPointer().absolute_path
        self._item_states[path] = False

    def _item_expanded(self, model_index):
        """Function for itemExpanded signal"""
        path = model_index.internalPointer().absolute_path
        self._item_states[path] = True

    def _item_clicked(self, model_index):
        """Function for itemSelected signal"""
        data = model_index.internalPointer()
        if model_index.column() == 0 and data.key.span is not None:  # key
            span = data.key.span
        elif (model_index.column() == 1 and isinstance(data, CompositeNode) and
                  data.type is not None):  # AbstractRecord type
            span = data.type.span
        else:  # entire node (value)
            span = data.span
            # if an array is clicked, select the "- " as well
            is_array_member = (data.parent is not None and
                               isinstance(data.parent, CompositeNode) and
                               data.parent.explicit_keys is False)
            has_delimiters = data.is_flow is False and data.delimiters is not None
            if is_array_member and has_delimiters:
                span = data.delimiters

        self.itemSelected.emit(span.start.column, span.start.line,
                               span.end.column, span.end.line)

    def select_data_node(self, data_node):
        """Sets the selection to the given `DataNode`."""
        row = Node.row(data_node)
        index = self._model.createIndex(row, 0, data_node)
        self.selectionModel().select(index, QtCore.QItemSelectionModel.ClearAndSelect)
        self.scrollTo(index, QtWidgets.QAbstractItemView.PositionAtCenter)


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
        child = Node.get_child(parent, row)
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
        column = node.column()
        data = node.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            return Node.data(data, column)
        elif role == QtCore.Qt.SizeHintRole:
            return QtCore.QSize(120, 20)
        elif role == QtCore.Qt.ForegroundRole:
            if column == 1 and isinstance(data, CompositeNode) and data.type is not None:
                return QColor(QtCore.Qt.darkMagenta)  # AbstractRecord type
            return QColor(QtCore.Qt.black)

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
            if 0 <= section <= len(self.headers):
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
        if isinstance(node.parent, CompositeNode):
            return node.parent.children.index(node)
        return None

    @staticmethod
    def count_child_rows(node):
        """return count of children for node"""
        if isinstance(node, CompositeNode):
            return len(node.children)
        return 0

    @staticmethod
    def get_child(node, row):
        """return child in row row for node"""
        if isinstance(node, CompositeNode):
            if len(node.children) > row:
                return node.children[row]
        return None

    @staticmethod
    def data(node, column):
        """return text displayed in tree in set column for node"""
        if column == 0:
            return node.key.value
        if column == 1:
            if isinstance(node, ScalarNode):
                return str(node.value)
            elif isinstance(node, CompositeNode) and node.type is not None:
                return str(node.type.value)
        return ""
