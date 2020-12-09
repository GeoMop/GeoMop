import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore

class Grid(QtWidgets.QGraphicsPolygonItem):
    """ 
    Represents a join of nodes in the diagram
    """
    
    STANDART_ZVALUE = 1000
    DASH_PATTERN = [10, 5]
    
    def __init__(self, quad, u_knots, v_knots, parent=None):
        polygon = QtGui.QPolygonF()        
        for point in quad:
            polygon.append(QtCore.QPointF(point[0], -point[1]))
        polygon.append(QtCore.QPointF(quad[0][0], -quad[0][1]))
        super(Grid, self).__init__(polygon)
        self.quad = quad
        self.u_knots = u_knots
        self.v_knots = v_knots
        self.setZValue(self.STANDART_ZVALUE)
        
    def set_quad(self, quad, u_knots, v_knots):
        """Set quad"""
        self.quad = quad
        polygon = QtGui.QPolygonF()
        for point in quad:
            polygon.append(QtCore.QPointF(point[0], -point[1]))
        polygon.append(QtCore.QPointF(quad[0][0], -quad[0][1]))
        self.u_knots = u_knots
        self.v_knots = v_knots
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
                          self.quad[2][0], -self.quad[2][1]),
            QtCore.QLineF(self.quad[2][0], -self.quad[2][1],
                          self.quad[3][0], -self.quad[3][1]),
            QtCore.QLineF(self.quad[3][0], -self.quad[3][1],
                          self.quad[0][0], -self.quad[0][1])
            ]
        painter.setPen(bold_pen)
        painter.drawLines(lines)

        lines = []

        for uk in self.u_knots:
            lines.append(QtCore.QLineF(
                self._make_point(self.quad[0], self.quad[3], uk),
                self._make_point(self.quad[1], self.quad[2], uk)))

        for vk in self.v_knots:
            lines.append(QtCore.QLineF(
                self._make_point(self.quad[2], self.quad[3], vk),
                self._make_point(self.quad[1], self.quad[0], vk)))


        painter.setPen(dash_pen)
        painter.drawLines(lines)

    def _make_point(self, pmin, pmax, uk):
        """Return devided point"""
        return QtCore.QPointF(pmin[0]+(pmax[0]-pmin[0])*uk,
                              -pmin[1]-(pmax[1]-pmin[1])*uk)
