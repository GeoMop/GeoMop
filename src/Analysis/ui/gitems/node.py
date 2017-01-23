import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore

from .items_action import RequiredAction
from .connection import Connection

class Node(QtWidgets.QGraphicsRectItem):
    """ 
    Represents a block in the diagram 
    """
    WIDTH = 140.0
    HEIGHT = 80.0
    HEAD_SIZE = 21    
   
    def __init__(self, node, parent=None):
        self.selected = False
        """if item is selected"""
        super(Node, self).__init__(parent)        
        self._node = node
        self.setFlags(self.ItemIsMovable)
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.setRect(0.0, 0.0, self.WIDTH, self.HEIGHT)
        self.setPos(node.pos.x(),node.pos.y()) 
        self.set_ports_rects()
 
    def set_ports_rects(self):
        """recount ports possition, call after node possition changing"""
        rect_width = self.HEAD_SIZE/3
        pos = self.pos()
        for i in range(0, len(self._node.in_ports_pos)):            
            self._node.in_ports_pos[i] = QtCore.QPointF(
                rect_width*1.5+pos.x(),
                rect_width*1.5+i*self.HEAD_SIZE+pos.y())
        self._node.out_port_pos = QtCore.QPointF(
            self.WIDTH + pos.x()-1.5*rect_width, 
            self.HEIGHT + pos.y()-1.5*rect_width)
            
    def get_port_number(self, cursor):
        """
        If slot in set possition, returns its number. Cursor is
        set in item coordinates
        
        0-n - number of input slot
        -1 no slot
        -2 output slot
        """
        rect_width = self.HEAD_SIZE/3
        for i in range(0, len(self._node.in_ports_pos)):            
            rect = QtCore.QRectF(
                rect_width + i*self.HEAD_SIZE, 
                rect_width, 
                rect_width, 
                rect_width)
            if rect.contains(cursor):
                return i
        rect = QtCore.QRectF(
            self.WIDTH-2*rect_width, 
            self.HEIGHT-2*rect_width, 
            rect_width, 
            rect_width)
        if rect.contains(cursor):
            return -2
        return -1
        
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
        painter.drawText(text_rect, QtCore.Qt.AlignCenter, self._node. unique_name)
        #paint head
        rect_width = self.HEAD_SIZE/3
        for i in range(0, len(self._node.in_ports_pos)):            
            rect = QtCore.QRectF(rect_width + i*self.HEAD_SIZE, rect_width, rect_width, rect_width)
            painter.drawRect(rect)
        #pait tail
        rect = QtCore.QRectF(self.WIDTH-2*rect_width, self.HEIGHT-2*rect_width, rect_width, rect_width)
        painter.drawRect(rect)
        # paint focus        
        if self.selected:
            painter.setPen(QtGui.QPen(QtCore.Qt.red, 3))
            painter.setBrush(QtGui.QBrush(QtCore.Qt.NoBrush))
            painter.drawRect(QtCore.QRect(0,0, self.WIDTH, self.HEIGHT))

    def mark_invalid(self):
        """Qt standart event"""
        self.set_ports_rects()
        self._node.repaint_conn = True        
        
    def mousePressEvent(self,event):
        """Standart mouse event"""        
        if event.items_action.item is not None and \
            isinstance(event.items_action.item, Connection):
            if self.get_port_number(event.pos()) != -1:
                event.items_action.item = self
                event.items_action.action = RequiredAction.conn_move
            return
        event.items_action.item = self
        if self.get_port_number(event.pos()) != -1:
            event.items_action.action = RequiredAction.conn_add
            return
        if event.button()==QtCore.Qt.RightButton:
            event.items_action.action = RequiredAction.node_menu
            return
        super(Node, self). mousePressEvent(event)                
        event.items_action.action = RequiredAction.node_focus
    
    def get_conn(self, node, pos, data):
        """
        return connection for set node and possition
        
        pos is in scene coordinates
        """
        i = self.get_port_number(pos-self.pos())
        if i>0 and i<len(self._node.in_ports_pos):
            return data.get_conn(self._node, self._node.in_ports_pos[i])
        elif i==-2:
            return data.get_conn(self._node, self._node.out_ports_pos)
        return None
