from .action_types import ParametrizedActionType, Runner, ActionType, BaseActionType, ActionStateType
from .data_types_tree import CompositeDTT

class Flow123dAction(ParametrizedActionType):
    
    _name = "Flow123d"
    """Display name of action"""
    _description = "Flow123d"
    """Display description of action"""  

    def __init__(self, **kwargs):
        """
        :param string YAMLFile: path to Yaml file
        :param action or DTT Input: action DTT variable
        :param DTT Output: DTT variable if variable is set
            output is reduce to this variable (variable is check with
            params in YAML file), if variable is not set, output is 
            set accoding params in YAML file
        """

        super(Flow123dAction, self).__init__(**kwargs)
        self.type = ActionType.complex
        self.file_output = self._get_output()
        
            
    def inicialize(self):
        """inicialize action run variables"""
        if self.state.value > ActionStateType.created.value:
            return
        if len(self.outputs)==0:
            self.outputs.append(self.file_output)
        self.state = ActionStateType.initialized    

    def get_output(self, number):
        """return output relevant for set action"""
        if number>0:
            return None
        return self.outputs[0]

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
        if len(self.outputs)==0:
                    err.append("Can't determine output from YAML file")
        return err
        
    def validate(self):    
        """validate variables, input and output"""
        err = super(Flow123dAction, self).validate()
        if len(self.outputs)>0:
            if not self.outputs[0].match_type(self.file_output):
                err.append("Output type validation fails")
        if isinstance(input[0], BaseActionType) and \
            len(self.inputs)>0:
            input_type = self.inputs[0]. get_output(self)
            if input_type is None:
                err.append("Can't validate input (Output slot of input action is empty)")
            else:
                params =  self.get_require_params(self)
                for param in params:
                    if not hasattr(self.inputs[0],  param) :
                        err.append("Yaml parameter {0} is not set in input")                
        else:
            if len(self.inputs)>0 and isinstance(input[0], CompositeDTT):
                if not input[0].is_set():
                    err.append("Input data can't be empty DTT")
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
        
    
