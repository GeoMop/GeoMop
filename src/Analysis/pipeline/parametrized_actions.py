from .action_types import ParametrizedActionType, Runner, ActionType, ActionStateType

class Flow123dAction(ParametrizedActionType):
    
    _name = "Flow123d"
    """Display name of action"""
    _description = "Flow123d"
    """Display description of action"""  

    def __init__(self, **kwargs):
        """
        :param string YAMLFile: path to Yaml file
        :param action or DTT Input: action DTT variable
        :param DTT Output:  output is 
            set accoding params in YAML file
        """

        super(Flow123dAction, self).__init__(**kwargs)
        self.type = ActionType.complex
        self.file_output = self._get_output()
            
    def inicialize(self):
        """inicialize action run variables"""
        if self.state.value > ActionStateType.created.value:
            return
        self.output = self.file_output
        self.state = ActionStateType.initialized    

    def _get_variables_script(self):    
        """return array of variables python scripts"""
        var = super(Flow123dAction, self)._get_variables_script()
        var.append(["YAMLFile='{0}'".format(self.variables["YAMLFile"])])
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
        if self.output is None:
                    err.append("Can't determine output from YAML file")
        return err
        
    def validate(self):    
        """validate variables, input and output"""
        err = super(Flow123dAction, self).validate()
        input_type = self.get_input_val(0)
        if input_type is None:
            err.append("Can't validate input (Output slot of input action is empty)")
        else:
            params =  self.get_require_params(self)
            for param in params:
                if not hasattr(self.inputs[0],  param) :
                    err.append("Yaml parameter {0} is not set in input")              
        return err
        
    def get_require_params(self):
        """Return list of params needed for completation of Yaml file"""
        # ToDo logic
        pass
        
    def _get_output(self):
        """Return DTT output structure from Yaml file"""
        # ToDo logic
        pass
        
    def _parametrise_file(self):
        """Rename and make completation of Yaml file and return new file path"""
        # ToDo logic
        pass
