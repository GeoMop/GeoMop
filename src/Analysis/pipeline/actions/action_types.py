import abc
from enum import IntEnum

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
    
        
class BaseActionType(metaclass=abc.ABCMeta):
    """
    Abbstract class of action type, that define tasks method for
    tasks classes
    """
    
    def __init__(self, **kwargs):
        self.name = ""
        """Display name of action"""
        self.description = ""
        """Display description of action"""
        self.inputs = []
        """dictionary names => types of input ports"""
        self.outputs = []
        """dictionary names => types of output ports"""
        self.variables = {}
        """dictionary names => types of variables"""
        for name, value in kwargs.items():
            if name == 'Input':
                self.inputs.append(value)
            elif name == 'Inputs':
                self.inputs.extend(value)
            elif name == 'Output':
                self.outputs.append(value)
            elif name == 'Outputs':
                self.outputs.extend(value)
            elif name == 'Variables':
                self.outputs.extend(value)
                
    @abc.abstractmethod 
    def get_script(self):    
        """return action python script"""
        pass
        
    @abc.abstractmethod 
    def _get_runner(self):    
        """prepare process environment and return Runner class with process description"""
        pass
        
    @abc.abstractmethod 
    def validate(self):    
        """return action python script"""
        pass
        
    @abc.abstractmethod 
    def _check_params(self):    
        """check if all require params is set"""
        pass

class GeneratorActionType(BaseActionType, metaclass=abc.ABCMeta):
        def __init__(self, **kwargs):
            super(GeneratorActionType, self).__init__(**kwargs)
            
        def _check_params(self):    
            """check if all require params is set"""
            err = []
            if len(self.inputs)>0:
                err.append("Generator action not use input parameter")
            if len(self.outputs)>0:
                err.append("Generator action require exactly one output parameter")
            return err
            
class ParametrizedActionType(BaseActionType, metaclass=abc.ABCMeta):
        def __init__(self, **kwargs):
            super(ParametrizedActionType, self).__init__(**kwargs)
            
        def _check_params(self):    
            """check if all require params is set"""
            err = []
            if len(self.inputs)>0:
                err.append("Parametrized action require exactly one input parameter")
            if len(self.outputs)>0:
                err.append("Parametrized action require exactly one output parameter")
            return err
