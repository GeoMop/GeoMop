import PyQt5.QtCore as QtCore
import pickle

class Task:
    """Class represent one task"""
    def __init__(self):
        """Init task"""
        self.geometry=Geometry()
        """Task's geometry"""
        self.path=""
        """File with path for saving"""

    def load(self):
        """
        Load geometry from data file
        """
        try:
            pkl_file = open(self.path, 'rb')
        except (FileNotFoundError, IOError):
            return None
        self.geometry = pickle.load(pkl_file)
        pkl_file.close()    
    
    def save(self):
        """Save config object to file Name.cfg in config directory"""    
        pkl_file = open(self.path, 'wb')
        pickle.dump(self.geometry, pkl_file)
        pkl_file.close()

class Geometry:
    """Class represent Geometry"""
    
    def __init__(self):
        """Init geometry"""
        self.workspace = QtCore.QRect(0, 0, 100, 100)
        """area for geometry defination"""
        self.layers = []
        """Task's layers"""

class Layer:
    """
    Class represent layer
    
    Description: geometry     
    """

    def __init__(self):
        """Init layer"""
        self.lines = []
        """lines id defined layer's geometry"""
        self.polys = []
        """Polygons that is defined as array of line indexes from variable array lines"""
        self.line_validity = []
        """helper boolean array mark invalid line as false"""
        
    def invalidateLines(self, rect):
        """set helper variable line_validity"""
        self.invalid_lines = []
        for line in self.lines:
            self.ine_validity.append(
                rect.contains(line.p1) and
                rect.contains( line.p2))
        for poly in self.polys:
            if not poly.isValid():
                for line in poly.lines:
                    self.line_validity[line]=False
    
    class _Poly:
        """Class represent polygon"""

        def __init__(self):
            """Init lpolygon"""
            self.lines=[]
            """array of line id"""
            
        def isValid(self):
            """Is lpolygon valid """
            if len(self.lines)<3:
                return False
            return True
