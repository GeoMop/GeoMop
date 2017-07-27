import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
from leconfig import cfg

class DiagramView(QtWidgets.QGraphicsItem):
    """ 
        Represents some diagram view in edited diagram background
    """
    
    ZVALUE = -9
    
    def __init__(self, diagram_id, parent=None):
        super(DiagramView, self).__init__(parent)
        self.id = diagram_id
        cfg.diagram.views_object[diagram_id] = self
        self.setZValue(self.ZVALUE) 
        
    def boundingRect(self):
        """Redefination of standart boundingRect function, that return boun rect"""
        r = cfg.diagram.pen.widthF()
        rect = cfg.diagrams[self.id].rect
        rect.adjust(-r, -r, r, r)
        return rect

    def paint(self, painter, option, widget):
        """Redefination of standart paint function, that paint object from shape file"""
        r = cfg.diagram.pen.widthF()
        view_diagram = cfg.diagrams[self.id]
        
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
        del cfg.diagram.views_object[self.id]    
