import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
from leconfig import cfg

class Mash(QtWidgets.QGraphicsPolygonItem):
    """ 
        Represents a join of nodes in the diagram
    """
    
    STANDART_ZVALUE = 1000
    DASH_PATTERN = [10, 5]
    
    def __init__(self, quad, u, v, parent=None):
        polygon = QtGui.QPolygonF()        
        for point in quad:
            polygon.append(QtCore.QPointF(point[0], -point[1]))
        polygon.append(QtCore.QPointF(quad[0][0], -quad[0][1]))
        super(Mash, self).__init__(polygon)
        self.quad = quad 
        self.u = u
        self.v = v
        self.setZValue(self.STANDART_ZVALUE)
        
    def set_quad(self, quad):
        """Set quad"""
        self.quad = quad
        polygon = QtGui.QPolygonF()
        for point in quad:
            polygon.append(QtCore.QPointF(point[0], -point[1]))
        polygon.append(QtCore.QPointF(quad[0][0], -quad[0][1]))
        self.setPolygon(polygon)
        
        
    def paint(self, painter, option, widget):
        """Redefinition of standard paint function"""
        # don't paint if line is null line        
        painter.setRenderHints(painter.renderHints() | QtGui.QPainter.Antialiasing)
        bold_pen = QtGui.QPen(cfg.diagram.pen)
        bold_pen.setWidthF(3*cfg.diagram.pen.widthF())
        bold_pen.setColor(QtGui.QColor("#ffb71c"))
        dash_pen = QtGui.QPen(cfg.diagram.pen)
        dash_pen.setWidthF(cfg.diagram.pen.widthF())
        #dash_pen.setDashPattern(self.DASH_PATTERN)
        dash_pen.setColor(QtGui.QColor("#ffb71c"))
        
        painter.setPen(bold_pen)
        painter.drawLine(QtCore.QLineF(self.quad[0][0], -self.quad[0][1], 
            self.quad[1][0], -self.quad[1][1]))
        painter.drawLine(QtCore.QLineF(self.quad[0][0], -self.quad[0][1], 
            self.quad[-1][0], -self.quad[-1][1]))    
        painter.setPen(dash_pen)
        for i in range(1, self.u+1):
            for j in range(1, self.v+1):
                painter.drawLine(self._make_point(self.quad[0],self.quad[-1], i, self.u),
                    self._make_point(self.quad[1],self.quad[2], i, self.u))
                painter.drawLine(self._make_point(self.quad[0],self.quad[1], j, self.v),
                    self._make_point(self.quad[3],self.quad[2], j, self.v))
                
    def _make_point(self, pmin, pmax, i, max):
        """Return devided point"""
        return QtCore.QPointF(pmin[0]+(pmax[0]-pmin[0])/max*i,
            -pmin[1]-(pmax[1]-pmin[1])/max*i)
        
            
