import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore

class Node(QtWidgets.QGraphicsRectItem):
    """ 
    Represents a block in the diagram 
    """
    WIDTH = 140.0
    HEIGHT = 80.0
    HEAD_SIZE = 21
    
   
    def __init__(self, node, parent=None):
        super(Node, self).__init__(parent)
        """repaint related connections"""
        self._node = node
        self.setFlags(self.ItemIsSelectable | self.ItemIsMovable)
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.setRect(0.0, 0.0, self.WIDTH, self.HEIGHT)
        self.setPos(node.pos.x(),node.pos.y()) 
        self.set_ports_rects()
 
    def set_ports_rects(self):
        rect_width = self.HEAD_SIZE/3
        pos = self.pos()
        for i in range(0, len(self._node.in_ports_pos)):            
            self._node.in_ports_pos[i] = QtCore.QPointF(
                rect_width*1.5+pos.x(),
                rect_width*1.5+i*self.HEAD_SIZE+pos.y())
        self._node.out_port_pos = QtCore.QPointF(
            self.WIDTH + pos.x()-1.5*rect_width, 
            self.HEIGHT + pos.y()-1.5*rect_width)
        
    def paint(self, painter, option, widget):
        """paint item"""
        #paint rect
        painter.setPen(QtGui.QPen(QtCore.Qt.black, 2))
        painter.setBrush(QtGui.QBrush(QtCore.Qt.lightGray))
        painter.drawRect(QtCore.QRect(0,0, self.WIDTH, self.HEIGHT))
        #paint text area
        text_rect = QtCore.QRectF(0, self.HEAD_SIZE, self.WIDTH, self.HEIGHT-2*self.HEAD_SIZE)
        painter.setBrush(QtGui.QBrush(QtCore.Qt.white))        
        painter.drawRect(text_rect)
        painter.drawText(text_rect, QtCore.Qt.AlignCenter, self._node.action_def.name)
        #paint head
        rect_width = self.HEAD_SIZE/3
        for i in range(0, len(self._node.in_ports_pos)):            
            rect = QtCore.QRectF(rect_width, rect_width + i*self.HEAD_SIZE , rect_width, rect_width)
            painter.drawRect(rect)
        #pait tail
        rect = QtCore.QRectF(self.WIDTH-2*rect_width, self.HEIGHT-2*rect_width, rect_width, rect_width)
        painter.drawRect(rect)       

    def mark_invalid(self):
        """Qt standart event"""
        self.set_ports_rects()
        self._node.repaint_conn = True

    def contextMenuEvent(self, event):
        i=5
#        menu = QMenu()
#        menu.addAction('Delete')
#        pa = menu.addAction('Parameters')
#        pa.triggered.connect(self.editParameters)
#        menu.exec_(event.screenPos())
#
