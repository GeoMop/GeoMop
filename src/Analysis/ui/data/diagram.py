from .diagram_structures import Node, Connection
import PyQt5.QtCore as QtCore

class Diagram():
    def __init__(self, **kwargs):
        self.nodes = []
        """List of diagram nodes"""
        self.connections = []
        """List of diagram connections"""
        self.file = ""
        """serialize to file"""
        
    def save(self):
        """serialize to file"""
        pass
        
    def load(self):
        """serialize from file"""
        pass
        
    def add_node(self, x, y, template_num):
        """Add new action to diagram data scheme"""
        pos = QtCore.QPoint(x, y)
        node = Node(template_num, pos)
        self.nodes.append(node)
        return node
        
    def add_connection(self, in_node, out_node):
        """Add new connection to diagram data scheme"""
        conn =  Connection(in_node, out_node)
        self.connections.append(conn)
        return conn
        
    def mark_invalid_connections(self):
        """Mark connection to moved nodes for repaint"""
        n = []
        for node in self.nodes:
            if node.repaint_conn:
                n.append(node)
                node.repaint_conn = False
        for conn in self.connections:
            if conn.input in n or conn.output in n:
                conn.repaint = True
