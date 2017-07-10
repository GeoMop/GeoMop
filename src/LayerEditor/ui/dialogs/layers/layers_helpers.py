"""
Dialogs for settings text name property or depth
"""

from geomop_dialogs import GMErrorDialog
import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
from ui.data import LayerSplitType

class LayersHelpers():

    @staticmethod
    def validate_depth(edit, validator, dialog):
        """
        Try validate depth parameter. If problem occured,
        display error and return False
        """
        pos = 0
        text = edit.text()
        state =validator.validate(text, pos)[0]
        if state==QtGui.QValidator.Acceptable:                        
            return True
        elif state == QtGui.QValidator.Intermediate:
            error = "Depth value out of range"
        else:
            error = "Bad depth value format" 
        err_dialog = GMErrorDialog(dialog)
        err_dialog.open_error_dialog(error)
        
    @staticmethod
    def split_type_combo():
        """Get combo box with layer splitting types """
        combo = QtWidgets.QComboBox()
        combo.addItem("interpolated", LayerSplitType.interpolated)
        combo.addItem("editable", LayerSplitType.editable)
        combo.addItem("split interpolated", LayerSplitType.split_interpolated)
        combo.addItem("split editable", LayerSplitType.split_editable)
        combo.setCurrentIndex(0)
        return combo
