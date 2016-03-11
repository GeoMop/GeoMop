from .action_types import GeneratorActionType, Runner, ActionType, BaseActionType
from .data_types_tree import CompositeDTT

class RangeGenerator(GeneratorActionType):
    
    _name = "RangeGenerator"
    """Display name of action"""
    _description = "Generator for generation parallel list"
    """Display description of action"""  

    def __init__(self, **kwargs):
        """
        :param DTT Output: type of data, that is use in constructor as
            template for resalt structure if empty, type is constructed
            from values as Struct of set names 
        :param Dictionary Items: Dictionary that describe generated
            way how generate result. Values have this attributes::
                - :name(string):require  variable name 
                - :value(float): require variable middle value
                - :step(float): default 1, step for generation
                - :n_plus(integer): default 1, amount of plus steps
                - :n_minus(integer): default 1, amount of minus steps
                - :exponential(bool): default False, if true value is processed exponencially 
        :param AllCases bool: Cartesian product, default value False:
        """
        super(RangeGenerator, self).__init__(**kwargs)
        self.file_output = self._get_output()
        if self.output is None:
            self.output = self._get_output_from_items()

    def _get_output_from_items(self):
        """Construct output from set items"""
        # ToDo
        pass

    def _get_variables_script(self):    
        """return array of variables python scripts"""
        var = super(RangeGenerator, self)._get_variables_script()
        if self.variables["AllCases"]:
            var.append("AllCases=False")
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
        err = self._check_params()
        if not self.output.match_type(self.file_output):
            err.append("Output type validation fails")
        if isinstance(input[0], BaseActionType) and len(self.inputs)>0:
            input_type = self.inputs[0].output
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
        
    
