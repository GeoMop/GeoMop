import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui

__next_id__ = 1

class Point():
    """
    Class for graphic presentation of point
    """
    def __init__(self, x, y, id=None):
        global __next_id__
        self.x = x 
        """x coordinate"""
        self.y = y 
        """y coordinate"""
        self.lines = []
        """This point instance is use for these lines"""
        self.object = None
        """Graphic object""" 
        self.id = id
        """Line history id"""
        if id is None:            
            self.id = __next_id__
            __next_id__ += 1
            
    def qpointf(self):
        """return QPointF coordinates"""
        return QtCore.QPointF(self.x, self.y)
        
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
    def __init__(self, p1, p2, id=None):
        global __next_id__
        self.p1 = p1
        """First point"""
        self.p2 = p2
        """Second point"""
        self.object = None
        """Graphic object"""
        self.id = id
        """Line history id"""
        if id is None:            
            self.id = __next_id__
            __next_id__ += 1
            
    def qrectf(self):
        """return QRectF coordinates"""
        return QtCore.QRectF(self.p1, self.p2)

class Diagram():
    """
    Layer diagram
    
    Use only class functions for adding new shapes. This function ensure folloving 
    requirements. New class function must ensure this requirements too.
    requirements:
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
        self._history = History(self)
        """history"""
      
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
    
    def get_point_by_id(self, id):
        """return point or None if not exist"""
        for point in self.points:
            if point.id==id:
                return point
        return None

    def get_line_by_id(self, id):
        """return line or None if not exist"""
        for line in self.lines:
            if line.id==id:
                return line
        return None

    def recount_canvas(self):
        """recount canvas size"""
        self._rect = None
        for p in self.points:
            if self._rect is None:
                self._rect = QtCore.QRectF(p.x, p.y, 0, 0)   
            else:
                if self._rect.left()>p.x:
                    self._rect.setLeft(p.x)
                if self._rect.right()<p.x:
                    self._rect.setRight(p.x)
                if self._rect.top()>p.y:
                    self._rect.setTop(p.y)            
                if self._rect.bottom()<p.y:
                    self._rect.setBottom(p.y)
        
    def add_point(self, x, y, label='Add point', id=None, not_history=False):
        """Add point to canvas"""
        point = Point(x, y, id)
        self.points.append(point)
        #save revert operations to history
        if not not_history:
            self._history.delete_point(point.id, label)
        # recount canvas size
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
    
    def move_point(self, p, x, y, label='Move point', not_history=False):
        """Add point to canvas"""
        #save revert operations to history
        if not not_history:
            self._history.move_point(p.id, p.x, p.y, label)
        # compute recount params
        need_recount = False
        small = (self._rect.width()+self._rect.height())/1000000
        trimed = self._rect - QtCore.QMarginsF(small, small, small, small)
        if (not trimed.contains(p.qpointf())) or \
            (not self._rect.contains(QtCore.QPointF(x, y))):
            need_recount = True
        # move point
        p.x = x
        p.y = y        
        # recount canvas size
        if need_recount:
            self.recount_canvas()
            
    def delete_point(self, p, label='Delete point', not_history=False):
        assert len(p.lines)==0
        #save revert operations to history
        if not not_history:
            self._history.add_point(p.id, p.x, p.y, label)
        # compute recount params
        need_recount = False
        small = (self._rect.width()+self._rect.height())/1000000
        trimed = self._rect - QtCore.QMarginsF(small, small, small, small)
        if not trimed.contains(p.qpointf()) :
            need_recount = True
        # remove point
        self.points.remove(p)
        # recount canvas size
        if need_recount:
            self.recount_canvas()

    def join_line(self,p1, p2, label=None, id=None, not_history=False):
        """Add line from point p1 to p2"""
        assert p1 != p2
        if p1>p2:
            pom = p1
            p1 = p2
            p2 = pom
        for line in p1.lines:
            if line.p2 == p2:
                return line
        line = Line(p1,p2, id)
        p1.lines.append(line)
        p2.lines.append(line)
        self.lines.append(line)
        #save revert operations to history
        if not not_history:
            self._history.delete_line(line.id, label)
        return line
        
    def delete_line(self, l, label="Delete line", not_history=False):
        """remove set line from lines end points"""
        self.lines.remove(l)
        l.p1.lines.remove(l)
        l.p2.lines.remove(l)
        #save revert operations to history
        if not not_history:
            self._history.add_line(l.id, l.p1.id, l.p2.id, label)
    
    def move_point_after(self, p, x_old, y_old, label='Move point'):
        """Call if point is moved by another way and need save history"""
        #save revert operations to history
        self._history.move_point(p.id, x_old, y_old)
        # compute recount params
        small = (self._rect.width()+self._rect.height())/1000000
        trimed = self._rect - QtCore.QMarginsF(small, small, small, small)
        if (not trimed.contains(QtCore.QPointF(x_old, y_old))) or \
            (not self._rect.contains(p.qpointf())):
            self.recount_canvas()
        
    def add_line(self,p, x, y, label='Add line', no_history=False):
        """Add line from point p to [x,y]"""
        p2 = self.add_point(x, y, label, None, no_history)
        return p2, self.join_line(p, p2, None, None, no_history)
        
    def add_new_point_to_line(self, line, x, y, label='Add new point to line'):
        """Add new point to line and split it """
        xn, yn = self.get_point_on_line(line, x, y)
        p = self.add_point(xn, yn, label)
        p.lines.append(line)
        line.p2.lines.remove(line)
        point2 = line.p2
        line.p2 = p
        l2 = self.join_line(point2, line.p2, None)
        #save revert operations to history        
        self._history.add_line(line.id, line.p1, point2, None)
        self._history.delete_line(line.id, None)        
        return p, l2
        
    def add_point_to_line(self, line, point, label='Add point to line'):
        """
        Add point to line and split it. Return new line and array of lines that should be removed.
        This lines is released from data, but object is existed, and should be relesed after discarding
        graphic object.
        """
        releasing_lines = []
        xn, yn = self.get_point_on_line(line, point.x, point.y)
        self.move_point(point, xn, yn, label)
        point.lines.append(line)
        line.p2.lines.remove(line)
        point2 = line.p2
        line.p2 = point
        l2 = self.join_line(point, point2)        
        #save revert operations to history
        self._history.add_line(line.id, line.p1.id, point2.id, None)
        self._history.delete_line(line.id, None)
        # TODO: case if one line is merged (line between new point and one of line point)
        # TODO: case if two lines is merged (triangle) 
        

        return l2, releasing_lines
        
    def merge_point(self, point, atached_point, label='Merge Points'):
        """
        Merge rwo points. Atached_point will be remove from data
        and shoud be released after discarding graphic object.
        Return array of lines that should be removed. This lines is 
        released from data, but object is existed, and should be relesed 
        after discarding graphic object.
        """
        releasing_lines = []
        # move all lines from atached_point to point
        for line in atached_point.lines:
            if line in point.lines:
                # line between point and atached_point
                assert (line.p1== point and line.p2 == atached_point) or \
                    (line.p2 == point and line.p1 == atached_point)
                releasing_lines.append(line)
                self.delete_line(line, label)
                label = None
                continue
            p = None            
            if line.p1== atached_point:
                p = line.p1
            else:
                assert line.p2== atached_point
                p = line.p2
            for mline in point.lines:
                if (mline.p1== p) or (mline.p2==p):
                    # exist two lines between: p - atached_point and 
                    # the p - point ₌> merge this lines
                    releasing_lines.append(line)
                    self.delete_line(line, label)
                    label = None
                    p=None
                    break
            if p is not None:
                # move line from atached_point to point
                objekt = line.object
                id = line.id
                self.delete_line(line, label)
                label = None
                if p == line.p1:
                    line.p1 = point
                else:
                    line.p2 = point
                line = self.join_line(line.p1, line.p2, label, id)
                line.object = objekt                
        # remove point 
        self.delete_point(atached_point, label)
        return releasing_lines
        
    def try_delete_point(self, p, label="Delete point"):
        """Try remove set point, and return it 
        if point is in some line return False"""
        if len(p.lines)>0:
            return False
        self.delete_point(p, label)
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
        
    def undo_to_label(self, label=None):
        """undo to set label, if label is None, undo to previous operation, 
        that has not None label"""
        return  self._history.undo_to_label(label)
        
    def redo_to_label(self, label=None):
        """redo to set label, if label is None, redo to next operation, 
        that has not None label"""
        return  self._history.redo_to_label(label)
        
class History():
    """
    Diagram history
    
    Basic diagram operation for history purpose
    """
    class Step():
        def __init__(self, operation, params=[], label=None):
            """
            add new step
            :param func operation: history function for restore step
            :param tuple params: tuple of arguments for history restoring function
            :param str label: Label name that is show in history
            """
            self._operation = operation
            self._params = params
            self.label = label
            
        def process(self):
            """process history step restoring"""
            if self._operation is not None:
                return self._operation(*self._params)
            return None
            
    def __init__(self, diagram):       
        self._diagram = diagram
        """Diagram object"""
        self.steps = []
        """history steps"""
        self.undo_steps = []
        """Returned history steps"""
        self.last_undo_steps = 0
        """Len of steps list during last undo operation"""
        self.multi = {}
        """Step is small-grained history operation, multi is use for broad 
        structuring of history steps. Milti ids dictionary of step label:id
        """
        self._added_points = []
        """added points after last history operation calling"""
        self._removed_points = []
        """removed points after last history operation calling"""
        self._moved_points = []
        """moved points after last history operation calling"""
        self._added_lines = []
        """added lines after last history operation calling"""
        self._removed_lines = []
        """removed lines after last history operation calling"""
       
    def _return_op(self):
        """return changes maked after last history operation calling and
        remove old"""
        ret = (self._added_points, self._removed_points, self._moved_points, 
            self._added_lines, self._removed_lines)
        self._added_points = []
        self._removed_points = []
        self._moved_points = []
        self._added_lines = []
        self._removed_lines = []    
        return ret
        
    def undo_to_label(self, label=None):
        """undo to set label, if label is None, undo to previous operation, 
        that has not None label"""
        while True:
            if len(self.steps)==0:
                break
            step = self.steps.pop()
            revert = step.process()
            if step.label is not None:
                revert.label=step.label
            self.undo_steps.append(revert)
            if step.label is not None and (label is None or label==step.label):
                self.last_undo_steps=len(self.steps)
                break
        return  self._return_op( )
        
    def redo_to_label(self, label=None):
        """redo to set label, if label is None, redo to next operation, 
        that has not None label"""
        if self.last_undo_steps!=len(self.steps):
            self.undo_steps = []
            return
        end = False
        while len(self.undo_steps)>0 and \
            (self.undo_steps[-1].label is None or not end):
            # finish if not undo steps or end is set to True and next step has label
            step = self.undo_steps.pop()
            revert = step.process()
            if step.label is not None:
                revert.label=step.label
            self.steps.append(revert)
            if step.label is not None and (label is None or label==step.label):
                end = True
        self.last_undo_steps=len(self.steps)
        return  self._return_op( )
        
    def add_multi(self, label):
        """Add new name of multi operation after last operation"""
        self.multi[label] = len(self.steps)
        
    def undo_to_multi(self, label=None):
        """undo to set multi label"""
        return  self._return_op( )
        
    def redo_to_multi(self, label=None):
        """redo to set multi label"""
        return  self._return_op( )
        
    def delete_point(self, id, label=None):
        """
        Add delete point to history operation.
                
        Calling function must ensure, that any line using this poin is not exist .
        Return invert operation
        """
        self.steps.append(self.Step(self._delete_point, [id],label))
        
    def _delete_point(self, id):
        """
        Delete point from diagram
        
        Return invert operation
        """
        point = self._diagram.get_point_by_id(id)
        assert point is not None
        revert = self.Step(self._add_point, [id, point.x, point.y])
        self._removed_points.append(point)
        self._diagram.delete_point(point, None, True)
        return revert
        

    def add_point(self, id, x,  y, label=None):
        """
        Add add point to history operation.        
        """
        self.steps.append(self.Step(self._add_point, [id,  x,  y],label))
        
    def _add_point(self, id, x, y):
        """
        Add point to diagram
        
        Return invert operation
        """
        revert = self.Step(self._delete_point, [id])
        point = self._diagram.add_point(x,  y,  None, id, True)
        self._added_points.append(point)
        return revert

    def move_point(self, id, x,  y, label=None):
        """
        Add move point to history operation. 
 
        Return invert operation 
        """
        self.steps.append(self.Step(self._move_point, [id,  x,  y],label))
        
    def _move_point(self, id,  x,  y):
        """
        Move point in diagram
        
        Return invert operation
        """
        point = self._diagram.get_point_by_id(id)
        assert point is not None
        revert = self.Step(self._move_point, [id, point.x, point.y])
        self._diagram.move_point(point, x, y, None, True)
        self._moved_points.append(point)
        return revert
        
    def delete_line(self, id, label=None):
        """
        Add delete line to history operation.
                
        If outer points contain this line, is removed from list.
        Return invert operation
        """
        self.steps.append(self.Step(self._delete_line, [id],label))
        
    def _delete_line(self, id):
        """
        Delete line from diagram
        """
        line = self._diagram.get_line_by_id(id)
        assert line is not None
        revert = self.Step(self._add_line, [id, line.p1.id, line.p2.id])
        self._removed_lines.append(line)
        self._diagram.delete_line(line, None, True)
        return revert

    def add_line(self, id, p1_id, p2_id, label=None):
        """
        Add add line to history operation. 
 
        Calling function must ensure, that both points exist.
        Return invert operation 
        """
        self.steps.append(self.Step(self._add_line, [id, p1_id, p2_id],label))
        
    def _add_line(self, id, p1_id, p2_id):
        """
        Add line to diagram
        
        Return invert operation
        """
        p1 = self._diagram.get_point_by_id(p1_id)
        assert p1 is not None
        p2 = self._diagram.get_point_by_id(p2_id)
        assert p2 is not None
        
        revert = self.Step(self._delete_line, [id])
        line = self._diagram.join_line(p1, p2, None, id, True)
        self._added_lines.append(line)
        return revert
    
