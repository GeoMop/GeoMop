from .action_types import ParametrizedActionType

class Flow123dAction(ParametrizedActionType):
    def __init__(self, **kwargs):
        super(Flow123dAction, self).__init__(**kwargs)
          
        self.file = None
        """Input Yaml file"""
        for name, value in kwargs.items():
            if name == 'YAMLFile':
                self.file = value
            
        def _check_params(self):    
            """check if all require params is set"""
            err = super(Flow123dAction, self)._check_params()
            if self.file is None:
                err.append("Flow123d action require file parameter")
            params =  get_require_params(self)
            for param in params:
                if param not in self.variables:
                    err.append("Yaml parameter {0} is not set in input")
            return err
            
        def get_require_params(self):
            """Return list of params needed for completation of Yaml file"""
            # ToDo logic
            pass
