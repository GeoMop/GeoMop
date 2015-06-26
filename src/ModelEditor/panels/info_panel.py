import PyQt5.QtWidgets as QtWidgets
from data.meconfig import MEConfig as cfg

class InfoPanelWidget(QtWidgets.QLabel):

    def __init__(self):
        QtWidgets.QLabel.__init__(self)
