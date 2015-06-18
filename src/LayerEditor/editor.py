"""Start script that inicialize main window """

import sys
sys.path.insert(1, '../lib')

import panels.addpicture
import panels.canvas
import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets

class Editor:
    """Layeout editor main class"""
    
    def __init__(self):
        self._app = QtWidgets.QApplication(sys.argv)
        self._messageSplitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self._messageSplitter.setWindowTitle("GeoMop Layer Editor")
        self._form1 = panels.addpicture.AddPictureWidget(self._messageSplitter)
        self._form2 = panels.canvas.CanvasWidget(self._messageSplitter)
        self._messageSplitter.addWidget(self._form1)
        self._messageSplitter.addWidget(self._form2)
        self._messageSplitter.show()
        self._form1.pictureListChanged.connect(self._picture_list_changed)

    def main(self):
        """go"""        
        self._app.exec_()

    def _picture_list_changed(self):
        """
        Send list of background pictures from :mod:`Panels.AddPictureWidget`
        to :mod:`Panels.CanvasWidget`
        """
        self._form2.set_undercoat(self._form1.get_pixmap(100, 100))

Editor().main()

