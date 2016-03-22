from .action_types import WrapperActionType, ActionStateType, BaseActionType
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
            is constructed from WrappedAction and placed in Ensemble
        :param Ensemble Input: Composite of WrappedAction cyclic  inputs, 
            this parameter is set after declaration this action by function
           set_wrapped_action 
        """
        self.wa_instances=[]
        """
        Set wrapper class serve only as template, for run is make
        copy of this class. The variable is for the copies.
        """
        self.wa_inputs=[]
        """input for the copy of wrapper class"""        
        super(ForEach, self).__init__(**kwargs)

    def get_output(self, action, number):
        """return output relevant for set action"""
        if number>0:
            return None
        if 'WrappedAction' in self.variables and \
            isinstance(self.variables['WrappedAction'],  BaseActionType):
            if action==self.variables['WrappedAction'] and len(self.inputs)>0:
                # for wraped action return previous input
                return self.get_input_val(number)
            output=self.variables['WrappedAction'].get_output(number)
            if self._is_DTT(output):    
                return None
            res=Ensemble(output)
            if self.state != ActionStateType.finished:
                for instance in self.wa_instances:
                    """Running instance, get input from generator"""
                    res.add_item(instance.get_output(number))
            return res
        return None

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
        err = self._check_params()
        err.extend(self._check_params())
        if 'WrappedAction' in self.variables and \
            isinstance(self.variables['WrappedAction'],  BaseActionType):
            err.extend(self.variables['WrappedAction'].validate())
        return err
