"""
Geomop's dialogs used in more geomop apllications
that have standartized appearent
"""
import PyQt5.QtWidgets as QtWidgets


class GMErrorDialog(QtWidgets.QMessageBox):
    """Error dialog for GeoMop graphic applications"""
    def __init__(self, parent):
        """
        Inicialize standart QDialoc with GeoMop specific properties"""
        super(GMErrorDialog, self).__init__(parent)
        self.setIcon(QtWidgets.QMessageBox.Critical)

    def open_error_dialog(self, text, error=None, title="GeoMop Error"):
        """Display dialog with title, text and error message in detail"""
        self.setWindowTitle(title)
        self.setText(text)
        if error == None:
            self.setInformativeText("")
        else:
            self.setInformativeText(type(error).__name__ +" "+str(error))
        super(GMErrorDialog, self).exec_()
