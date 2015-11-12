"""Start script that inicialize main window """
import sys
import os
__lib_dir__ = os.path.join(os.path.split(
    os.path.dirname(os.path.realpath(__file__)))[0], "common")
sys.path.insert(1, __lib_dir__)

from ui import panels
import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets

class LayerEditor:
    """Layeout editor main class"""
    
    def __init__(self):
        self._app = QtWidgets.QApplication(sys.argv)
        self._hsplitter1 = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self._hsplitter1.setWindowTitle("GeoMop Layer Editor")
        self._form1 = panels.addpicture.AddPictureWidget(self._hsplitter1)
        self._form2 = panels.canvas.CanvasWidget(self._hsplitter1)
        self._hsplitter1.addWidget(self._form1)
        self._hsplitter1.addWidget(self._form2)
        self._hsplitter1.show()
        self._form1.pictureListChanged.connect(self._picture_list_changed)

    def main(self):
        """go"""        
        self._app.exec_()

    def _picture_list_changed(self):
        """
        Send list of background pictures from :mod:`Panels.AddPictureWidget`
        to :mod:`Panels.CanvasWidget`
        """
        self._form2.set_undercoat(self._form1.get_pixmap(1200, 800,  10))

if __name__ == "__main__":
    LayerEditor().main()

