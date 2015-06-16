import sys
from panels.addpicture import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtTest import QTest
import pytest

app = QApplication(sys.argv)
app_not_init = pytest.mark.skipif( not (type(app).__name__=="QApplication"), 
    reason="App not inicialized")
signal_is_send = None

def test_loadApp():
    #test inicializace qt applikace
    assert  type(app).__name__=="QApplication"    

@app_not_init
def test_loadPanel():
    global  signal_is_send
    panel = AddPictureWidget( )
    #test inicializace panelu
    assert  type(panel).__name__=="AddPictureWidget"
    _d = os.path.dirname(os.path.realpath(__file__))
    panel._file_name.setText(_d + "/data/test.png")
    signal_is_send=False
    panel.pictureListChanged.connect(_picture_list_changed)
    QTest.mouseClick(panel._add_button, Qt.LeftButton)
    #test poslani signalu
    assert not signal_is_send
    #test pridani item
    assert len(panel._list[0])==3
    assert len(panel._list[1])==3

def _picture_list_changed():
    global  signal_is_send
    signal_is_send=True
