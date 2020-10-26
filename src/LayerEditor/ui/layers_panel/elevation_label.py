from PyQt5.QtWidgets import QLabel


class ElevationLabel(QLabel):
    def __init__(self, elevation):
        super(ElevationLabel, self).__init__("{}".format(elevation))
        self.setContentsMargins(5, 0, 0, 0)




