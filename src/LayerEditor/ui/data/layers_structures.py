import PyQt5.QtCore as QtCore

class Layer():
    """One layer in panel"""
    
    def __init__(self, name):
        self.name = name
        """Layer name"""
        self.rect = QtCore.QRectF(0, 0, 0, 0)
        """Clicable name area"""
        
class Fracture():
    """One fracture in panel"""
    
    def __init__(self, name):
        self.name = name
        """Fracture name"""
        self.rect = QtCore.QRectF(0, 0, 0, 0)
        """Clicable name area"""

class Interface():
    """One interface in panel"""

    def __init__(self, depth, fracture=None, diagram_id1=None, diagram_id2=None):
        self.depth = depth
        """String depth description"""
        self.fracture = fracture
        """Fracture object or None if fracture is not on interface"""
        self.diagram_id1 = diagram_id1
        """First diagram id. None if interface is enterpolated"""
        self.diagram_id2 = diagram_id2
        """Second diagram id. None if interface has not two independent Note Sets"""
        self.edited = 0
        """is diagram edited (0,1,2 for no, first, second)"""
        self.viewed = 0
        """is diagram viwed (0,1,2 for no, first, second)"""
        self.rect = QtCore.QRectF(0, 0, 0, 0)
        """Clicable name area"""
        self.view_rect1 = None
        """Clicable view check box area"""
        self.edit_rect1 = None
        """Clicable edit check box area"""
        self.view_rect2 = None
        """Clicable view check box area"""
        self.edit_rect2 = None
        """Clicable edit check box area"""

class Layers():
    """Layers data"""
    
    def __init__(self):
        self.layers = []
        """List of layers"""
        self.interfaces = []
        """List of interfaces"""
        self.font = QtGui.QFont()
        """Lazer diagram font"""
        
    def add_interface(self, depth, fracture=None, diagram_id1=None, diagram_id2=None):
        """add new interface"""
        self.interfaces.append(Interface(depth, fracture, diagram_id1, diagram_id2))
        return len(self.interfaces)-1
        
    def add_layer(self, name):
        """add new layer"""
        self.layers.append(Layers(name))
        return len(self.layers)-1
