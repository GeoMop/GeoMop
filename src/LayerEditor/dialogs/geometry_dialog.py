import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import data.task

class GeometryDlg(QtWidgets.QDialog):

    def __init__(self, geometry=None, parent=None):
        super(GeometryDlg, self).__init__(parent)
        
        if geometry == None:
            geometry = new data.

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



self.setLayout(grid)

        self.connect(buttonBox, SIGNAL("accepted()"),
                     self, SLOT("accept()"))
        self.connect(buttonBox, SIGNAL("rejected()"),
                     self, SLOT("reject()"))
        self.setWindowTitle("Set Number Format (Modal)")
        
        
