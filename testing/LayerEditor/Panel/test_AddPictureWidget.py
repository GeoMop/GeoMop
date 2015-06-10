import sys
from Panels.AddPictureWidget import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pytest

app = QApplication(sys.argv)
appNotInit=pytest.mark.skipif(True)

def test_loadApp():
    #test inicializace qt applikace
    assert  type(app).__name__=="QApplication"
    appNotInit= pytest.mark.skipif( not (type(app).__name__=="QApplication"))

@appNotInit
def test_loadPanel():    
    panel = AddPictureWidget( )
    #test inicializace panelu
    assert  type(panel).__name__=="AddPictureWidget"
