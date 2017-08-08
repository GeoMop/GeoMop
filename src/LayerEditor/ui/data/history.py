from enum import IntEnum

class EventLocation(IntEnum):
    """Location where event happen"""
    diagram = 0
    layer = 1

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
    
    def __init__(self, cfg):
        self.cfg = cfg
        """dara structures"""
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
        self.removed_diagrams = []
        """Diagram that is removed from history"""
    
    def is_changes(self):
        """Return if changes is made after saving"""
        return self.last_save_labels != len(self.labels)
        
    def saved(self):
        """Save point, where is data saved"""
        self.last_save_labels = len(self.labels)
    
    def add_history(self, history):
        """Add history to histories variable, end return its id"""
        self.histories.append(history)
        return len(self.histories)-1

    def add_label(self, history_id, label):
        """Add label to global history"""
        self.labels.append(LocalLabel(history_id, label, 
            self.cfg.get_current_view(self.histories[history_id].__location__)))
        
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
        if not self.labels[-1].view.is_compatible():
            return self.labels[-1].view 
        return None
        
    def get_redo_view(self):
        """If current view is different from view that is need for next redo opperation
        return it, else return None"""
        if len(self.undo_labels)<1:
            return None
        if not self.undo_labels[-1].view.is_compatible():
            return self.undo_labels[-1].view 

        return None

    def try_undo_to_label(self):
        """Make all undo opperations, that was done in current view,
        if is label operation done, return True and ops list. If not, new current view 
        is set and return False"""
        id = None
        while len(self.labels)>0:
            if not self.labels[-1].view.cmp(
                self.histories[self.labels[-1].history_id].__location__):
                # view is changes
                if id is not None:
                    return False, self.histories[id].return_op()
                return False, self.return_op()
            label = self.labels.pop()
            id = label.history_id            
            self.histories[id].undo()
            self.undo_labels.append(label)
            self.last_undo_labels = len(self.labels)
            if label.label is not None:
                # to label
                if id is not None:
                    return True, self.histories[id].return_op()
                return True, self.return_op()
        if id is not None:
            return True, self.histories[id].return_op()
        return True, self.return_op()
        
    def try_redo_to_label(self):
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
        id = None
        while len(self.undo_labels)>0 and \
            (self.undo_labels[-1].label is None or not end):
            # label if is first and all None labels (if first label is not 
            # is none, view was changed)
            end = True
            if not self.undo_labels[-1].view.cmp(
                self.histories[self.undo_labels[-1].history_id].__location__):
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
            "removed_points":self._removed_points, "moved_points":self._moved_points, 
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
        self.global_history.add_label(self.id, label)
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
        self.global_history.add_label(self.id, label)
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
        self.global_history.add_label(self.id, label)
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
        self.global_history.add_label(self.id, label)
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
        self.global_history.add_label(self.id, label)
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
        
