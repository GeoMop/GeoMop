import sys
from panels.addpicture import *
from panels.addpicture import _AddPictureData as Data
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
def test_loadPanel(request):
    global  signal_is_send
    
    Data.SERIAL_FILE = "AddPictureData_test"
    panel = AddPictureWidget( )
    def fin_test_config():
        import config
        config.delete_config_file("AddPictureData_test")
    request.addfinalizer(fin_test_config)    
    
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
    assert len(panel._data.pic_paths)==2
    assert len(panel._data.pic_names)==2

def _picture_list_changed():
    global  signal_is_send
    signal_is_send=True
