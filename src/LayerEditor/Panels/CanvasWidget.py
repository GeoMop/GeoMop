from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class CanvasWidget(QWidget):
    
    def __init__(self, parent=None):
        super(CanvasWidget, self).__init__(parent)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding,
                                       QSizePolicy.Expanding))
        self.setMinimumSize(QSize(500, 500))
        self._pictures=None

 #   def mousePressEvent(self, event):
  
  #  def keyPressEvent(self, event):
 
    def paintEvent(self, event=None):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        
        if self._pictures:
            for picture in self._pictures:
                target = painter.window()
                pixmap=QPixmap(picture)
                if pixmap:
                    source = pixmap.rect();
                    painter.drawPixmap(target,pixmap, source);
 

    def setBacground(self, pictures):
        self._pictures=pictures
        self.repaint (0, 0, -1, -1)
