from ui.helpers import EventLocation, CurrentView

class LocalLabel():
    """
    Class with base history state variables
    """
    def __init__(self, history_id,  label, view):
        self.label = label
        self.view = view
        self.history_id = history_id
        

class GlobalHistory():
    """
    This static class save history of all histories and display view for displaying
    this local histories. For undo is displayed changis in this views
    
    Usage:
    --------
    
    Global history needto know current view. All local hostory call global history, when history
    opperation is done and global history store it. If try functions is call, is check, if history operation is
    make on same view as current. If no is return False, and wait for settings right view. Functions 
    get_undo_view and  get_redo_view get expected view,    
    """
    
    def __init__(self):
        self.histories = []
        """List of local histories"""
        self.labels = []
        """List of local labels"""
        self.undo_labels = []
        """List of local undo labels"""
        self.last_undo_labels = 0
        """Len of steps list during last undo operation"""
        self.last_save_labels = 0
        """Len of steps list during saving undo operation"""
    
    def is_changes(self):
        """Return if changes is made after saving"""
        return self.last_save_labels != len(self.labels)

        
    def saved(self):
        """Save point, where is data saved"""
        self.last_save_labels = len(self.labels)
    
    def add_history(self, history):
        """Add history to histories variable, end return its id"""
        self.histories.append(history)
        return len(self.histories)

    def add_label(self, history_id, label):
        """Add label to global history"""
        self.labels.append(LocalLabel(history_id, label, CurrentView(self.histories[history_id].__location__)))
        pass
        
    def remove_all(self):
        """Releas all histories"""
        for history in self.histories:
            history.global_history = None
            history.release()
        self.histories = []
        self.labels = []
        self.undo_labels = []
        
    def get_undo_view(self):
        """If current view is different from view that is need for next undo opperation
        return it, else return None"""
        if len(self.labels)<1:
            return None
        if not self.labels[-1].view.cmp():
            return self.labels[-1].view 
        return None
        
    def get_redo_view(self):
        """If current view is different from view that is need for next redo opperation
        return it, else return None"""
        if len(self.undo_labels)<1:
            return None
        if not self.undo_labels[-1].view.cmp():
            return self.undo_labels[-1].view 

        return None

    def try_undo_to_label(self):
        """Make all undo opperations, that was done in current view,
        if is label operation done, return True and ops list. If not, new current view 
        is set and return False"""
        id = None
        while len(self.labels)>0:
            if not self.labels[-1].view.cmp():
                # view is changes
                if id is not None:
                    return False, self.histories[id].return_op()
                return False, self.return_op()
            label = self.labels.pop()
            id = label.history_id            
            self.histories[id].undo()
            self.undo_labels.append(label)
            self.last_undo_labels = len(self.steps)
            if label.label is not None:
                # to label
                if id is not None:
                    return True, self.histories[id].return_op()
                return True, self.return_op()
        if id is not None:
            return True, self.histories[id].return_op()
        return True, self.return_op()
        
    def try_redo_to_label(self, count=1):
        """Make all redo opperations, that was done in current view,
        if is label operation done, return True and ops list. If not, new current view 
        is set and return False"""
        if self.last_undo_labels!=len(self.labels):
            # new history step was added after undo operation
            self.undo_labels = []
            for history in self.histories:
                history.undo_steps = []            
            return True, self._return_op( )
        end = False
        while len(self.undo_labels)>0 and \
            (self.undo_labels[-1].label is None or not end):
            # label if is first and all None labels (if first label is not 
            # is none, view was changed)
            end = True
            if not self.undo_labels[-1].view.cmp():
                self.last_undo_labels=len(self.labels)
                if id is not None:
                    return False, self.histories[id].return_op()
                return False, self.return_op()
            label = self.undo_labels.pop()
            id = label.history_id            
            self.histories[id].redo()
            self.labels.append(label)
        self.last_undo_labels=len(self.labels)
        if id is not None:
            return True, self.histories[id].return_op()
        return True, self.return_op()
        
    def return_op(self):
        """Return changes maked after last history operation calling and
        remove old. This changes is for refresh display operation and depends to 
        class implementation."""
        return {"type":None}
    
    
class HistoryStep():
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
        

class History():
    
    def __init__(self,  global_history):
        self.global_history = global_history
        """Link to global history"""
        self.id = self.global_history.add_history(self)
        """Id for global history opperations"""
        self.steps = []
        """history steps"""
        self.undo_steps = []
        """Returned history steps"""
        self.multi = {}
        """Step is small-grained history operation, multi is use for broad 
        structuring of history steps. Milti ids dictionary of step label:id
        """        

    def return_op(self):
        """Return changes maked after last history operation calling and
        remove old. This changes is for refresh display operation and depends to 
        class implementation."""
        return {"type":None}
        
    def undo(self):
        """undo make one undo operation"""
        assert len(self.steps)>0
        step = self.steps.pop()
        revert = step.process()
        if step.label is not None:
            revert.label=step.label
        self.undo_steps.append(revert)
        
    def redo(self):
        """make one redo operation"""
        step = self.undo_steps.pop()
        revert = step.process()
        if step.label is not None:
            revert.label=step.label
        self.steps.append(revert)
        self.last_undo_steps=len(self.steps)
        
    def release(self):
        """Set or lins to none"""
        pass

    
