import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
from leconfig import cfg

class InitArea(QtWidgets.QGraphicsPolygonItem):
    """ 
        Represents a join of nodes in the diagram
    """
    
    STANDART_ZVALUE = -1000
    
    def __init__(self, diagram, parent=None):
        poly = diagram.get_area_poly(cfg.layers, cfg.diagrams.index(diagram))
        super(InitArea, self).__init__(poly)
        self.setPen(QtGui.QPen(QtCore.Qt.NoPen))
        brush = QtGui.QBrush(QtGui.QColor(246, 246, 246))
        self.setBrush(brush)
        self.setZValue(self.STANDART_ZVALUE) 
                
    def reload(self):
        """Reload new init area"""
        poly = cfg.diagram.get_area_poly(cfg.layers, cfg.diagrams.index(cfg.diagram))
        self.setPolygon(poly)    
 
    
