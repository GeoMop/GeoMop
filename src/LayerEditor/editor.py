# pylint: disable=C0103
"""Start script that inicialize main window """

import sys
sys.path.insert(1, '../lib')

import panels.addpicture
import panels.canvas
import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets
from lang_le import gettext as _

_app = QtWidgets.QApplication(sys.argv)
_messageSplitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
_messageSplitter.setWindowTitle(_("GeoMop Layer Editor"))
_form1 = panels.addpicture.AddPictureWidget(_messageSplitter)
_form2 = panels.canvas.CanvasWidget(_messageSplitter)

_messageSplitter.addWidget(_form1)
_messageSplitter.addWidget(_form2)
_messageSplitter.show()

def _picture_list_changed():
    """
    Send list of background pictures from :mod:`Panels.AddPictureWidget`
    to :mod:`Panels.CanvasWidget`

    """
    _form2.set_undercoat(_form1.get_picture_paths())

_form1.pictureListChanged.connect(_picture_list_changed)
_app.exec_()
