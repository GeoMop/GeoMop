import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore

class Blink(QtWidgets.QGraphicsRectItem):
    """ 
        Represents a shp file diagram background
    """
    
    ZVALUE = -1000
    
    def __init__(self, rect, parent=None):
        super(Blink, self).__init__(rect, parent)
        brush = QtGui.QBrush(QtGui.QColor(232, 232, 232))
        self.setBrush(brush)     
        self.setZValue(self.ZVALUE)
