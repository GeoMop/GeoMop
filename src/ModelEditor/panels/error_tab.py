"""Error widget panel module"""
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
from data.meconfig import MEConfig as cfg
import data.data_node as dn

class ErrorWidget(QtWidgets.QListWidget):
    """
    List widget for viewing errors messages

    Events:
        :ref:`item_selected <item_selected>`
    """
    itemSelected = QtCore.pyqtSignal(int, int, int, int)
    """
    .. _item_selected:
    Sgnal is sent when error item is clicked.
    """

    def __init__(self):
        QtWidgets.QListWidget.__init__(self)
        self.clicked.connect(self._item_clicked)

    def reload(self):
        """start of reload data from config"""
 
    def _item_clicked(self, model_index):
        """Function for itemSelected signal"""
        item = self.currentItem()
        data = item.data()
        if(model_index.column() == 0 and
           data.key.section is not None):
            self.itemSelected.emit(data.key.section.start.column,
                                   data.key.section.start.line,
                                   data.key.section.end.column,
                                   data.key.section.end.line)
        else:
            self.itemSelected.emit(data.span.start.column, data.span.start.line,
                                   data.span.end.column, data.span.end.line)
