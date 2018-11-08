from LayerEditor.ui.dialogs.init_dialog_ui import Ui_InitDialog
from PyQt5 import QtWidgets, QtGui, QtCore



class InitDialog(QtWidgets.QDialog):
    open_existing_signal = QtCore.pyqtSignal()
    open_recent_signal = QtCore.pyqtSignal()
    init_from_shapefile_signal = QtCore.pyqtSignal()
    # Emitted with x,y, x_size, y_size, top left corner and size of rectangle.
    init_new_signal = QtCore.pyqtSignal(float, float, float, float)


    def set_int_lineedit(self, ledit, coord_idx):
        def set_coord():
            self.coords[coord_idx] = int(ledit)
        ledit.editingFinished.connect(set_coord)
        validator = QtGui.QIntValidator()
        ledit.setValidator(validator)


    def __init__(self, recent_group, parent=None):
        super().__init__(parent)
        self.ui = Ui_InitDialog()
        self.ui.setupUi(self)

        self.ui.open_existing_button.clicked.connect(self.open_existing_signal)

        self.recent_menu = QtGui.QMenu(self.ui.open_recent_button)
        # ?? How to set group action to menu
        #group = QtGui.QActionGroup(self.toolMenu) # ???

        self.ui.open_recent_button.setMenu(self.recent_menu)
        self.ui.open_recent_button.setPopupMode(QtGui.QToolButton.InstantPopup)
        #group.triggered.connect(self.test)







        self.ui.from_shape_button.clicked.connect(self.init_from_shapefile_signal)
        self.ui.from_coords_button.clicked.connect(lambda :
            InitDialog.init_new_signal.emit(self.coords[0], self.coords[1], self.coords[2], self.coords[3]))
        self.set_int_lineedit(self.ui.min_x_lineedit, 0)
        self.set_int_lineedit(self.ui.min_y_lineedit, 1)
        self.set_int_lineedit(self.ui.size_x_lineedit, 2)
        self.set_int_lineedit(self.ui.size_y_lineedit, 3)

    #
    #     self.
    #     self.setWindowTitle("Set Slice Inicialization Method")
    #
    #     self.closed = False
    #     """Dialog was closed"""
    #
    #     grid = QtWidgets.QGridLayout(self)
    #
    #     self.shp = QtWidgets.QRadioButton("")
    #     self.shp.clicked.connect(self.enable_controls)
    #     d_shp_file = QtWidgets.QLabel("Shape File:")
    #     self.shp_file_name = QtWidgets.QLineEdit()
    #     self.shp_file_button = QtWidgets.QPushButton("...")
    #     self.shp_file_button.clicked.connect(self._add_shp_file)
    #
    #     grid.addWidget(self.shp, 0, 0)
    #     grid.addWidget(d_shp_file, 0, 1)
    #     grid.addWidget(self.shp_file_name, 0, 2, 1, 2)
    #     grid.addWidget(self.shp_file_button, 0, 4)
    #
    #     self.coordinates = QtWidgets.QRadioButton("")
    #     self.coordinates.clicked.connect(self.enable_controls)
    #     self.coordinates.setChecked(True)
    #     d_coordinates = QtWidgets.QLabel("Coordinates:", self)
    #
    #     d_x = QtWidgets.QLabel("x:", self)
    #     d_x.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
    #     self.x = QtWidgets.QLineEdit()
    #     self.x.setText("0.0")
    #     self.x.setValidator(QtGui.QDoubleValidator())
    #
    #     d_y = QtWidgets.QLabel("y:", self)
    #     d_y.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
    #     self.y = QtWidgets.QLineEdit()
    #     self.y.setText("0.0")
    #     self.y.setValidator(QtGui.QDoubleValidator())
    #
    #     d_dx = QtWidgets.QLabel("dx:", self)
    #     d_dx.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
    #     self.dx = QtWidgets.QLineEdit()
    #     self.dx.setText("100.0")
    #     self.dx.setValidator(QtGui.QDoubleValidator())
    #
    #     d_dy = QtWidgets.QLabel("dy:", self)
    #     d_dy.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
    #     self.dy = QtWidgets.QLineEdit()
    #     self.dy.setText("100.0")
    #     self.dy.setValidator(QtGui.QDoubleValidator())
    #
    #     grid.addWidget(self.coordinates, 1, 0, 1, 2)
    #     grid.addWidget(d_coordinates, 1, 1, 1, 2)
    #
    #     grid.addWidget(d_x, 2, 1)
    #     grid.addWidget(self.x, 2, 2)
    #     grid.addWidget(d_dx, 2, 3)
    #     grid.addWidget(self.dx, 2, 4)
    #
    #     grid.addWidget(d_y, 3, 1)
    #     grid.addWidget(self.y, 3, 2)
    #     grid.addWidget(d_dy, 3, 3)
    #     grid.addWidget(self.dy, 3, 4)
    #
    #     self._inicializa_button = QtWidgets.QPushButton("Inicialize New", self)
    #     self._inicializa_button.clicked.connect(self.accept)
    #     self._cancel_button = QtWidgets.QPushButton("Open Existing ...", self)
    #     self._cancel_button.clicked.connect(self.reject)
    #
    #     button_box = QtWidgets.QDialogButtonBox()
    #     button_box.addButton(self._inicializa_button, QtWidgets.QDialogButtonBox.AcceptRole)
    #     button_box.addButton(self._cancel_button, QtWidgets.QDialogButtonBox.RejectRole)
    #
    #     grid.addWidget(button_box, 4, 3, 1, 2)
    #     self.setLayout(grid)
    #     self.enable_controls()
    #
    # def _add_shp_file(self):
    #     """Clicked event for _file_button"""
    #     home = cfg.config.data_dir
    #     file = QtWidgets.QFileDialog.getOpenFileName(
    #         self, "Choose shape file", home, "File (*.shp)")
    #     if file[0]:
    #         self.shp_file_name.setText(file[0])
    #
    # def enable_controls(self):
    #     """Disable all not used controls"""
    #     self.x.setEnabled(self.coordinates.isChecked())
    #     self.y.setEnabled(self.coordinates.isChecked())
    #     self.dx.setEnabled(self.coordinates.isChecked())
    #     self.dy.setEnabled(self.coordinates.isChecked())
    #
    #     self.shp_file_name.setEnabled(self.shp.isChecked())
    #     self.shp_file_button.setEnabled(self.shp.isChecked())
    #
    # def closeEvent(self, event):
    #     """Standart close event"""
    #     self.closed = True
    #     super(SetDiagramDlg, self).closeEvent(event)
    #
    # def accept(self):
    #     """
    #     Accepts the form if file data fields are valid
    #     and inicialize dialog
    #     :return: None
    #     """
    #     ret = True
    #
    #     if self.coordinates.isChecked():
    #         try:
    #             x1 = float(self.x.text())
    #             x2 = x1 + float(self.dx.text())
    #             y1 = float(self.y.text())
    #             y2 = y1 + float(self.dy.text())
    #         except:
    #             err_dialog = GMErrorDialog(self)
    #             err_dialog.open_error_dialog("Bad coordinates format")
    #             ret = False
    #         cfg.diagram.area.set_area([x1, x1, x2, x2], [y1, y2, y2, y1])
    #     else:
    #         if cfg.open_shape_file(self.shp_file_name.text()):
    #             if cfg.main_window is not None:
    #                 cfg.main_window.refresh_diagram_shp()
    #             rect = cfg.diagram.shp.boundrect
    #             cfg.diagram.area.set_area([rect.left(), rect.left(), rect.right(), rect.right()],
    #                                       [-rect.top(), -rect.bottom(), -rect.bottom(), -rect.top()])
    #         else:
    #             err_dialog = GMErrorDialog(self)
    #             err_dialog.open_error_dialog("Bad shape file format")
    #             ret = False
    #     if ret:
    #         super(SetDiagramDlg, self).accept()
