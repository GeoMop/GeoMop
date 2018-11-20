import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
from LayerEditor.leconfig import cfg

class DiagramView(QtWidgets.QGraphicsItem):
    """ 
        Represents some diagram view in edited diagram background
    """
    
    ZVALUE = -9
    
    def __init__(self, diagram_uid, parent=None):
        super(DiagramView, self).__init__(parent)
        self.uid = diagram_uid
        cfg.diagram.views_object[diagram_uid] = self
        self.setZValue(self.ZVALUE) 
        
    def boundingRect(self):
        """Redefination of standart boundingRect function, that return boun rect"""
        id = 0
        if self.uid in cfg.diagrams[0].map_id:
            id = cfg.diagrams[0].map_id[self.uid]
        r = cfg.diagram.pen.widthF()
        rect = cfg.diagrams[id].rect
        rect.adjust(-r, -r, r, r)
        return rect

    def paint(self, painter, option, widget):
        """Redefination of standart paint function, that paint object from shape file"""
        if self.uid in cfg.diagrams[0].map_id:
            id = cfg.diagrams[0].map_id[self.uid]
            r = cfg.diagram.pen.widthF()
            view_diagram = cfg.diagrams[id]
            
            pen = QtGui.QPen(cfg.diagram.pen)
            pen.setStyle(QtCore.Qt.DotLine)
            painter.setPen(pen)
            if painter.pen().style() != QtCore.Qt.DotLine:
                painter.pen().setStyle(QtCore.Qt.DotLine)
                
            painter.setRenderHints(painter.renderHints() | QtGui.QPainter.Antialiasing)
            for line in view_diagram.lines:
                painter.drawLine(line.p1.qpointf(), line.p2.qpointf())
            for point in view_diagram.points:
                painter.drawEllipse(point.qpointf(), r, r)
            pen.setStyle(QtCore.Qt.SolidLine)
            painter.setPen(pen)
         
    def release_view(self):
        del cfg.diagram.views_object[self.uid]    
