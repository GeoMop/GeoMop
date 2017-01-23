"""Diagram file"""
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
from ui.gitems import Node, Connection, ItemsAction, RequiredAction

class Diagram(QtWidgets.QGraphicsScene):
    """GeoMop design area"""

    def __init__(self, data, parent=None):
        """
        Inicialize window

        Args:
            parent (QWidget): parent window ( empty is None)
        """ 
        self._data = data
        self._conn = []
        """List of connections"""
        self.selected_node = None
        """selected node"""
        self.repairing_connection = None
        """
        If connection is about changes, is in this variable 
        
        """
        super(Diagram, self).__init__(parent)        
        self.set_data(data)        
        
    def set_data(self, data):
        """set data structure to Graphic Scene"""
        self._data = data
        self.clear()
        self._conn = []
        for node in data.nodes:
            n = Node(node)
            self.addItem(n) 
        for conn in data.connections:
            c = Connection(conn)
            self.addItem(c)  
            self._conn.append(c)            

    def mouseMoveEvent(self, event):
        """Standart mouse event"""
        super(Diagram, self).mouseMoveEvent(event)
        item = self.mouseGrabberItem() 
        if item is not None:
            item.mark_invalid()
            self._data.mark_invalid_connections()
            for conn in self._conn:
                if conn.need_repaint():
                    conn.set_path()
                    #conn.update()   
                 
    def _select_node(self, node):
        """select set node"""
        if isinstance(node, Node):
            if self.selected_node is not None:
                self.selected_node.selected = False
                self.selected_node.update()
            self.selected_node = node                 
            self.selected_node.selected = True
            self.selected_node.update()
            
    def mousePressEvent(self,event):
        """Standart mouse event"""
        event.items_action = ItemsAction()
        super(Diagram, self). mousePressEvent(event)
        if event.items_action.item is not None and \
           event.items_action.action != RequiredAction.no_action:
            if event.items_action.action is RequiredAction.node_focus:
                self._select_node(event.items_action.item)
            elif event.items_action.action is RequiredAction.conn_add:
                if isinstance( event.items_action.item, Node):
                    if event.items_action.item.get_conn(
                       event.items_action.item, event.scenePos(), self._data) is not None:
                        self._con_move_menu(event, event.items_action.item)
                    else:
                        self._con_add_menu(event, event.items_action.item)
            elif event.items_action.action is RequiredAction.conn_move:
                if isinstance( event.items_action.item, Node):
                    self._con_move_menu(event, event.items_action.item)
            elif event.items_action.action is RequiredAction.conn_delete:
                if isinstance( event.items_action.item, Connection):
                    self._con_delete_menu(event, event.items_action.item)
            elif event.items_action.action is RequiredAction.node_menu:
                if isinstance( event.items_action.item, Node):
                    self._node_menu(event, event.items_action.item)
        elif event.items_action.item is None and \
            event.button()==QtCore.Qt.RightButton:
            self._diagram_menu(event)
            
                
    def _con_add_menu(self, event, node):            
        menu =  QtWidgets.QMenu()
        menu.addAction("Add Connection")
        menu.exec_(event.screenPos())

    def _con_move_menu(self, event, node):            
        menu =  QtWidgets.QMenu()        
        menu.addAction("Move Connection")
        if node.get_port_number(event.pos())==-2:
            menu.addAction("Add Connection")
        menu.addAction("Delete Connection")
        menu.exec_(event.screenPos())

    def _con_delete_menu(self, event, conn):            
        menu =  QtWidgets.QMenu()
        menu.addAction("Delete Connection")
        menu.addAction("Move Connection Point ({0})".format(
            conn.get_point_desc(0)))
        menu.addAction("Move Connection Point ({0})".format(
            conn.get_point_desc(1)))
        menu.exec_(event.screenPos())

    def _node_menu(self, event, node):            
        menu =  QtWidgets.QMenu()
        menu.addAction("Add Node Input Port")
        menu.addAction("Delete Node Input Port")
        menu.addAction("Delete Node")
        menu.exec_(event.screenPos())
        
    def _diagram_menu(self, event):
        group_actions = self._data.get_action_dict() 
        menu =  QtWidgets.QMenu()
        for group, actions in group_actions.items(): 
            group_menu = menu.addMenu(group)
            pom_lamda = lambda action_template, pos : lambda: self. _add_action(action_template, pos)
            for atemp in  actions:
                faction = QtWidgets.QAction(self._data.action_template(atemp).name, menu)
                faction.setStatusTip(self._data.action_template(atemp).description)
                group_menu.addAction(faction)
                faction.triggered.connect(pom_lamda(atemp, event.scenePos()))
        menu.exec_(event.screenPos())
                
    def _add_action(self, action_template, pos):
        """add action to set pos in scene coordinate"""
        node = self._data.add_node(pos.x(), pos.y(), action_template)
        n = Node(node)
        self.addItem(n)
