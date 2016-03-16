from .action_types import WrapperActionType
from .data_types_tree import Ensemble

class ForEach(WrapperActionType):
    
    _name = "ForEach"
    """Display name of action"""
    _description = "Cyclic action processor"
    """Display description of action"""  

    def __init__(self, **kwargs):
        """
       Class for cyclic action processing.      
        :param BaseActionType WrappedAction: Wrapped action
        :param Ensemble Output: This variable is ignore,  outputs
             is construct WrappedAction placed in Ensemble
        :param Ensemble Input: Composite of WrappedAction cyclic  inputs
        """
        super(ForEach, self).__init__(**kwargs)
        self.output = self._get_output_from_wa()

    def _get_output_from_wa(self):
        res = None
        if self.output is None and \
            'WrappedAction' in self.variables and \
            len(self.variables['WrappedAction'])>0:            
            res = Ensemble(self.variables['WrappedAction'])
        return res

    def _get_runner(self, params):    
        """
        return Runner class with process description
        """        
        return None
        
    def run(self):    
        """
        Process action on client site or prepare process environment and 
        return Runner class with  process description or None if action not 
        need externall processing.
        """
        return  self._get_runner(None)        

    def _check_params(self):    
        """check if all require params is set"""
        err = super(ForEach, self)._check_params()
        return err
        
    def validate(self):    
        """validate variables, input and output"""
        # ToDo logic
        err = self._check_params()
        return err
