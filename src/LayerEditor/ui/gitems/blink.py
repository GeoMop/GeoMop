import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
from LayerEditor import definitions

class Blink(QtWidgets.QGraphicsRectItem):
    """ 
    Blink on change for the user friendly behaviour, e.g. layer_block change.
    """
    
    def __init__(self, rect, parent=None):
        super(Blink, self).__init__(rect, parent)
        brush = QtGui.QBrush(QtGui.QColor(232, 232, 232))
        self.setBrush(brush)     
        self.setZValue(definitions.ZVALUE_BLINK)
