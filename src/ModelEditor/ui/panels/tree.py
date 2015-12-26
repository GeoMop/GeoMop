"""
Tree widget panel

.. codeauthor:: Pavel Richter <pavel.richter@tul.cz>
.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""
import os
from copy import deepcopy

import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
from PyQt5.QtGui import QColor

from geomop_util import load_stylesheet
from meconfig import cfg
from data import DataNode


class TreeWidget(QtWidgets.QTreeView):
    """Widget displays the config file structure in a tree.

    pyqtSignals:
        * :py:attr:`itemSelected(int, int, int, int) <itemSelected>`
    """

    itemSelected = QtCore.pyqtSignal(int, int, int, int)
    """Signal is sent when a tree item is clicked.

    :param int start_line: Line where the error begins.
    :param int start_column: Column where the error begins.
    :param int end_line: Line where the error ends.
    :param int end_column: Column where the error ends.
    """

    def __init__(self, parent=None):
        """Initialize the class."""
        super(TreeWidget, self).__init__(parent)
        self.showColumn(3)
        self._model = DataNodeTreeModel(cfg.root)
        self.setModel(self._model)
        self.setMinimumSize(250, 400)
        self.setMaximumWidth(450)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.clicked.connect(self._item_clicked)
        self.collapsed.connect(self._item_collapsed)
        self.expanded.connect(self._item_expanded)
        self._item_states = {}
        self.setRootIsDecorated(True)
        self.setIndentation(10)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        stylesheet_path = os.path.join(cfg.stylesheet_dir, 'tree.css')
        cfg.logger.info('tree.css path: {0}, resource dir: {1}'.format(stylesheet_path,
                                                                       cfg.resource_dir))
        stylesheet = load_stylesheet(stylesheet_path, cfg.resource_dir)
        self.setStyleSheet(stylesheet)

    def reload(self):
        """Start of reload data from config."""
        self._model = DataNodeTreeModel(cfg.root)
        self.setModel(self._model)
        self._restore_expanded()

    def _restore_expanded(self, item=None):
        """Restore expanded state after init."""
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
        """Handle itemCollapsed signal."""
        path = model_index.internalPointer().absolute_path
        self._item_states[path] = False

    def _item_expanded(self, model_index):
        """Handle itemExpanded signal."""
        path = model_index.internalPointer().absolute_path
        self._item_states[path] = True

    def _item_clicked(self, model_index):
        """Handle itemClicked signal."""
        data = model_index.internalPointer()
        if model_index.column() == 0 and data.key.span is not None:  # key
            span = deepcopy(data.key.span)
        elif model_index.column() == 1 and \
                data.implementation == DataNode.Implementation.mapping and \
                data.type is not None:  # AbstractRecord type
            span = deepcopy(data.type.span)
        else:  # entire node (value)
            span = deepcopy(data.span)
            # if an array is clicked, select the "- " as well
            if model_index.column() == 0:
                is_array_member = (data.parent is not None and
                                   data.parent.implementation == DataNode.Implementation.sequence)
                has_delimiters = data.is_flow is False and data.delimiters is not None
                if is_array_member and has_delimiters:
                    span.start = data.delimiters.start

        if span.start is not None and span.end is not None:
            self.itemSelected.emit(span.start.line, span.start.column,
                                   span.end.line, span.end.column)

    def select_data_node(self, data_node):
        """Mark data node as selected in the tree.

        :param DataNode data_node: data node to be selected
        """
        row = NodeHelper.row(data_node)
        if row is None:
            return
        index = self._model.createIndex(row, 0, data_node)
        self.selectionModel().select(index, QtCore.QItemSelectionModel.ClearAndSelect)
        self.scrollTo(index, QtWidgets.QAbstractItemView.PositionAtCenter)

    def resizeEvent(self, event):
        """Adjust column size on resize."""
        super(TreeWidget, self).resizeEvent(event)
        width = int(event.size().width() * 60/100)
        self.setColumnWidth(0, width)

    def sizeHint(self):
        """Return the preferred size of widget."""
        return QtCore.QSize(300, 800)


class DataNodeTreeModel(QtCore.QAbstractItemModel):
    """Item model for PyQt tree containing :py:class:`DataNode <data.data_node.DataNode>`."""

    def __init__(self, root):
        """Initialize the class.

        :param DataNode root: root data node of the tree
        """
        super(DataNodeTreeModel, self).__init__(None)
        self.root = root
        self.headers = ["key", "value"]

    def index(self, row, column, parent):
        """Return index used to access data by the view.

        :param int row: row to create the index for
        :param int column: not really relevant, the tree item handles this
        :param QModelIndex parent: parent this index should be created under
        :return: index to access the data
        :rtype: QModelIndex
        """
        if not parent.isValid():
            parent = self.root
        else:
            parent = parent.internalPointer()
        if parent is None:
            return QtCore.QModelIndex()
        child = NodeHelper.get_child(parent, row)
        if child is None:
            return QtCore.QModelIndex()
        return self.createIndex(row, column, child)

    def parent(self, child):
        """Create a parent index based on a child index.

        :param QModelIndex child: index of the child to get the parent from
        :return: index of parent
        :rtype: QModelIndex
        """
        if not child.isValid():
            return QtCore.QModelIndex()
        child = child.internalPointer()
        if child is None:
            return QtCore.QModelIndex()
        parent = NodeHelper.get_parent(child)
        if parent is None:
            return QtCore.QModelIndex()
        if NodeHelper.get_parent(parent) is None:
            return QtCore.QModelIndex()
        row = NodeHelper.row(parent)
        if row is None:
            return QtCore.QModelIndex()
        return self.createIndex(row, 0, parent)

    # virtual function
    # pylint: disable=R0201
    def data(self, index, role):
        """Extract data for the index and role.

        :param QModelIndex index: index to extract the data from
        :param DisplayRole role: data access role the view requests from the model
        :return: requested data
        """
        column = index.column()
        data = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            return NodeHelper.data(data, column)
        elif role == QtCore.Qt.SizeHintRole:
            return QtCore.QSize(120, 20)
        elif role == QtCore.Qt.ForegroundRole:
            if column == 1:
                if data.implementation == DataNode.Implementation.mapping and data.type is not None:
                    return QColor(QtCore.Qt.darkGreen)  # AbstractRecord type
                return QColor(QtCore.Qt.black)

    # virtual function
    # pylint: disable=C0103
    def rowCount(self, index):
        """Return the amount of rows for a given index.

        :param QModelIndex index: index of the node
        :return: amount of rows
        :rtype: int
        """
        if not index.isValid():
            node = self.root
        else:
            node = index.internalPointer()
        if node is None:
            return 0
        return NodeHelper.count_child_rows(node)

    # virtual function
    # pylint: disable=W0613
    def columnCount(self, index):
        """Return the amount of columns for a given index.

        :param QModelIndex index: the index
        :return: amount of columns
        :rtype: int
        """
        return 2

    def headerData(self, section, orientation, role):
        """Return header parameters.

        :param int section: number of the column
        :param orientation: orientation of the header
        :param DisplayRole role: display role for the data
        :return: header data
        :rtype: QVariant
        """
        if(orientation == QtCore.Qt.Horizontal and
           role == QtCore.Qt.DisplayRole):
            if 0 <= section <= len(self.headers):
                return QtCore.QVariant(self.headers[section])
        return QtCore.QVariant()


class NodeHelper:
    """Contains helper functions for transforming `DataNode` to model structure."""

    @staticmethod
    def get_parent(node):
        """Return parent of the node.

        :param DataNode node: node to get the parent of
        :return: parent of the node
        :rtype: DataNode
        """
        return node.parent

    @staticmethod
    def row(node):
        """Return row index of the node.

        :param DataNode node: node to get the row index of
        :return: index of the node in its parent
        :rtype: int or None
        """
        if node.parent and node in node.parent.visible_children:
            return node.parent.visible_children.index(node)
        return None

    @staticmethod
    def count_child_rows(node):
        """Return the amount of children for the node.

        :param DataNode node: parent node of the children
        :return: amount of children the node has
        :rtype: int
        """
        return len(node.visible_children)

    @staticmethod
    def get_child(node, row):
        """Return a child node at a given row.

        :param DataNode node: parent node
        :param int row: index of the child
        :return: child node
        :rtype: DataNode or None
        """
        if len(node.visible_children) > row:
            return node.visible_children[row]
        return None

    @staticmethod
    def data(node, column):
        """Return text displayed in tree.

        The first column displays keys. The second column displays values.

        :param DataNode node: node to extract the text from
        :param int column: index of the column
        :return: text to display
        :rtype: str
        """
        if column == 0:
            return node.key.value
        if column == 1:
            if node.implementation == DataNode.Implementation.scalar:
                return str(node.value)
            elif node.implementation == DataNode.Implementation.mapping and node.type is not None:
                return str(node.type.value)
        return ""
