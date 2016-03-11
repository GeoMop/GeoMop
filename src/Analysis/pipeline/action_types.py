import abc
from enum import IntEnum
from .data_types_tree import BaseDTT, CompositeDTT
from .code_formater import Formater

class ActionType(IntEnum):
    """Action type"""
    simple = 0
    complex = 1

class Runner():
    """
    Data crate for action process runner description 
    """
    def __init__(self, type=ActionType.simple):
        self.name = ""
        """Runner name for loging"""
        self.command = ""
        """Command for popen"""
        self.params = {}
        """dictionary names => types of input ports"""
        self.type =  type   

__action_counter__ = 0
"""action counter"""
        
class BaseActionType(metaclass=abc.ABCMeta):
    """
    Abstract class of action type, that define tasks method for
    tasks classes
    """

    _name = ""
    """Display name of action"""
    _description = ""
    """Display description of action"""

    def __init__(self, **kwargs):
        global __action_counter__
 
        __action_counter__ += 1
        self.id = __action_counter__
        """unique action number"""
        self.inputs = []
        """dictionary names => types of input ports"""
        self.output = None
        """DTT type on output port"""
        self.variables = {}
        """dictionary names => types of variables"""
        self.type = ActionType.simple
        """action type"""
        for name, value in kwargs.items():
            if name == 'Input':
                self.inputs.append(value)
            elif name == 'Inputs':
                self.inputs.extend(value)
            elif name == 'Output':
                self.output=value
            else:
                self.variables[name] = value
    
    @property
    def name(self):
        return self._name
        
    @property
    def description(self):
        return self._description

    def get_settings_script(self):    
        """return python script, that create instance of this class"""
        lines = []
        lines.append("{0}_{1} = {2}(".format(self.name, str(self.id), self.__class__.__name__))
        lines.append("        Inputs = [")
        is_emty=True
        for input in self.inputs:
            is_emty=False
            if isinstance(input, BaseDTT) or  isinstance(input, CompositeDTT):
                lines.extend(Formater.format_parameter(input.get_settings_script(), 12))
            elif isinstance(input, BaseActionType):
                lines.append("            {0},".format(input.get_instance_name()))
            else:
                raise Exception("Unknown input type")
        if not is_emty:
            lines[-1] = lines[-1][:-1]
        lines.append("        ],")

        if self.output is not None:
            lines.append("        Output = (")
            if not (isinstance(self.output, BaseDTT) or  isinstance(self.output, CompositeDTT)):
                raise Exception("Unknown output type")
            lines.extend(Formater.format_parameter(self.output.get_settings_script(), 12))
            lines[-1] = lines[-1][:-1]
        lines.append("        ),") 
        for script in self._get_variables_script():
            lines.append("        {0},".format(script))
        lines[-1] = lines[-1][:-1]
        lines.append("    )")
        return lines
            
    def get_instance_name(self):
        return "{0}_{1}".format(self.name, str(self.id))
        
    def _get_variables_script(self):    
        """return array of variables as python scripts"""
        return []
        
    @abc.abstractmethod 
    def _get_runner(self,  params):    
        """
        return Runner class with process description
        """
        pass
        
    @abc.abstractmethod 
    def run(self):    
        """
        Process action on client site or prepare process environment and 
        return Runner class with  process description or None if action not 
        need externall processing.
        """
        pass
        
    @abc.abstractmethod 
    def validate(self):    
        """validate variables, input and output"""
        pass
        
    @abc.abstractmethod 
    def _check_params(self):
        """check if all require params is set"""
        pass

class ConvertorActionType(BaseActionType, metaclass=abc.ABCMeta):
        def __init__(self, **kwargs):
            super(GeneratorActionType, self).__init__(**kwargs)
            
        def _check_params(self):    
            """check if all require params is set"""
            err = []
            if len(self.inputs)<1:
                err.append("Convertor action require at least one input parameter")
            if self.output is not None:
                err.append("Convertor action require exactly one output parameter")
            return err

class GeneratorActionType(BaseActionType, metaclass=abc.ABCMeta):
        def __init__(self, **kwargs):
            super(GeneratorActionType, self).__init__(**kwargs)
            
        def _check_params(self):    
            """check if all require params is set"""
            err = []
            if len(self.inputs)>0:
                err.append("Generator action not use input parameter")
            if self.output is None:
                err.append("Generator action require output parameter")
            return err
            
class ParametrizedActionType(BaseActionType, metaclass=abc.ABCMeta):
        def __init__(self, **kwargs):
            super(ParametrizedActionType, self).__init__(**kwargs)
            
        def _check_params(self):    
            """check if all require params is set"""
            err = []
            if len(self.inputs)  != 1:
                err.append("Parametrized action require exactly one input parameter")
            return err