class DiagramHistory(History):
    """
    Diagram history
    
    Basic diagram operation for history purpose
    """

    __location__ = EventLocation.diagram
            
    def __init__(self, diagram,  global_history): 
        super(DiagramHistory, self).__init__(global_history)       
        self._diagram = diagram
        """Diagram object""" 
        self._id = diagram
        """Diagram object"""     
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
        
    def return_op(self):
        """return changes maked after last history operation calling and
        remove old"""
        ret = {"type":"Diagram", "added_points":self._added_points, 
            "removed_points":self._removed_points, "added_points":self._moved_points, 
            "added_lines":self._added_lines, "removed_lines":self._removed_lines}
        self._added_points = []
        self._removed_points = []
        self._moved_points = []
        self._added_lines = []
        self._removed_lines = []    
        return ret
        
    def delete_point(self, id, label=None):
        """
        Add delete point to history operation.
                
        Calling function must ensure, that any line using this poin is not exist .
        Return invert operation
        """
        if label is not None:
            self.global_history.add_label(self._id, label)
        self.steps.append( HistoryStep(self._delete_point, [id],label))
        
    def _delete_point(self, id):
        """
        Delete point from diagram
        
        Return invert operation
        """
        point = self._diagram.get_point_by_id(id)
        assert point is not None
        revert =  HistoryStep(self._add_point, [id, point.x, point.y])
        self._removed_points.append(point)
        self._diagram.delete_point(point, None, True)
        return revert
        

    def add_point(self, id, x,  y, label=None):
        """
        Add add point to history operation.        
        """
        if label is not None:
            self.global_history.add_label(self._id, label)
        self.steps.append( HistoryStep(self._add_point, [id,  x,  y],label))
        
    def _add_point(self, id, x, y):
        """
        Add point to diagram
        
        Return invert operation
        """
        revert =  HistoryStep(self._delete_point, [id])
        point = self._diagram.add_point(x,  y,  None, id, True)
        self._added_points.append(point)
        return revert

    def move_point(self, id, x,  y, label=None):
        """
        Add move point to history operation. 
 
        Return invert operation 
        """
        if label is not None:
            self.global_history.add_label(self._id, label)
        self.steps.append( HistoryStep(self._move_point, [id,  x,  y],label))
        
    def _move_point(self, id,  x,  y):
        """
        Move point in diagram
        
        Return invert operation
        """
        point = self._diagram.get_point_by_id(id)
        assert point is not None
        revert = HistoryStep(self._move_point, [id, point.x, point.y])
        self._diagram.move_point(point, x, y, None, True)
        self._moved_points.append(point)
        return revert
        
    def delete_line(self, id, label=None):
        """
        Add delete line to history operation.
                
        If outer points contain this line, is removed from list.
        Return invert operation
        """
        if label is not None:
            self.global_history.add_label(self._id, label)
        self.steps.append(HistoryStep(self._delete_line, [id],label))
        
    def _delete_line(self, id):
        """
        Delete line from diagram
        """
        line = self._diagram.get_line_by_id(id)
        assert line is not None
        revert =  HistoryStep(self._add_line, [id, line.p1.id, line.p2.id])
        self._removed_lines.append(line)
        self._diagram.delete_line(line, None, True)
        return revert

    def add_line(self, id, p1_id, p2_id, label=None):
        """
        Add add line to history operation. 
 
        Calling function must ensure, that both points exist.
        Return invert operation 
        """
        if label is not None:
            self.global_history.add_label(self._id, label)
        self.steps.append(HistoryStep(self._add_line, [id, p1_id, p2_id],label))
        
    def _add_line(self, id, p1_id, p2_id):
        """
        Add line to diagram
        
        Return invert operation
        """
        p1 = self._diagram.get_point_by_id(p1_id)
        assert p1 is not None
        p2 = self._diagram.get_point_by_id(p2_id)
        assert p2 is not None
        
        revert =  HistoryStep(self._delete_line, [id])
        line = self._diagram.join_line(p1, p2, None, id, True)
        self._added_lines.append(line)
        return revert
        
    def release(self):
        """Set or lins to none"""
        self._added_points = []
        self._removed_points = []
        self._moved_points = []
        self._added_lines = []
        self._removed_lines = []
        self._diagram = None
