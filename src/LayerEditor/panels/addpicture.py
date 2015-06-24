# pylint: disable=E1002
"""AddPictureWidget file"""
import os
import copy
import drawing.draw_lib as pxl
import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui

BIG_NUMBER = 100000000.1

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

        label_picture = QtWidgets.QLabel("Select Underlying Picture:")

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
        if self._data.rect.left()<(1-BIG_NUMBER):
            self._x.setText("min")
        else:
            self._x.setText(str(self._data.rect.left()))
        self._x.editingFinished.connect(self._rect_changed)
        
        label_y = QtWidgets.QLabel("y:")
        self._y = QtWidgets.QLineEdit()
        if self._data.rect.top()<(1-BIG_NUMBER):
            self._y.setText("min")
        else:
            self._y.setText(str(self._data.rect.top()))
        self._y.editingFinished.connect(self._rect_changed)
        
        label_dx = QtWidgets.QLabel("dx:")
        self._dx = QtWidgets.QLineEdit()
        if self._data.rect.width()<(1-BIG_NUMBER):
            self._dx.setText("max")
        else:
            self._dx.setText(str(self._data.rect.width()))
        self._dx.editingFinished.connect(self._rect_changed)
            
        label_dy = QtWidgets.QLabel("dy:")
        self._dy = QtWidgets.QLineEdit()
        if self._data.rect.height()<(1-BIG_NUMBER):
            self._dy.setText("max")
        else:
            self._dy.setText(str(self._data.rect.height()))
        self._dy.editingFinished.connect(self._rect_changed)
            
        label_opaque = QtWidgets.QLabel("Opaque:")
        self._opaque = QtWidgets.QSpinBox()
        self._opaque.setAlignment(QtCore.Qt.AlignRight)
        self._opaque.setRange(0, 100)
        self._opaque.setValue(self._data.opaque)
        self._opaque.valueChanged.connect(self._opaque_changed)
        
        self._above_layer = QtWidgets.QCheckBox("Disply Above Layer")
        self._above_layer.setChecked(self._data.layer_above)
        self._above_layer.stateChanged.connect(lambda: self._change_disply_layer(True))
        self._al_color = QtWidgets.QFrame(self)
        self._al_color.setStyleSheet("QWidget { background-color: %s }" 
            % self._data.layer_above_color.name())
        self._al_color_button = QtWidgets.QPushButton("Color ...")
        self._al_color_button.clicked.connect(lambda: self._change_color(True))

        self._below_layer = QtWidgets.QCheckBox("Disply Below Layer")
        self._below_layer.setChecked(self._data.layer_below)
        self._below_layer.stateChanged.connect(lambda: self._change_disply_layer(False))
        self._bl_color = QtWidgets.QFrame(self)
        self._bl_color.setStyleSheet("QWidget { background-color: %s }" 
            % self._data.layer_below_color.name())
        self._bl_color_button = QtWidgets.QPushButton("Color ...")
        self._bl_color_button.clicked.connect(lambda: self._change_color(False))
        
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
        layout.addWidget(label_picture)
        layout.addWidget(self._list_widget)
        layout.addLayout(grid)
        self.setLayout(layout)

    def get_pixmap(self, x, y,  scale):
        """
        .. _getPicturePaths:
        Return underlying composite picture

        return:
            QPixmap underlying picture
        """
        
        picture = pxl.getWhitePixmap(x, y)
        
        if self._data.selected>0:
            rect = QtCore.QRect(0, 0, x,  y)
            if self._data.rect.left() > (1-BIG_NUMBER):
                rect.setX(int(self._data.rect.left()*scale))
            if self._data.rect.top() > (1-BIG_NUMBER):
                rect.setY(int(self._data.rect.top()*scale))    
            if self._data.rect.width() > (1-BIG_NUMBER):
                rect.setRight(int(self._data.rect.right()*scale))
            if self._data.rect.height() > (1-BIG_NUMBER):
                rect.setBottom(int(self._data.rect.bottom()*scale))

            pxl.drawPictureTiPixmap(self._data.lastPicture, rect, picture,  self._data.opaque)
