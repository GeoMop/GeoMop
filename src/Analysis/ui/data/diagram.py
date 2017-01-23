from .diagram_structures import Node, Connection
from .action_def import  ACTION_TYPES
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
        self.recount_node_uniqueness(node.action_def.name)
        return node
        
    def delete_node(self, node):
        """Delete action and all its connections from
        diagram data scheme"""
        del_conn = []
        for conn in self.connections:
            if conn.input is node or conn.output is node:
                del_conn.append(conn)
        for conn in del_conn:
            self.delete_connection(conn)
        aname = node.action_def.name
        self.nodes.remove(node)
        self.recount_node_uniqueness(aname)

    def recount_node_uniqueness(self, aname):
        """repair nodes unique numbering"""
        first = None
        i = 1
        for node in self.nodes:
            if node.action_def.name==aname:
                if first is None:
                    first = node
                node.unique=i
                i += 1
        if i==2:
            first.unique=0
        
    def add_connection(self, in_node, out_node):
        """Add new connection to diagram data scheme"""
        conn =  Connection(in_node, out_node)
        self.connections.append(conn)
        return conn

    def delet_connection(self, conn):
        """Add new connection to diagram data scheme"""
        self.connections.remove(conn)

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
                
    def get_conn(self, node, pos):
        """
        return connection for set node and possition
        """
        for conn in self.connections:
            if conn.is_conn_point(node, pos):
                return conn
        return None
        
    def get_action_dict(self):
        """return dict of action grouped to dictionary accoding group"""
        dict = {}
        for i in range(0, len(ACTION_TYPES)):
            if ACTION_TYPES[i].group not in dict:
                dict[ACTION_TYPES[i].group] = []
            dict[ACTION_TYPES[i].group].append(i)
        return dict
    
    @staticmethod
    def action_template(i):
        """return action template i"""
        return ACTION_TYPES[i]
        
 