class LayersHistory(History):
    """
    Layer history
    
    Basic layer operation for history purpose
    """

    __location__ = EventLocation.layer
            
    def __init__(self, layer,  global_history): 
        super(LayersHistory, self).__init__(global_history)       
        self._layer = layer
        """Layer panel object""" 
        self._refresh_panel = True
        """Refresh layer panel"""
        self._check_viewed = False
        """Check interfaces set as viewed for existance"""
        self._edit_first = False
        """Edit first interface"""
        
    def insert_layer(self, layer, id, label=None):
        """
        Add insert layer to history operation. 
 
        Calling function must ensure that interface sequence related
        to new layer
        """
        self.global_history.add_label(self.id, label)
        self.steps.append(HistoryStep(self._insert_layer, [layer, id],label))
        
    def _insert_layer(self, layer, id):
        """
        Insert layer to layers
        
        Return invert operation
        """
        layers = self.global_history.cfg.layers
        layers.insert_layer(layer, id)
        
        revert =  HistoryStep(self._delete_layer, [id])
        self._refresh_panel = True
        return revert

    def delete_layer(self, id, label=None):
        """
        Add delete layer to history operation. 
 
        Calling function must ensure that interface sequence related
        to rest layers
        """
        self.global_history.add_label(self.id, label)
        self.steps.append(HistoryStep(self._delete_layer, [id],label))
        
    def _delete_layer(self, id):
        """
        Delete layer from layers
        
        Return invert operation
        """
        layers = self.global_history.cfg.layers
        del_layer = layers.delete_layer(id)
        
        revert =  HistoryStep(self._insert_layer, [del_layer, id])
        self._refresh_panel = True
        self._check_viewed = True
        return revert
        
    def change_layer(self, layer, id, label=None):
        """
        Add change layer to history operation. 
 
        Calling function must ensure that interface sequence related
        to rest layers
        """
        self.global_history.add_label(self.id, label)
        self.steps.append(HistoryStep(self._change_layer, [id, layer],label))
        
    def _change_layer(self, layer, id):
        """
        Switch layer id to set layer in layers
        
        Return invert operation
        """
        layers = self.global_history.cfg.layers
        old_layer = layers.change_layer(id, layer)
        
        revert =  HistoryStep(self._change_layer, [id, old_layer])
        self._refresh_panel = True
        self._check_viewed = True
        return revert

        
    def insert_interface(self, interface, label=None):
        """
        Add insert layer to history operation. 
 
        Calling function must ensure that diagram sequence related
        to new interface
        """
        self.global_history.add_label(self.id, label)
        self.steps.append(HistoryStep(self._insert_interface, [interface, id],label))
        
    def _insert_interface(self, interface, id):
        """
        Insert interface to layers
        
        Return invert operation
        """
        layers = self.global_history.cfg.layers
        layers.insert_interface(interface, id)
        
        revert =  HistoryStep(self._delete_interface, [id])
        self._refresh_panel = True        
        return revert

    def delete_interface(self, id, label=None):
        """
        Add delete layer to history operation. 
 
        Calling function must ensure that diagram sequence related
        to rest interfaces
        """
        self.global_history.add_label(self.id, label)
        self.steps.append(HistoryStep(self._delete_interface, [id],label))
        
    def _delete_interface(self, id):
        """
        Delete layer from layers
        
        Return invert operation
        """
        layers = self.global_history.cfg.layers
        del_interface = layers.delete_interface(id)
        layers.strip_edited(del_interface)
        
        revert =  HistoryStep(self._insert_interface, [del_interface, id])
        self._refresh_panel = True
        self._check_viewed = True
        
        return revert

    def change_interface(self, interface, id, label=None):
        """
        Add change layer to history operation. 
 
        Calling function must ensure that diagram sequence related
        to new interfaces
        """
        self.global_history.add_label(self.id, label)
        self.steps.append(HistoryStep(self._change_interface, [id],label))
        
    def _change_interface(self, id):
        """
        Switch id layer to set layers
        
        Return invert operation
        """
        layers = self.global_history.cfg.layers
        old_interface = layers.change_interface(id)
        layers.strip_edited(old_interface)
        
        revert =  HistoryStep(self._change_interface, [old_interface, id])
        self._refresh_panel = True
        self._check_viewed = True
        
        return revert
        
    def change_group(self, layers, interfaces, id, old_count, label=None):
        """
        Add switching two groups to history  
        
        Calling function must ensure that diagram sequence related
        to new group.
        """
        self.global_history.add_label(self.id, label)
        self.steps.append(HistoryStep(self._change_group, [layers, interfaces, id, old_count],label))
 
    def _change_group(self, new_layers, new_interfaces, id, old_count):
        """
        Switch id layer to set layers
        
        Return invert operation
        """
        layers = self.global_history.cfg.layers
        old_layers, old_interfaces = layers.change_interface(id)
        for interface in old_interfaces:
            layers.strip_edited(interface)
            
        revert =  HistoryStep(self._change_group, [old_layers, old_interfaces, id, len(new_layers)])
        self._refresh_panel = True
        self._check_viewed = True
        
        return revert 

    def delete_diagrams(self, id, count, oper, label=None):
        """
        Add diagram deleting to history  
        
        Calling function must ensure that interface sequence related
        to rest diagrams.
        """
        self.global_history.add_label(self.id, label)
        self.steps.append(HistoryStep(self._delete_diagrams, [id, count, oper],label))
 
    def _delete_diagrams(self, id, count, oper):
        """
        Switch id layer to set layers
        
        Return invert operation
        """
        cfg = self.global_history
        for i in range(0, count):
            if cfg.remove_and_save_diagram(id):
                self._edit_first = True
        diagrams = self.global_history.removed_diagrams
        self.global_history.removed_diagrams = []
        
        revert =  HistoryStep(self._insert_diagrams, [diagrams, id, count, oper])
        
        return revert 

    def insert_diagrams(self, id, oper, label=None):
        """
        Add diagram inserting to history  
        
        Calling function must ensure that interface sequence related
        to inserted diagrams.
        """
        self.global_history.add_label(self.id, label)
        
        diagrams = self.global_history.removed_diagrams
        self.global_history.removed_diagrams = []
        
        self.steps.append(HistoryStep(self._insert_diagrams, [diagrams, id, oper], label))
 
    def _insert_diagrams(self, diagrams, id, oper):
        """
        Switch id layer to set layers
        
        Return invert operation
        """
        cfg = self.global_history
        cfg.insert_diagrams(diagrams, id, oper)
        
        revert =  HistoryStep(self._delete_diagrams, [id, len(diagrams), oper])
        
        return revert 

    def return_op(self):
        """return nedded check """
        ret = {"type":"Layers", "refresh_panel":self._refresh_panel, 
            "check_viewed":self._check_viewed, "edit_first":self._edit_first}
        self._refresh_panel = False
        self._check_viewed = False
        self._edit_first = False
        return ret
        



