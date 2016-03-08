from .action_types import ParametrizedActionType, Runner, ActionType

class Flow123dAction(ParametrizedActionType):
    def __init__(self, **kwargs):
        super(Flow123dAction, self).__init__(**kwargs)
        
        self.name = "Flow123d"
        """Display name of action"""
        self.description = "Flow123d"
        """Display description of action"""  
        self.file = None
        """Input Yaml file"""
        self.type = ActionType.complex
            
    def _get_variables_script(self):    
        """return array of variables python scripts"""
        var = super(Flow123dAction, self)._get_variables_script()
        var.append("YAMLFile={0}".Format(self.variables["YAMLFile"]))
        return var
        
    def _get_runner(self, params):    
        """
        return Runner class with process description
        """
        runner = Runner("flow123d", [], self.type)
        return runner
        
    def run(self):    
        """
        Process action on client site or prepare process environment and 
        return Runner class with  process description or None if action not 
        need externall processing.
        """
        
        file = self._parametrise_file()
        return  self._get_runner(file)

    def _check_params(self):    
        """check if all require params is set"""
        err = super(Flow123dAction, self)._check_params()
        if 'YAMLFile' not in self.variables:
            err.append("Flow123d action require YAMLFile parameter")
            
        if len(self.inputs) > 0:
            params =  self.get_require_params(self)
            
            for param in params:
                if not hasattr(self.self.inputs[0],  param) :
                    err.append("Yaml parameter {0} is not set in input")
        return err
        
    def get_require_params(self):
        """Return list of params needed for completation of Yaml file"""
        # ToDo logic
        pass
        
    def _parametrise_file(self):
        """Rename and make completation of Yaml file and return new file path"""
        # ToDo logic
        pass
