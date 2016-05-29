from .action_types import ParametrizedActionType, Runner, QueueType,  ActionStateType
from .data_types_tree import Struct, String

class Flow123dAction(ParametrizedActionType):
    
    name = "Flow123d"
    """Display name of action"""
    description = "Flow123d"
    """Display description of action"""  

    def __init__(self, **kwargs):
        """
        :param string YAMLFile: path to Yaml file
        :param action or DTT Input: action DTT variable
        """
        super(Flow123dAction, self).__init__(**kwargs)
        self._logical_queue = QueueType.external
        self._file_output = self.__file_output()
            
    def _inicialize(self):
        """inicialize action run variables"""
        if self._get_state().value > ActionStateType.created.value:
            return
        self._output = self.__file_output()
        self._set_state(ActionStateType.initialized)
        self._process_base_hash()
        # TODO add file hash

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
        runner.command = ["flow123d", params[0]]
        return runner
        
    def _update(self):    
        """
        Process action on client site and return None or prepare process 
        environment and return Runner class with  process description if 
        action is set for externall processing.        
        """
        file = self.__parametrise_file()
        return  self._get_runner([file])
        
    def _after_update(self, store_dir):    
        """
        Set real output variable and set finished state.
        """
        # TODO read output from files
        self._store_results(store_dir)
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
        # TODO logic
        return String("Test")
        
    def __parametrise_file(self):
        """Rename and make completation of Yaml file and return new file path"""
        # TODO logic
        pass

    def _store(self, path):
        """
        make all needed serialization processess and
        return text data for storing
        """
        res = ""
        # TODO copy result files to store path and store only files names
        return res

    def _restore(self, text, path):
        """
        make all needed deserialization processess and
        return text data for storing
        """
        # TODO instead next commented line restore files names and make output from it
        # self._output = eval(res)
