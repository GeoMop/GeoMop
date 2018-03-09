from ModelEditor.ui.panels.tree import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtTest import QTest
import testing.ModelEditor.mock.mock_config as mockcfg
from PyQt5.Qt import QApplication
import sys
import pytest


# def setup_module(module):
#     module.app = QApplication(sys.argv)
#
#
# def teardown_module(module):
#     module.app.quit()


signal_is_send = None
x=None

@pytest.mark.qt
def test_loadPanel(request, qapp):
    global  signal_is_send,  x

    # Setup mockcfg
    # Alternatively one can create a fixture if this same test configuration
    # is used in more tests. In order to guarantee order of teardown one should
    # have fixture dependency like:
    # @pytest.fixture
    # def mockcfg(qapp):
    #     ...
    mockcfg.set_empty_config()
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
    panel.show()
    timer = QTimer(panel)
    timer.timeout.connect(lambda: start_dialog(panel))
    timer.start(100)
    qapp.exec()


    #test poslani signalu
    assert not signal_is_send
    assert x is None


    # Teardown
    mockcfg.clean_config()

def start_dialog(panel):
    QTest.mouseClick(panel, Qt.LeftButton)

def _tree_item_changed(x1, y1, x2, y2):
    global  signal_is_send
    global x
    signal_is_send=True
    x=x1
    qapp.quit()
