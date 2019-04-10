import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore

class Grid(QtWidgets.QGraphicsPolygonItem):
    """ 
    Represents a join of nodes in the diagram
    """
    
    STANDART_ZVALUE = 1000
    DASH_PATTERN = [10, 5]
    
    def __init__(self, quad, nuv, parent=None):
        polygon = QtGui.QPolygonF()        
        for point in quad:
            polygon.append(QtCore.QPointF(point[0], -point[1]))
        polygon.append(QtCore.QPointF(quad[0][0], -quad[0][1]))
        super(Grid, self).__init__(polygon)
        self.quad = quad
        self.u, self.v = nuv
        self.setZValue(self.STANDART_ZVALUE)
        
    def set_quad(self, quad, nuv):
        """Set quad"""
        self.quad = quad
        polygon = QtGui.QPolygonF()
        for point in quad:
            polygon.append(QtCore.QPointF(point[0], -point[1]))
        polygon.append(QtCore.QPointF(quad[0][0], -quad[0][1]))
        self.u, self.v  = nuv
        self.setPolygon(polygon)
        self.update()
        
        
    def paint(self, painter, option, widget):
        """Redefinition of standard paint function"""
        # don't paint if line is null line        

        dash_pen = QtGui.QPen(QtGui.QColor("#ffb71c"))
        dash_pen.setCosmetic(True)

        bold_pen = QtGui.QPen(dash_pen)
        bold_pen.setWidth(3)


        lines = [
            QtCore.QLineF(self.quad[0][0], -self.quad[0][1],
                          self.quad[1][0], -self.quad[1][1]),
            QtCore.QLineF(self.quad[1][0], -self.quad[1][1],
                          self.quad[2][0], -self.quad[2][1])
            ]
        painter.setPen(bold_pen)
        painter.drawLines(lines)

        lines = []
        for i in range(1, self.u+1):
            for j in range(0, self.v):
                lines.append(QtCore.QLineF(
                    self._make_point(self.quad[0], self.quad[-1], i, self.u),
                    self._make_point(self.quad[1], self.quad[2], i, self.u)))
                lines.append(QtCore.QLineF(
                    self._make_point(self.quad[0],self.quad[1], j, self.v),
                    self._make_point(self.quad[3],self.quad[2], j, self.v)))

        painter.setPen(dash_pen)
        painter.drawLines(lines)

    def _make_point(self, pmin, pmax, i, max):
        """Return devided point"""
        return QtCore.QPointF(pmin[0]+(pmax[0]-pmin[0])/max*i,
            -pmin[1]-(pmax[1]-pmin[1])/max*i)
        
            
