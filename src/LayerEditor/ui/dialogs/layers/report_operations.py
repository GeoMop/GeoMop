import PyQt5.QtWidgets as QtWidgets

class ReportOperationsDlg(QtWidgets.QMessageBox):
    """Information dialog for layers"""
    
    def __init__(self, title, messages, parent):
        """Initialize standard QDialog with GeoMop specific properties."""
        super(ReportOperationsDlg, self).__init__(parent)
        self.setWindowTitle(title)
        self.setText("This operation will be processed:")
        self.setInformativeText("\n".join(messages))
        self.setIcon(QtWidgets.QMessageBox.Information)
        self.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
