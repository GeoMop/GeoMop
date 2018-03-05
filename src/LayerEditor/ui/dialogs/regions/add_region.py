"""
Dialog for adding region to interface.
"""
from gm_base.geometry_files.format_last import RegionDim
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
from LayerEditor.leconfig import cfg
from gm_base.geomop_dialogs import GMErrorDialog

class AddRegionDlg(QtWidgets.QDialog):
    
    BACKGROUND_COLORS = [    
        QtGui.QColor("#ff0000"), # red
        QtGui.QColor("#ffff00"), # yellow
        QtGui.QColor("#00ff00"), # lime
        QtGui.QColor("#00ffff"), # aqua
        QtGui.QColor("#0000ff"), # blue
        QtGui.QColor("#ff00ff"), # fuchsia
        QtGui.QColor("#800000"), # maroon
        QtGui.QColor("#808000"), # olive
        QtGui.QColor("#008000"), # green
        QtGui.QColor("#008080"), # teal
        QtGui.QColor("#000080"), # navy
        QtGui.QColor("#800080"), # purple

        # QtGui.QColor("#e2caff"),  # blue1
        # QtGui.QColor("#bbffc0"),  # green1
        # QtGui.QColor("#fffaae"),  # yelow1
        # QtGui.QColor("#ffd3d0"),  # red1
        # QtGui.QColor("#c8c8c8"),  # gray
        # QtGui.QColor("#c1cfff"),  # blue2
        # QtGui.QColor("#ffcde6"),  # pink1
        # QtGui.QColor("#c1ffda"),  # green2
        # QtGui.QColor("#ffd0b8"),  # red2
        # QtGui.QColor("#ffff7f"),  # yelow2
        # QtGui.QColor("#ffd2f6"),  # pink2
        # QtGui.QColor("#cfebff"),  # blue3
        # QtGui.QColor("#e3ffb5"),  # green3
        # QtGui.QColor("#ffd7dd"),  # red3
        # QtGui.QColor("#f3ffb3"),  # yelow3
        # QtGui.QColor("#8effff")  # blue4
    ]
        
    REGION_DESCRIPTION = {
        RegionDim.none: "None (default)",
        RegionDim.point: "Point (0D)",
        RegionDim.well: "Well (1D)",
        RegionDim.fracture: "Fracture (2D)", 
        RegionDim.bulk: "Bulk (3D)"
    }
    
    REGION_DESCRIPTION_SHORT = {
        RegionDim.none: "default",
        RegionDim.point: "point",
        RegionDim.well: "well",
        RegionDim.fracture: "fracture", 
        RegionDim.bulk: "bulk"
    }


    def __init__(self,  parent=None):
        super(AddRegionDlg, self).__init__(parent)
        self.setWindowTitle("Add Region")

        grid = QtWidgets.QGridLayout(self)

        d_region_dim = QtWidgets.QLabel("Region Dimension:", self)
        self.region_dim = QtWidgets.QComboBox()
        self.region_dim.addItem(self.REGION_DESCRIPTION[RegionDim.point], RegionDim.point)
        self.region_dim.addItem(self.REGION_DESCRIPTION[RegionDim.well], RegionDim.well)
        self.region_dim.addItem(self.REGION_DESCRIPTION[RegionDim.fracture], RegionDim.fracture)
        self.region_dim.addItem(self.REGION_DESCRIPTION[RegionDim.bulk], RegionDim.bulk)
        # TODO: change the default value according to the maximal dimension of selected elements in the viewport area
        self.region_dim.setCurrentIndex(3)

        d_region_name = QtWidgets.QLabel("Region Name:", self)
        self.region_name = QtWidgets.QLineEdit()
        self.image = QtWidgets.QLabel(self)

        self.image.setMinimumWidth(self.region_name.sizeHint().height())
        self.image.setPixmap(QtGui.QIcon.fromTheme("emblem-default").pixmap(self.region_name.sizeHint().height()))
        self.image.setToolTip('Region name is unique, everything is fine.')
        self.have_default_name = True
        self.set_default_name(3)
        self.region_name.textChanged.connect(self.reg_name_changed)




        grid.addWidget(d_region_name, 0, 0)
        grid.addWidget(self.region_name, 0, 1)
        grid.addWidget(self.image, 0, 2)


        self.region_dim.currentIndexChanged[int].connect(self.set_default_name)
        grid.addWidget(d_region_dim, 1, 0)
        grid.addWidget(self.region_dim, 1, 1, 1, 2)

        self._tranform_button = QtWidgets.QPushButton("Add", self)
        self._tranform_button.clicked.connect(self.accept)
        self._cancel_button = QtWidgets.QPushButton("Cancel", self)
        self._cancel_button.clicked.connect(self.reject)

        button_box = QtWidgets.QDialogButtonBox()
        button_box.addButton(self._tranform_button, QtWidgets.QDialogButtonBox.AcceptRole)
        button_box.addButton(self._cancel_button, QtWidgets.QDialogButtonBox.RejectRole)

        grid.addWidget(button_box, 2, 1)
        self.setLayout(grid)

    @classmethod
    def is_unique_region_name(self, reg_name):
        """ Return False in the case of colision with an existing region name."""
        for region in cfg.diagram.regions.regions:
            if reg_name == region.name:
                return False
        return True

    def reg_name_changed(self, reg_name):
        """ Called when Region Line Edit is changed."""
        self.have_default_name = False
        if self.is_unique_region_name(reg_name):
            self.image.setPixmap(
                QtGui.QIcon.fromTheme("emblem-default").pixmap(self.region_name.sizeHint().height())
            )
            self.image.setToolTip('Unique name is OK.')
            self._tranform_button.setEnabled(True)
        else:
            self.image.setPixmap(
                QtGui.QIcon.fromTheme("emblem-important").pixmap(self.region_name.sizeHint().height())
            )
            self.image.setToolTip('Name is not unique!')
            self._tranform_button.setEnabled(False)


    @classmethod
    def get_some_color(cls, i):
        """Return firs collor accoding to index"""
        return cls.BACKGROUND_COLORS[i % len(cls.BACKGROUND_COLORS)]


    def set_default_name(self, dim):
        """ Set default name if it seems to be default name. """
        if self.have_default_name:
            dim_to_regtype = ["point_", "well_", "fracture_", "bulk_"]
            reg_id = 0
            name = cfg.diagram.regions.regions[0].name
            while not self.is_unique_region_name(name):
                reg_id += 1
                name = dim_to_regtype[dim] + str(reg_id)
            self.region_name.setText(name)
            self.have_default_name = True

    def accept(self):
        """
        Accepts the form if region data is valid.
        :return: None
        """
        error = None
        for region in cfg.diagram.regions.regions:
            if self.region_name.text() == region.name:
                error = "Region name already exist"
                break
        if len(self.region_name.text())==0 or self.region_name.text().isspace():
            error = "Region name is empty"
        if error is not None:
            err_dialog = GMErrorDialog(self)
            err_dialog.open_error_dialog(error)
        else:
            super(AddRegionDlg, self).accept()
