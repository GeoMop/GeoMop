from .action_types import ParametrizedActionType, Runner, ActionType, ActionStateType, ActionRunningState
from .data_types_tree import Struct

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
        self._type = ActionType.complex
        self._file_output = self.__file_output()
            
    def _inicialize(self):
        """inicialize action run variables"""
        if self._state.value > ActionStateType.created.value:
            return
        self._output = self.__file_output
        self._state = ActionStateType.initialized    

    def _get_variables_script(self):    
        """return array of variables python scripts"""
        var = super(Flow123dAction, self)._get_variables_script()
        var.append(["YAMLFile='{0}'".format(self._variables["YAMLFile"])])
        return var

    def _get_runner(self, params):    
        """
        return Runner class with process description
        """
        runner = Runner(self)
        runner.name = self._get_instance_name()
        runner.command = "flow123d"
        return runner
        
    def _run(self):    
        """
        Process action on client site or prepare process environment and 
        return Runner class with  process description or None if action not 
        need externall processing.
        """
        if self._state == ActionStateType.processed:
            return ActionRunningState.wait,  None
        if self._state == ActionStateType.finished:
            return ActionRunningState.finished,  None
        self._state = ActionStateType.processed
        file = self.__parametrise_file()
        return  ActionRunningState.wait,  self._get_runner(file)
        
    def _after_run(self):    
        """
        Set real output variable and set finished state.
        """
        # ToDo read output from files
        self._state = ActionStateType.finished

    def _check_params(self):    
        """check if all require params is set"""
        err = super(Flow123dAction, self)._check_params()
        if 'YAMLFile' not in self._variables:
            err.append("Flow123d action require YAMLFile parameter")
        if self._output is None:
                    err.append("Can't determine output from YAML file")
        return err
        
    def validate(self):    
        """validate variables, input and output"""
        err = super(Flow123dAction, self).validate()
        input_type = self.get_input_val(0)
        if input_type is None:
            err.append("Can't validate input (Output slot of input action is empty)")
        else:
            if not isinstance(input_type, Struct):
                err.append("Flow123d input parameter must return Struct") 
            params =  self.get_require_params()
            for param in params:
                if not hasattr(self._inputs[0],  param) :
                    err.append("Yaml parameter {0} is not set in input")              
        return err
        
    def get_require_params(self):
        """Return list of params needed for completation of Yaml file"""
        # ToDo logic
        return []
        
    def __file_output(self):
        """Return DTT output structure from Yaml file"""
        # ToDo logic
        pass
        
    def __parametrise_file(self):
        """Rename and make completation of Yaml file and return new file path"""
        # ToDo logic
        pass
