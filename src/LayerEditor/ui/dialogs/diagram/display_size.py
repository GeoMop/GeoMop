"""
Dialog for settings diagram size.
"""
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore

class DisplaySizeDlg(QtWidgets.QDialog):
    def __init__(self, rect):
        super(DisplaySizeDlg, self).__init__()
        self.setWindowTitle("Display Size Settings")

        grid = QtWidgets.QGridLayout(self)
        
        d_x = QtWidgets.QLabel("Origin X:", self)
        d_y = QtWidgets.QLabel("Origin Y:", self)
        d_dx = QtWidgets.QLabel("Size X:", self)
        d_dy = QtWidgets.QLabel("Size Y:", self)
        self.x = QtWidgets.QLineEdit()
        self.x.setValidator(QtGui.QDoubleValidator())
        self.x.setText(str(rect.left()))
        self.y = QtWidgets.QLineEdit()
        self.y.setValidator(QtGui.QDoubleValidator())
        self.y.setText(str(-rect.bottom()))
        self.dx = QtWidgets.QLineEdit()
        self.dx.setValidator(QtGui.QDoubleValidator())
        self.dx.setText(str(rect.width()))
        self.dy = QtWidgets.QLineEdit()
        self.dy.setValidator(QtGui.QDoubleValidator())
        self.dy.setText(str(rect.height()))
        
        grid.addWidget(d_x, 0, 0)
        grid.addWidget(self.x, 0, 1)
        grid.addWidget(d_y, 1, 0)
        grid.addWidget(self.y, 1, 1)
        grid.addWidget(d_dx, 2, 0)
        grid.addWidget(self.dx, 2, 1)
        grid.addWidget(d_dy, 3, 0)
        grid.addWidget(self.dy, 3, 1)

        self._set_button = QtWidgets.QPushButton("Set Display", self)
        self._set_button.clicked.connect(self.accept)
        self._cancel_button = QtWidgets.QPushButton("Cancel", self)
        self._cancel_button.clicked.connect(self.reject)

        button_box = QtWidgets.QDialogButtonBox()
        button_box.addButton(self._set_button, QtWidgets.QDialogButtonBox.AcceptRole)
        button_box.addButton(self._cancel_button, QtWidgets.QDialogButtonBox.RejectRole)

        grid.addWidget(button_box, 4, 1)
        self.setLayout(grid)
        
    def get_rect(self):
        """Return set display"""
        y = float(self.y.text())
        dy = float(self.dy.text())
        return QtCore.QRectF(float(self.x.text()),-(y+dy), 
            float(self.dx.text()),dy)
