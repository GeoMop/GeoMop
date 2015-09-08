"""Error widget panel module"""

# pylint: disable=no-member

import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
from data.meconfig import MEConfig as cfg
import data.data_node as dn
import icon

class ErrorWidget(QtWidgets.QListWidget):
    """
    List widget for viewing errors messages

    Events:
        :ref:`item_selected <item_selected>`
    """
    itemSelected = QtCore.pyqtSignal(int, int, int, int)
    """
    .. _item_selected:
    Signal is sent when error item is clicked.
    """

    def __init__(self):
        QtWidgets.QListWidget.__init__(self)
        self.clicked.connect(self._item_clicked)
        self._load_items()

    def select_error(self, line):
        """Select error according line number"""
        for row in range(0, self.count()):
            item = self.item(row)
            data = item.data(QtCore.Qt.UserRole)
            if data.span.start.line == line:
                item.setSelected(True)
                break

    def reload(self):
        """start of reload data from config"""
        self.clear()
        self._load_items()

    def _load_items(self):
        """load errors"""
        for error in cfg.errors:
            if error.severity == dn.DataError.Severity.fatal:
                item = QtWidgets.QListWidgetItem(
                    icon.get_icon("fatal", 24), error.title + ": " + error.description)
            elif error.severity == dn.DataError.Severity.error:
                item = QtWidgets.QListWidgetItem(
                    icon.get_icon("error", 24), error.title + ": " + error.description)
            elif error.severity == dn.DataError.Severity.warning:
                item = QtWidgets.QListWidgetItem(
                    icon.get_icon("warning", 24), error.title + ": " + error.description)
            else:
                item = QtWidgets.QListWidgetItem(
                    icon.get_icon("information", 24), error.title + ": " + error.description)
            item.setData(QtCore.Qt.UserRole, error)
            self.addItem(item)

    def _item_clicked(self, model_index):
        """Function for itemSelected signal"""
        item = self.currentItem()
        data = item.data(QtCore.Qt.UserRole)
        self.itemSelected.emit(data.span.start.column, data.span.start.line,
                               data.span.end.column, data.span.end.line)
