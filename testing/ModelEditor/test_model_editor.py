import ModelEditor.model_editor
from PyQt5.QtTest import QTest
from PyQt5.QtCore import QTimer, Qt
import testing.ModelEditor.mock.mock_config as mockcfg
import pytest

@pytest.mark.qt
def test_err_dialog():

    global dialog_result,  editor

    dialog_result = {}
    mockcfg.set_empty_config()
    editor = ModelEditor.model_editor.ModelEditor()


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

    assert dialog_result['title'] == "GeoMop Model Editor - New File"
    assert dialog_result['closed_window'] is True


def start_dialog(editor):
    print("start_dialog")
    global dialog_result

    dialog_result['title'] = editor.mainwindow.windowTitle()
    # simulate press of  'Ctrl-Q'
    QTest.keyPress(editor.mainwindow, Qt.Key_Q,  Qt.ControlModifier)
    dialog_result['closed_window'] = editor.mainwindow.close()
    editor._app.quit()
