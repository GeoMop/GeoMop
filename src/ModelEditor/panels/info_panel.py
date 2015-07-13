import PyQt5.QtWidgets as QtWidgets

class InfoPanelWidget(QtWidgets.QTextEdit):

    def __init__(self):
        QtWidgets.QTextEdit.__init__(self)
        self.setReadOnly(True)
