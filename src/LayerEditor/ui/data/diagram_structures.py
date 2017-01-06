import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui

class Point():
    """
    Class for graphic presentation of point
    """
    def __init__(self, x, y):
        self.x = x 
        """x coordinate"""
        self.y = y 
        """y coordinate"""
        self.lines = []
        """This point instance is use for these lines"""
        self.object = None
        """Graphic object""" 
        
    def __lt__(self, other):
        """operators for comparation"""
        if self.x<other.x or (self.x==other.x and self.y<other.y):
            return True
        return False
        
    def __le__(self, other):
        """operators for comparation"""        
        if self.x<other.x:
            return True
        if self.x==other.x and self.y==other.y:
            assert self is other
            return True
        return False
        
    def __eq__(self, other):
        """operators for comparation"""
        return self is other
        
    def __ne__(self, other):
        """operators for comparation"""
        return self is not other
        
    def __gt__(self, other):
        """operators for comparation"""
        if self.x>other.x or (self.x==other.x and self.y>other.y):
            return True
        return False
        
    def __ge__(self, other):
        """operators for comparation"""
        if self.x>other.x:
            return True
        if self.x==other.x and self.y==other.y:
            assert self is other
            return True
        return False

        

class Line():
    """
    Class for graphic presentation of line
    """
    def __init__(self, p1, p2):
        self.p1 = p1
        """First point"""
        self.p2 = p2
        """Second point"""
        self.object = None
        """Graphic object"""        

class Diagram():
    """
    Layer diagram
    
    Use only class functions for adding new shapes. This function ensure olloving 
    requirements. New class function must ensure this requirements too.
    requirements::
        - All points is unique
        - All points contains used lines
        - Point is griater if is right or x coordinate is equol and point is below 
        - Line.p1<line.p2
    """
    def __init__(self):       
        self._rect = None
        """canvas Rect"""
        self.points = []
        """list of points"""
        self.lines = []
        """list of lines"""
        self._zoom = 1.0
        """zoom"""
        self.pen = QtGui.QPen(QtCore.Qt.black, 1)
        """pen for object paintings"""
        self.pen_changed = True
        """pen need be changed"""
        self._recount_zoom = 1.0
        """pen need be changed"""
        self.x = 0
        """x vew possition"""
        self.y = 0 
        """y viw possition"""
      
    @property
    def rect(self):
        if self._rect is None:
            return QtCore.QRectF(0, 0, 450, 300)
        margin = (self._rect.width()+self._rect.height())/100
        return QtCore.QRectF(
            self._rect.left()-margin, 
            self._rect.top()-margin,
            self._rect.width()+2*margin,
            self._rect.height()+2*margin)
            
    @property
    def zoom(self):
        return self._zoom
        
    @zoom.setter
    def zoom(self, value):
        """zoom property, if zoom is too different, recount pen width"""        
        self._zoom = value
        ratio = self._recount_zoom/value
        if ratio>1.2 or ratio<0.8:
            self.pen_changed = True
            self.pen = QtGui.QPen(QtCore.Qt.black, 1.2/value)
            self._recount_zoom = value
            
        
    def add_point(self, x, y):
        """Try find point or add new. Return found point or new"""
        for point in self.points:
            if x==point.x and y==point.y:
                return point
        point = Point(x, y)
        self.points.append(point)
        if self._rect is None:
            self._rect = QtCore.QRectF(x, y, 0, 0)        
        else:
            if self._rect.left()>x:
                self._rect.setLeft(x)
            if self._rect.right()<x:
                self._rect.setRight(x)
            if self._rect.top()>y:
                self._rect.setTop(y)            
            if self._rect.bottom()<y:
                self._rect.setBottom(y)
        return point
        
    def add_line(self,p, x, y):
        """Add line from point p to [x,y]"""
        p2 = self.add_point(x, y)
        return p2, self.join_line(p, p2)
        
    def add_point_to_line(self, line, x, y):
        """Add point to line and split it """
        xn, yn = self.get_point_on_line(line, x, y)
        p = self.add_point(xn, yn)
        p.lines.append(line)
        line.p2.lines.remove(line)
        l2 = self.join_line(p, line.p2)
        line.p2 = p
        return p, l2
        
    def join_line(self,p1, p2):
        """Add line from point p1 to p2"""
        if p1 == p2:
            return None
        if p1>p2:
            pom = p1
            p1 = p2
            p2 = pom
        for line in p1.lines:
            if line.p2 == p2:
                return line
        line = Line(p1,p2)
        p1.lines.append(line)
        p2.lines.append(line)
        self.lines.append(line)
        return line
        
    def delete_line(self, l):
        """remove set line from lines end points"""
        self.lines.remove(l)
        l.p1.lines.remove(l)
        l.p2.lines.remove(l)
        
    def delete_point(self, p):
        """Try remove set point, and return it 
        if point is in some line return False"""
        if len(p.lines)>0:
            return False
        self.points.remove(p)    
        return True
    
    @staticmethod
    def make_tmp_line(p1x, p1y, p2x, p2y):
        """Make temporrary line"""
        p1 = Point(p1x, p1y)
        p2 = Point(p2x, p2y)
        line = Line(p1,p2)
        p1.lines.append(line)
        p2.lines.append(line)
        return line
        
    @staticmethod
    def get_point_on_line(line, px, py):
        """Compute point on line"""
        dx = line.p2.x-line.p1.x
        dy = line.p2.y-line.p1.y 
        if dx>dy:
            return px, line.p1.y + (px-line.p1.x)*dy/dx
        return line.p1.x + (py-line.p1.y)*dx/dy, py
    
