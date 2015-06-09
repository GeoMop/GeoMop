import sys
sys.path.insert(0, '../lib')

from Panels.AddPictureWidget import *
from Panels.CanvasWidget import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from lang import gettext as _ 

test=_("Layer below")

app = QApplication(sys.argv)
messageSplitter = QSplitter(Qt.Horizontal)
form1 = AddPictureWidget(messageSplitter )
form2 = CanvasWidget(messageSplitter )
    
messageSplitter.addWidget(form1)
messageSplitter.addWidget(form2)
messageSplitter.show()
 
def pictureListChanged():
    form2.setBacground(form1.getPicturePaths())
  
form1.pictureListChanged.connect(pictureListChanged) 
 
app.exec_()
