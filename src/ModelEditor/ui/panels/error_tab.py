"""Error widget panel

.. codeauthor:: Pavel Richter <pavel.richter@tul.cz>
"""
import icon
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
from meconfig import cfg
from helpers import Notification


class ErrorWidget(QtWidgets.QListWidget):
    """Widget displays a list of error messages.

    pyqtSignals:
        * :py:attr:`itemSelected(int, int, int, int) <itemSelected>`
    """
    itemSelected = QtCore.pyqtSignal(int, int, int, int)
    """Signal is sent when error item is clicked.

    :param int start_line: Line where the error begins.
    :param int start_column: Column where the error begins.
    :param int end_line: Line where the error ends.
    :param int end_column: Column where the error ends.
    """

    def __init__(self, parent=None):
        """Initialize the class."""
        super(ErrorWidget, self).__init__(parent)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.currentItemChanged.connect(self._current_item_changed)
        self._load_items()

    def select_error(self, line):
        """Select error according to line number.

        If there are multiple errors on the line, the first match is selected.

        :param int line: Line number in editor.
        """
        for row in range(0, self.count()):
            item = self.item(row)
            data = item.data(QtCore.Qt.UserRole)
            if data.span.start.line == line:
                self.setCurrentItem(item)
                break

    def reload(self):
        """Start of reload data from config."""
        self.clear()
        self._load_items()

    def _load_items(self):
        """Load errors from config."""
        for error in cfg.notifications:
            if error.severity == Notification.Severity.fatal:
                item = QtWidgets.QListWidgetItem(
                    icon.get_icon("fatal", 24), str(error))
            elif error.severity == Notification.Severity.error:
                item = QtWidgets.QListWidgetItem(
                    icon.get_icon("error", 24), str(error))
            elif error.severity == Notification.Severity.warning:
                item = QtWidgets.QListWidgetItem(
                    icon.get_icon("warning", 24), str(error))
            else:
                item = QtWidgets.QListWidgetItem(
                    icon.get_icon("information", 24), str(error))
            item.setData(QtCore.Qt.UserRole, error)
            self.addItem(item)

    def _current_item_changed(self, current, previous):
        """Handle :py:attr:`currentItemChanged` signal."""
        if current is None:
            return
        data = current.data(QtCore.Qt.UserRole)
        self.itemSelected.emit(data.span.end.line, data.span.end.column,
                               data.span.start.line, data.span.start.column)
