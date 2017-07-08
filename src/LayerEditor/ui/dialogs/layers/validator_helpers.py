"""
Dialogs for settings text name property or depth
"""

from geomop_dialogs import GMErrorDialog
import PyQt5.QtGui as QtGui

class ValidatorHelpers():

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
