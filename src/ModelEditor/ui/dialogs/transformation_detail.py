"""
Transformation dialog.
"""

import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui


class TranformationDetailDlg(QtWidgets.QDialog):

    def __init__(self, name, description, v1, orig_v1, v2, is_v2, parent=None):
        super(TranformationDetailDlg, self).__init__(parent)
        self.setWindowTitle("Transformation Summary")
        errors = []

        grid = QtWidgets.QGridLayout(self)

        l_name = QtWidgets.QLabel("Name:", self)
        l_name_v = QtWidgets.QLabel(name, self)
        l_name_v.setFrameStyle(QtWidgets.QFrame.Sunken)
        grid.addWidget(l_name, 0, 0)
        grid.addWidget(l_name_v, 0, 1)

        l_description = QtWidgets.QLabel("Description:", self)
        l_description_v = QtWidgets.QLabel(description, self)
        l_description_v.setFrameStyle(QtWidgets.QFrame.Sunken)
        grid.addWidget(l_description, 1, 0)
        grid.addWidget(l_description_v, 1, 1)

        l_old_version = QtWidgets.QLabel("Old Version:", self)
        l_old_version_v = QtWidgets.QLabel(v1, self)
        l_old_version_v.setFrameStyle(QtWidgets.QFrame.Sunken)
        if v1 != orig_v1:
            pal = QtGui.QPalette(l_old_version_v.palette())
            pal.setColor(QtGui.QPalette.WindowText, QtGui.QColor(QtCore.Qt.red))
            l_old_version_v.setPalette(pal)
            errors.append(" * Original text format '" + orig_v1 +
                          "' and format specified in transformation file '" +
                          v1 + "' are different")
        grid.addWidget(l_old_version, 2, 0)
        grid.addWidget(l_old_version_v, 2, 1)

        l_new_version = QtWidgets.QLabel("New Version:", self)
        l_new_version_v = QtWidgets.QLabel(v2, self)
        l_new_version_v.setFrameStyle(QtWidgets.QFrame.Sunken)
        if not is_v2:
            pal = QtGui.QPalette(l_new_version_v.palette())
            pal.setColor(QtGui.QPalette.WindowText, QtGui.QColor(QtCore.Qt.red))
            l_new_version_v.setPalette(pal)
            errors.append(" * Requested format specified in transformation file '" +
                          v2 + "' is not available")
        grid.addWidget(l_new_version, 3, 0)
        grid.addWidget(l_new_version_v, 3, 1)

        new_line = 4
        if len(errors) > 0:
            err = QtWidgets.QLabel("\n".join(errors), self)
            err.setFrameStyle(QtWidgets.QFrame.Sunken)
            pal = QtGui.QPalette(err.palette())
            pal.setColor(QtGui.QPalette.WindowText, QtGui.QColor(QtCore.Qt.red))
            err.setPalette(pal)
            grid.addWidget(err, new_line, 0, 1, 2)
            new_line += 1

        self._tranform_button = QtWidgets.QPushButton("Transform file", self)
        self._tranform_button.clicked.connect(self.accept)
        self._cancel_button = QtWidgets.QPushButton("Cancel", self)
        self._cancel_button.clicked.connect(self.reject)

        button_box = QtWidgets.QDialogButtonBox()
        button_box.addButton(self._tranform_button, QtWidgets.QDialogButtonBox.AcceptRole)
        button_box.addButton(self._cancel_button, QtWidgets.QDialogButtonBox.RejectRole)

        grid.addWidget(button_box, new_line, 1)
        self.setLayout(grid)
