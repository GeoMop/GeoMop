import LayerEditor.layer_editor as layer_editor
from PyQt5.QtTest import QTest
from PyQt5.QtCore import QTimer, Qt
import testing.LayerEditor.mock.mock_config as mockcfg
import pytest
import sys

@pytest.mark.qt
def test_err_dialog():
    global dialog_result,  editor

    dialog_result = {}
    mockcfg.set_empty_config()
    editor = layer_editor.LayerEditor(False)

    timer = QTimer(editor.mainwindow)
    timer.timeout.connect(lambda: start_dialog(editor))
    print("start timer")
    timer.start(100)
    print("before main")
    editor.main()
    print("after main")
    print("Delete fixture app: ", str(editor._app))
    del editor._app
    del editor
    #sys.exit(0)



    
    assert dialog_result['title'] == "GeoMop Layer Editor - New File"
    assert dialog_result['closed_window'] is True


def start_dialog(editor):
    print("start_dialog")
    global dialog_result

    dialog_result['title'] = editor.mainwindow.windowTitle()
    # simulate press of  'Ctrl-Q'
    QTest.keyPress(editor.mainwindow, Qt.Key_Q,  Qt.ControlModifier)
    dialog_result['closed_window'] = editor.mainwindow.close()
    editor._app.quit()
