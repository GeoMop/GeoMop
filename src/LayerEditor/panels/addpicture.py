# pylint: disable=E1002
"""AddPictureWidget file"""
import os
from copy import deepcopy
import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets
from lang_le import gettext as _

#default item for  picture list in format PATH, Name
_DEFAULT_LIST = [
    ["LAYER_BELOW", "LAYER ABOVE"], [_("Layer below"), _("Layer above")]]

class AddPictureWidget(QtWidgets.QWidget):
    """
    QWidget descendant enable selecting a undercoat for design area

    Events:
        :ref:`pictureListChanged <pictureListChanged>`
    """
    pictureListChanged = QtCore.pyqtSignal()
    """
    .. _pictureListChanged:
    Send Signal when  picture selection was changed. Call
    :ref:`get_picture_paths  function <get_picture_paths>` for
    new set of underlying pictures.
    """

    def __init__(self, parent=None):
        """
        Inicialize window

        Args:
            parent (QWidget): parent window ( empty is None)
        """
        super(AddPictureWidget, self).__init__(parent)

        self.setSizePolicy(QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        self.setMinimumSize(QtCore.QSize(200, 500))

        self._list = deepcopy(_DEFAULT_LIST)

        self._list_widget = QtWidgets.QListWidget()
        self._init_list()

        self._add_button = QtWidgets.QPushButton(_("Add"))
        self._add_button.clicked.connect(self._add_item)
        self._delete_button = QtWidgets.QPushButton(_("Delete"))
        self._delete_button.clicked.connect(self._delete_item)

        grid = QtWidgets.QGridLayout()
        grid.addWidget(self._add_button, 0, 0)
        grid.addWidget(self._delete_button, 0, 1)

        self._file_name = QtWidgets.QLineEdit()
        self._file_button = QtWidgets.QPushButton("...")
        self._file_button.clicked.connect(self._add_picture)

        _file_layeout = QtWidgets.QHBoxLayout()
        _file_layeout.addWidget(self._file_name)
        _file_layeout.addWidget(self._file_button)

        label = QtWidgets.QLabel(_("Picture File:"))

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self._list_widget)
        layout.addLayout(grid)
        layout.addWidget(label)
        layout.addLayout(_file_layeout)
        self.setLayout(layout)

    def get_picture_paths(self):
        """
        .. _getPicturePaths:
        Return array of paths to undercoat pictures

        return:
            String[] underlying pictures
        """
        items = self._list_widget.selectedItems()
        pictures = []

        for item in items:
            i = self._list_widget.row(item)
            pictures.append(self._list[0][i])
        return pictures

    def _init_list(self):
        """create list of  pictures with default item"""
        self._list_widget.addItems(_DEFAULT_LIST[1])
        self._list_widget.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection)
        self._list_widget.itemSelectionChanged.connect(self._selection_changed)

        for i in range(0, len(self._list)-1):
            item = self._list_widget.item(i)
            item.setToolTip(self._list[0][i])

    def _add_item(self):
        """Clicked event for_add_button"""
        path = self._file_name.text()
        if not path:
            return
        name = os.path.basename(path)
        if not name:
            return

        self._list[0].append(path)
        self._list[1].append(name)

        item = QtWidgets.QListWidgetItem(name)
        self._list_widget.addItem(item)
        item.setToolTip(path)

    def _delete_item(self):
        """Clicked event for_delete_button"""
        items = self._list_widget.selectedItems()
        for item in items:
            i = self._list_widget.row(item)
            #self._list_widget.deleteItemWidget(item)
            item = self._list_widget.takeItem(i)

            del self._list[0][i]
            del self._list[1][i]

    def _add_picture(self):
        """Clicked event for _file_button"""
        from os.path import expanduser
        home = expanduser("~")
        picture = QtWidgets.QFileDialog.getOpenFileName(
            self, _("Choose Picture"), home, _("Images (*.png *.xpm *.jpg)"))
        if picture[0]:
            self._file_name.setText(picture[0])

    def _selection_changed(self):
        """ItemSelectionChanged event for _list_widget"""
        self.pictureListChanged.emit()
