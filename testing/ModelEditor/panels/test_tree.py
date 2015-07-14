import sys
from panels.tree import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtTest import QTest
import pytest
import mock_config as mockcfg

app = QApplication(sys.argv)
app_not_init = pytest.mark.skipif( not (type(app).__name__=="QApplication"),
    reason="App not inicialized")
signal_is_send = None
x=None

def test_loadApp():
    global app
    #test inicializace qt applikace
    assert  type(app).__name__=="QApplication"

@app_not_init
def test_loadPanel(request):
    global  signal_is_send,  x

    mockcfg.set_empty_config()
    def fin_test_config():
        mockcfg.clean_config()
    request.addfinalizer(fin_test_config)
    mockcfg.load_complex_structure_to_config()

    panel = TreeWidget()
    #test inicializace panelu
    assert  type(panel).__name__=="TreeWidget"

    #test config mock
    first=panel._model.index(0, 0, QModelIndex())
    second=panel._model.index(1, 0, QModelIndex())
    assert (
            first.data() == "output_streams" and
            second.data() == "problem"
        ) or (
            first.data() == "problem" and
            second.data() == "output_streams"
        )

    panel.itemSelected.connect(_tree_item_changed)
    QTest.mouseClick(panel, Qt.LeftButton)
    #test poslani signalu
    assert not signal_is_send
    assert x is None

def _tree_item_changed(x1, y1, x2, y2):
    global  signal_is_send
    global x
    signal_is_send=True
    x=x1
