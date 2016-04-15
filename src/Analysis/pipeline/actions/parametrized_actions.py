from .action_types import ParametrizedActionType

class Flow123dAction(ParametrizedActionType):
        def __init__(self, **kwargs):
            super(Flow123dAction, self).__init__(**kwargs)
            
        def _check_params(self):    
            """check if all require params is set"""
            err = []
            if len(self.inputs)>0:
                err.append("Parametrized action require exactly one input parameter")
            if len(self.outputs)>0:
                err.append("Parametrized action require exactly one output parameter")
            return err