#        picture = self._data.lastPicture
        if picture == "None":
            return []        
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
            if i==0:
                # none pocture can't be remove
                continue
                
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
        if self._data.is_state_changed():
            self.pictureListChanged.emit()
    
    def _rect_changed(self):
        """editingFinished event for _x ,_y, _dx or _dy widget"""
        self._data.rect = QtCore.QRectF(
            self._check_and_get_coordinate(self._x), 
            self._check_and_get_coordinate(self._y), 
            self._check_and_get_coordinate(self._dx), 
            self._check_and_get_coordinate(self._dy))
        self._data.save()
        if self._data.is_state_changed():
            self.pictureListChanged.emit()
        
    def _check_and_get_coordinate(self, edit):
        """get coordinate from QLineEdit or -1"""
        coord = edit.text()
        try:
            coord = float(coord)
        except ValueError:
            coord = -BIG_NUMBER
        return coord
        
    def _opaque_changed(self):
        """valueChanged event for _opaque widget"""
        self._data.opaque = self._opaque.value()
        self._data.save()
        if self._data.is_state_changed():
            self.pictureListChanged.emit()
    
    def _change_color(self,  above):
        """Clicked event for _al_color_button (above = True) or _bl_color_button button"""
        col = QtWidgets.QColorDialog.getColor()
        if above:
            self._data.layer_above_color = col
            self._al_color.setStyleSheet("QWidget { background-color: %s }" 
                % self._data.layer_above_color.name())
        else:
            self._data.layer_below_color = col
            self._bl_color.setStyleSheet("QWidget { background-color: %s }" 
                % self._data.layer_below_color.name())
        self._data.save()
        if self._data.is_state_changed():
            self.pictureListChanged.emit()
            
    def _change_disply_layer(self,  above):
        """stateChanged event for _al_color (above = True) or _bl_color checkbox"""
        if above:
            self._data.layer_above = self._above_layer.isChecked()
        else:
            self._data.layer_below = self._below_layer.isChecked()
        self._data.save()    
        if self._data.is_state_changed():
            self.pictureListChanged.emit()

import config

class _AddPictureData():
    """
    Helper for preservation AddPictureWidget data
    """
    SERIAL_FILE = "AddPictureData"    
    """Serialize class file"""
    
    def __init__(self, readfromconfig = True):
        """
        Try load AddPictureWidget data from config file, 
        or set default AddPictureWidget data if config file not exist
        """
        if readfromconfig:
            data=config.get_config_file(self.__class__.SERIAL_FILE)
        else:
            data=None
            
        if(data != None):
            self.pic_paths = copy.deepcopy(data.pic_paths)
            self.pic_names = copy.deepcopy(data.pic_names)
            self.selected = data.selected
            self.rect = QtCore.QRectF(data.rect)
            self.opaque = data.opaque
            self.layer_below = data.layer_below
            self.layer_above =  data.layer_above
            self.layer_below_color = QtGui.QColor(data.layer_below_color)
            self.layer_above_color = QtGui.QColor(data.layer_above_color)
        else:
            self.pic_paths = ["Without underlying picture"]
            self.pic_names = ["None"]
            self.selected = 0
            self.rect = QtCore.QRectF(-BIG_NUMBER, -BIG_NUMBER, -BIG_NUMBER, -BIG_NUMBER)
            self.opaque = 50
            self.layer_below = False
            self.layer_above = False
            self.layer_below_color = QtGui.QColor(255, 120, 200)
            self.layer_above_color = QtGui.QColor(120, 120, 255)
        self.lastPicture = None
        if  self.selected > 0 and self.selected <  len(self.pic_paths):
            self.lastPicture = self.pic_paths[self.selected]
        self._lastState = None
        
    def save(self):
        """Save AddPictureWidget data"""
        config.save_config_file(self.__class__.SERIAL_FILE, self)
        
    def is_state_changed(self):
        """
        Check last state and copy current state for next calling this function
        
        return if state was changed
        """
        changed = False
        if self._lastState == None:
            # for lastState values self.pic_paths, self.pic_names, _lastPicture and _lastState not use
            self._lastState = _AddPictureData(False)
        
        if  self.selected > 0 and self.selected <  len(self.pic_paths):
            newPicture = self.pic_paths[self.selected]
        else:
            newPicture = None
        if newPicture != self.lastPicture:
            changed = True
            self.lastPicture = newPicture
        if self.rect != self._lastState.rect:
            changed = True
            self._lastState.rect=QtCore.QRectF(self.rect)
        if self.opaque != self._lastState.opaque:
            changed = True
            self._lastState.opaque=self.opaque
        if self.layer_below != self._lastState.layer_below:
            changed = True
            self._lastState.layer_below = self.layer_below
            self._lastState.layer_below_color = QtGui.QColor(self.layer_below_color)
        elif self.layer_below and self._lastState.layer_below_color != self.layer_below_color:    
            changed = True
            self._lastState.layer_below_color = QtGui.QColor(self.layer_below_color)
        if self.layer_above != self._lastState.layer_above:
            changed = True
            self._lastState.layer_above = self.layer_above
            self._lastState.layer_above_color = QtGui.QColor(self.layer_above_color)
        elif self.layer_above and self._lastState.layer_above_color != self.layer_above_color:    
            changed = True
            self._lastState.layer_above_color = QtGui.QColor(self.layer_above_color)            
        return changed
