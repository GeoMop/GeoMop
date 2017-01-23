from .action_def import  ACTION_TYPES
import PyQt5.QtCore as QtCore

class Node():
    """
    Class for graphic presentation of task
    """
    def __init__(self, action_def, pos):
        self._action_def = action_def 
        """possition of type action defination in ACTION_TYPES"""
        self.action = None
        """action from last validation"""
        self.parameters = []
        """string value of parameters in order as in action defination"""        
        in_ports = 1
        if ACTION_TYPES[self._action_def].max_inputs==0:
            self.in_ports = 0
        self.pos = pos
        """node absolute possition"""
        self.in_ports_pos = []
        if in_ports==1:
            self.in_ports_pos.append(QtCore.QPointF(0, 0))
        """input ports absolute possition"""
        self.out_port_pos = QtCore.QPointF(0, 0)
        """otput port absolute possition"""
        self.repaint_conn = False
        """If is set to True, related connections need repaint"""
        self.repaint = False
        """If is set to True, node need repaint"""
        self.unique = 0
        """Parameter for unique name of action"""

    @property
    def action_def(self):
        """Return real action definition"""
        return ACTION_TYPES[self._action_def]
        
    @property
    def unique_name(self):
        """Return unique action name"""
        if self.unique==0:
            return self.action_def.name
        return self.action_def.name + " (" + str(self.unique) + ")"

class Connection():
    """
    Class for graphic presentation of task
    """
    def __init__(self, input, output):
        self.input = input
        """node from which connection come out"""
        self.output = output
        """node to which connection enter"""
        self.output_no = 0
        """Number of input node, to wicht connection enter"""
        self.repaint = False
        """If is set to True, connection need repaint"""
        
    def get_in_pos(self):
        """Get input absolute possition"""
        return self.input.out_port_pos
        
    def get_out_pos(self):
        """Get output absolute possition"""
        return self.output.in_ports_pos[self.output_no]
        
    def is_conn_point(self, node, pos):
        """Has connection end point on set possition (tolerance 2 point)"""
        if node==self.input:
            rect = QtCore.QRectF( 
                self.input.out_port_pos.x()-2, 
                self.input.out_port_pos.y()-2, 
                5, 5)
            if rect.contains(pos):
                return True
        if node==self.output and len(self.output.in_ports_pos)>self.output_no:
            rect = QtCore.QRectF( 
                self.input.in_ports_pos[self.output_no].x()-2, 
                self.input.in_ports_pos[self.output_no].y()-2, 
                5, 5)
            if rect.contains(pos):
                return True    
        return False
