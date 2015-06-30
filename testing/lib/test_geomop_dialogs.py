import geomop_dialogs
import sys
from PyQt5.QtTest import QTest
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import threading
import time

def test_err_dialog(request): 
    label=None
    err_dialog=None
#    threading.Thread(target=start_app, args=(label,err_dialog))
#   #QTest.mouseClick(err_dialog._add_button, Qt.LeftButton)
#    time.sleep( 5 )
#    assert err_dialog.buttons() == ""
#
#
#def start_app(label, err_dialog):
#    app=QApplication(sys.argv)
#    label = QLabel("test dialog")
#    label.setWindowFlags(Qt.SplashScreen)
#    label.show()
#    text = None
#    try:
#        file_name="not_esist_file.txt"
#        file_d = open(file_name, 'r')
#        text = file_d.read()
#        file_d.close()
#    except (RuntimeError, IOError) as err:
#        err_dialog = geomop_dialogs.GMErrorDialog(label)
#        err_dialog.open_error_dialog("Can't open file", err)
#    app.quit()
