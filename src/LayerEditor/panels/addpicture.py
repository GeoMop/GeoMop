# pylint: disable=E1002
"""AddPictureWidget file"""
import os
import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui

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
        
        self._data = _AddPictureData()

        self.setSizePolicy(QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        self.setMinimumSize(QtCore.QSize(200, 500))

        self._list_widget = QtWidgets.QListWidget()
        self._init_list()

        self._add_button = QtWidgets.QPushButton("Add")
        self._add_button.clicked.connect(self._add_item)
        self._delete_button = QtWidgets.QPushButton("Delete")
        self._delete_button.clicked.connect(self._delete_item)

        label_file = QtWidgets.QLabel("Picture File:")
        self._file_name = QtWidgets.QLineEdit()
        self._file_button = QtWidgets.QPushButton("...")
        self._file_button.clicked.connect(self._add_picture)

        label_x = QtWidgets.QLabel("x:")
        self._x = QtWidgets.QLineEdit()
        if self._data.rect.left()<0:
            self._x.setText("min")
        else:
            self._x.setText(self._data.rect.left())
        
        label_y = QtWidgets.QLabel("y:")
        self._y = QtWidgets.QLineEdit()
        if self._data.rect.bottom()<0:
            self._y.setText("min")
        else:
            self._y.setText(self._data.rect.bottom())
        
        label_dx = QtWidgets.QLabel("dx:")
        self._dx = QtWidgets.QLineEdit()
        if self._data.rect.width()<0:
            self._dx.setText("max")
        else:
            self._dx.setText(self._data.rect.width())
            
        label_dy = QtWidgets.QLabel("dy:")
        self._dy = QtWidgets.QLineEdit()
        if self._data.rect.height()<0:
            self._dy.setText("max")
        else:
            self._dy.setText(self._data.rect.height())
            
        label_opaque = QtWidgets.QLabel("Opaque:")
        self._opaque = QtWidgets.QSpinBox()
        self._opaque.setAlignment(QtCore.Qt.AlignRight)
        self._opaque.setRange(0, 100)
        self._opaque.setValue(self._data.opaque)
        
        self._above_layer = QtWidgets.QCheckBox("Disply Above Layer")
        self._above_layer.setChecked(self._data.layer_above)
        self._al_color = QtWidgets.QFrame(self)
        self._al_color.setStyleSheet("QWidget { background-color: %s }" 
            % self._data.layer_above_color.name())
        self._al_color_button = QtWidgets.QPushButton("Color ...")

        self._below_layer = QtWidgets.QCheckBox("Disply Below Layer")
        self._below_layer.setChecked(self._data.layer_below)
        self._bl_color = QtWidgets.QFrame(self)
        self._bl_color.setStyleSheet("QWidget { background-color: %s }" 
            % self._data.layer_below_color.name())
        self._bl_color_button = QtWidgets.QPushButton("Color ...")
        
        grid = QtWidgets.QGridLayout()
        grid.addWidget(self._add_button, 0, 0, 1, 2)
        grid.addWidget(self._delete_button, 0, 2, 1, 2)
        grid.addWidget(label_file, 1, 0, 1, 3)
        grid.addWidget(self._file_button, 1, 3)
        grid.addWidget(self._file_name, 2, 0, 1, 4)
        grid.addWidget(label_x, 3, 0)
        grid.addWidget(self._x, 3, 1)
        grid.addWidget(label_dx, 3, 2)
        grid.addWidget(self._dx, 3, 3)
        grid.addWidget(label_y, 4, 0)
        grid.addWidget(self._y, 4, 1)
        grid.addWidget(label_dy, 4, 2)
        grid.addWidget(self._dy, 4, 3)
        grid.addWidget(label_opaque, 5, 0, 1, 2)
        grid.addWidget(self._opaque, 5, 2)
        grid.addWidget(self._above_layer, 6, 0,  1,  2)
        grid.addWidget(self._al_color, 6, 2)
        grid.addWidget(self._al_color_button, 6, 3)
        grid.addWidget(self._below_layer, 7, 0,  1,  2)
        grid.addWidget(self._bl_color, 7, 2)
        grid.addWidget(self._bl_color_button, 7, 3)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self._list_widget)
        layout.addLayout(grid)
        self.setLayout(layout)

    def get_pixmap(self):
        """
        .. _getPicturePaths:
        Return underlying composite picture

        return:
            QPixmap underlying picture
        """
        items = self._list_widget.selectedItems()
        self._data.selected=-1
        
        for item in items:
            i = self._list_widget.row(item)
            self._data.selected=i
            picture = self._data.pic_paths[i]
            break
                      
        return [picture]

    def _init_list(self):
        """create list of  pictures with default item"""
        self._list_widget.addItems(self._data.pic_names)
        self._list_widget.itemSelectionChanged.connect(self._selection_changed)

        # set path as tooltip
        for i in range(0, len(self._data.pic_paths)-1):
            item = self._list_widget.item(i)
            item.setToolTip(self._data.pic_paths[i])
            
        # select item
        if  self._data.selected>=0  and self._data.selected <  len(self._data.pic_paths)   :
            self._list_widget.setCurrentRow(self._data.selected)

    def _add_item(self):
        """Clicked event for_add_button"""
        path = self._file_name.text()
        if not path:
            return
        name = os.path.basename(path)
        if not name:
            return

        self._data.pic_paths.append(path)
        self._data.pic_names.append(name)

        item = QtWidgets.QListWidgetItem(name)
        self._list_widget.addItem(item)
        item.setToolTip(path)
        self._data.save()

    def _delete_item(self):
        """Clicked event for_delete_button"""
        items = self._list_widget.selectedItems()
        for item in items:
            i = self._list_widget.row(item)
            #self._list_widget.deleteItemWidget(item)
            item = self._list_widget.takeItem(i)

            del self._data.pic_paths[i]
            del self._data.pic_names[i]
            self._data.save()

    def _add_picture(self):
        """Clicked event for _file_button"""
        from os.path import expanduser
        home = expanduser("~")
        picture = QtWidgets.QFileDialog.getOpenFileName(
            self, "Choose Picture", home,"Images (*.png *.xpm *.jpg)")
        if picture[0]:
            self._file_name.setText(picture[0])

    def _selection_changed(self):
        """ItemSelectionChanged event for _list_widget"""
        items = self._list_widget.selectedItems()
        self._data.selected=-1
        
        for item in items:
            i = self._list_widget.row(item)
            self._data.selected=i
            break
            
        self._data.save()
        self.pictureListChanged.emit()

import config

class _AddPictureData():
    """
    Helper for preservation AddPictureWidget data
    """
    
    def __init__(self):
        """
        Try load AddPictureWidget data from config file, 
        or set default AddPictureWidget data if config file not exist
        """
        data=config.get_config_file("AddPictureData")
        if(data != None):
            self = data
            return
        self.pic_paths = []
        self.pic_names = []
        self.selected = -1
        self.rect = QtCore.QRect(-1, -1, -1, -1)
        self.opaque = 50
        self.layer_below = False
        self.layer_above = False
        self.layer_below_color = QtGui.QColor(255, 120, 200)
        self.layer_above_color = QtGui.QColor(120, 120, 255)
        
    def save(self):
        """Save AddPictureWidget data"""
        config.save_config_file("AddPictureData", self)
