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
    def __init__(self, dx=100, dy=150):
        self.dx = dx 
        """x canvas size"""
        self.dy = dy 
        """y canvas size"""
        self.points = []
        """list of points"""
        self.lines = []
        """list of lines"""
        
    def add_point(self, x, y):
        """Try find point or add new. Return found point or new"""
        for point in self.points:
            if x==point.x and y==point.y:
                return point
        point = Point(x, y)
        self.points.append(point)
        return point
        
    def add_line(self,p, x, y):
        """Add line from point p to [x,y]"""
        p2 = self.add_point(x, y)
        return self.join_line(p, p2)
        
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
        
    
