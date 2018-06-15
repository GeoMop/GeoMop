import gm_base.geomop_dialogs
from PyQt5.QtTest import QTest
from PyQt5.QtCore import QTimer, Qt
from PyQt5.Qt import QSplashScreen
import pytest

@pytest.mark.qt
def test_err_dialog(request, qapp):
    global dialog_result

    dialog_result = {}

    splash = QSplashScreen()
    splash.show()
    text = None

    try:
        file_name="not_exist_file.txt"
        file_d = open(file_name, 'r')
        text = file_d.read()
        file_d.close()
    except (RuntimeError, IOError) as err:
        assert text is None
        err_dialog = gm_base.geomop_dialogs.GMErrorDialog(splash)
        timer=QTimer(splash)
        timer.timeout.connect(lambda: start_dialog(err_dialog))
        timer.start(1000)
        err_dialog.open_error_dialog("Can't open file", err)


    del splash


    #button tests
    assert dialog_result['button_count'] == 1
    assert dialog_result['button_text'] in ('&OK', 'OK')
    #text test
    assert dialog_result['text'] == "Can't open file"
    assert dialog_result['informativeText'][:12] == "FileNotFound"
    assert dialog_result['title'] == "GeoMop Error"

def start_dialog(dialog):
    global dialog_result
    dialog_result['button_count'] = len(dialog.buttons())
    ok_button = dialog.buttons()[0]
    dialog_result['button_text'] = ok_button.text()
    dialog_result['informativeText']=dialog.informativeText()
    dialog_result['text']=dialog.text()
    dialog_result['title']=dialog.windowTitle()
    QTest.mouseClick(ok_button, Qt.LeftButton)
