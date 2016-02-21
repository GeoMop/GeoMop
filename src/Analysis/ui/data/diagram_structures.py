from enum import Enum
import pipeline

class NodeType(Enum):
    """Node types"""
    base = 0
    transformation = 1
    iteration = 2
    
port_types = pipeline.PortTypes()

class Node():
    """
    Class for graphic presentation of task
    """
    def __init__(self):
        self.name = "New Node"
        """name of node"""
        self.type = NodeType.base
        """type of node (graphic presentation)"""
        self.in_ports = []
        """input ports class"""
        self.in_ports_rect = []
        """input ports Rect for connection between nodes"""
        self.out_ports = []
        """otput ports class"""
        self.in_ports_rect = []
        """output ports Rect for connection between nodes"""
        self.task = None
        """Object represeted task behind node"""

class Connection():
    """
    Class for graphic presentation of task
    """
    def __init__(self):
        self.in_port = None
        """input port class"""
        self.out_ports = None
        """otput port class"""
        self.connection_rect = []
        """input ports Rect for connection between nodes"""
        
        self.in_ports_rect = []
        """output ports Rect for connection between nodes"""
        self.task = None
        """Object represeted task behind node"""
