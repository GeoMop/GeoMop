import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore

class TranformationDetailDlg(QtWidgets.QDialog):

    def __init__(self, name, description, v1,  orig_v1, v2, is_v2 , parent=None):
        super(TranformationDetailDlg, self).__init__(parent)
        self.setWindowTitle("Json Editor")
        errors = []
        
        grid = QtWidgets.QGridLayout()
        
        name = QtWidgets.QLabel("Name:")
        name_v = QtWidgets.QLabel(name)
        name_v.setFrameStyle(QtWidgets.QFrame.Sunken)
        grid.addWidget(name, 0, 0)
        grid.addWidget(name_v, 0, 1)
        
        description = QtWidgets.QLabel("Description:")
        description_v = QtWidgets.QLabel(description)
        description_v.setFrameStyle(QtWidgets.QFrame.Sunken)
        grid.addWidget(description, 1, 0)
        grid.addWidget(description_v, 1, 1)
        
        old_version = QtWidgets.QLabel("Old Version:")
        old_version_v = QtWidgets.QLabel(v1)
        old_version_v.setFrameStyle(QtWidgets.QFrame.Sunken)
        if v1 != orig_v1:
            pal = QtCore.QPalette(old_version_v.palette())
            pal.setColor(QtCore.QPalette.WindowText, QtCore.QColor(QtCore.Qt.red))
            old_version_v.setPalette(pal)
            errors.append("Original text format '" + orig_v1 + 
                "' and format specified in transformation file '" +  
                v1 + "' are different")
        grid.addWidget(old_version, 2, 0)
        grid.addWidget(old_version_v, 2, 1)
        
        new_version = QtWidgets.QLabel("New Version:")
        new_version_v = QtWidgets.QLabel(v2)
        new_version_v.setFrameStyle(QtWidgets.QFrame.Sunken)
        if not is_v2:
            pal = QtCore.QPalette(new_version_v.palette())
            pal.setColor(QtCore.QPalette.WindowText, QtCore.QColor(QtCore.Qt.red))
            new_version_v.setPalette(pal)
            errors.append("Requested format specified in transformation file '" +  
                v2 + "' is not available")
        grid.addWidget(new_version, 3, 0)
        grid.addWidget(new_version_v, 3, 1)
        
        new_line = 4
        if len(errors)>0:
            err = QtWidgets.QLabel(errors.join("\n"))
            err.setFrameStyle(QtWidgets.QFrame.Sunken)
            grid.addWidget(err, new_line, 0, new_line, 1)
            new_line += 1
            
        self._tranform_button = QtWidgets.QPushButton("Transform file")
        self._cancel_button = QtWidgets.QPushButton("Cancel")
        grid.addWidget(self._tranform_button, new_line, 0)
        grid.addWidget(self._cancel_button, new_line, 1)
