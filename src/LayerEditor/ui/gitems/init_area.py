import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
from LayerEditor.leconfig import cfg

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
        self.reload()
                
    def reload(self):
        """Reload new init area"""
        bbox = cfg.diagram.get_diagram_all_rect(cfg.diagram.rect, cfg.layers, cfg.diagrams.index(cfg.diagram))
        poly = QtGui.QPolygonF(bbox)
        self.setPolygon(poly)
        cfg.diagram.area.gtpolygon = poly
