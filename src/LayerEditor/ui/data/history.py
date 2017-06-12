class LocalLabel():
    """
    Class with base history state variables
    """
    def __init__(self, label, view, history_id):
        self.label = label
        self.view = view
        self.history_id = history_id
        

class GlobalHistory():
    """This static class save history of all histories and display view for displaying
    this local histories. For undo is displayed changis in this views"""
    def __init__(self):
        self.histories = []
        """List of local histories"""
        self.labels = []
        """List of local labels"""
        self.undo_labels = []
        """List of local undo labels"""
        self.current_view
        """Currently set view"""
    
    def add_history(self, history):
        """Add history to histories variable, end return its id"""
        self.histories.append(history)
        return len(self.histories)
        
    def remove_all(self):
        """Releas all histories"""
        for history in self.histories:
            history.release()
        self.histories = []
        self.labels = []
        self.undo_labels = []
        
    def get_undo_view(self):
        """Get view that is need for next undo opperation"""
        pass
        
    def get_redo_view(self):
        """Get view that is need for next redo opperation"""
        pass
        
    def try_undo_to_label(self, label=None):
        """Make all undo opperations, that was done in current view,
        if is label operation done, return True and ops list. If not, new current view 
        is set and return False"""
        return  False, self._return_op( )
        
    def try_redo_to_label(self, label=None):
        """Make all redo opperations, that was done in current view,
        if is label operation done, return True and ops list. If not, new current view 
        is set and return False"""
        return  False, self._return_op( )
    
    
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

    def _return_op(self):
        """Return changes maked after last history operation calling and
        remove old. This changes is for refresh display operation and depends to 
        class implementation."""
        ret = (None)
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
        
    def release(self):
        """Set or lins to none"""
        pass

    
class DiagramHistory(History):
    """
    Diagram history
    
    Basic diagram operation for history purpose
    """
            
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
        
    def delete_point(self, id, label=None):
        """
        Add delete point to history operation.
                
        Calling function must ensure, that any line using this poin is not exist .
        Return invert operation
        """
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
    
