"""
Start script that inicialize main window
"""

import sys
sys.path.insert(1, '../lib')

from Panels.AddPictureWidget import *
from Panels.CanvasWidget import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from langLE import gettext as _ 

app = QApplication(sys.argv)
messageSplitter = QSplitter(Qt.Horizontal)
messageSplitter.setWindowTitle(_("GeoMop Layer Editor"))
form1 = AddPictureWidget(messageSplitter )
form2 = CanvasWidget(messageSplitter )
    
messageSplitter.addWidget(form1)
messageSplitter.addWidget(form2)
messageSplitter.show()
 
def pictureListChanged():
    """
    Send list of background pictures from :mod:`Panels.AddPictureWidget` 
    to :mod:`Panels.CanvasWidget` 
   
    """
    form2.setBacground(form1.getPicturePaths())
  
form1.pictureListChanged.connect(pictureListChanged) 
 
app.exec_()
