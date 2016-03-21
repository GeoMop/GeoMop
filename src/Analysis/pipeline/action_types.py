import abc
from enum import IntEnum
from .data_types_tree import BaseDTT, CompositeDTT
from .code_formater import Formater
import math

class ActionType(IntEnum):
    """Action type"""
    simple = 0
    complex = 1
    
class ActionStateType(IntEnum):
    """Action type"""
    created = 0
    initialized = 1
    wait = 2
    process = 3
    finished = 4   

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
        self.state = ActionStateType.created
        """action state"""
        self.inputs = []
        """dictionary names => types of input ports"""
        self.inputs_os = []
        """
        number of output slot where is action join (opposite slot)
        default is first slot
        """
        """dictionary names => types of input ports"""
        self.outputs = []
        """dictionary names => DTT typse on output ports"""
        self.variables = {}
        """dictionary names => types of variables"""
        self.type = ActionType.simple
        """action type"""
        self._checking=False
        """Variable for prevent recursive validation"""
        for name, value in kwargs.items():
            if name == 'Input':
                self.inputs.append(value)
            elif name == 'Inputs':
                self.inputs.extend(value)
            elif name == 'InputOpposite':
                self.inputs_os.append(value)
            elif name == 'InputOpposite':
                self.inputs_os.extend(value)
            elif name == 'Output':                
                self.outputs.append(value)
            elif name == 'Outputs':
                self.outputs.extend(value)
            else:
                self.variables[name] = value
        for i in range(len(self.inputs_os), len(self.inputs)):
            self.inputs_os.append(0)

    @abc.abstractmethod
    def inicialize(self):
        """inicialize action run variables"""
        pass
        
    @abc.abstractmethod
    def get_output(self,number):
        """return output relevant for set action"""
        pass
    
    @property
    def name(self):
        return self._name
        
    @property
    def description(self):
        return self._description
    
    @staticmethod
    def _is_DTT(var):
        """return if is var instance of DTT"""
        return isinstance(var, BaseDTT) or  isinstance(var, CompositeDTT)
        
    def get_settings_script(self):    
        """return python script, that create instance of this class"""
        lines = []
        lines.append("{0}_{1} = {2}(".format(self.name, str(self.id), self.__class__.__name__))
        if len(self.inputs)>0: 
            lines.append("    Inputs = [")
            for input in self.inputs:
                if self._is_DTT(input):
                    lines.extend(Formater.format_parameter(input.get_settings_script(), 8))
                elif isinstance(input, BaseActionType):
                    lines.append("        {0},".format(input.get_instance_name()))
                else:
                    raise Exception("Unknown input type")
            lines[-1] = lines[-1][:-1]
            lines.append("    ],")
        if len(self.outputs)>0:
            lines.append("    Outputs = [")
            for output in self.outputs:
                if self._is_DTT(output):
                    lines.extend(Formater.format_parameter(output.get_settings_script(), 8))
                elif isinstance(output, BaseActionType):
                    lines.append("        {0},".format(output.get_instance_name()))
                else:
                    raise Exception("Unknown output type")
            lines[-1] = lines[-1][:-1]
            lines.append("    ],")
        for script in self._get_variables_script():
            lines.extend(Formater.indent(script, 4))
            lines[-1] += ","
        if len(lines)==1:
            lines[0] = lines[0]+')'
        else:
            lines[-1] = lines[-1][:-1]
            lines.append(")")
        return lines
            
    def get_instance_name(self):
        return "{0}_{1}".format(self.name, str(self.id))
        
    def _get_variables_script(self):    
        """
        return array of variables as python scripts
        each item is array of variables in format 'variable=value'
        if value is extend to more lines, value must be closed to bracked
        """
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

    def prepare_validation(self):
        """set start validation for all actions recursivly"""
        self.checking=True
        for input in  self.inputs:
            if isinstance(input,  BaseActionType):
                input.prepare_validation() 
    
    def validate(self):    
        """validate variables, input and output"""
        if not self.checking:
            return []
        err = self._check_params()
        self.checking=False
        for input in  self.inputs:
            if isinstance(input,  BaseActionType):
                err.extend(input.validate())
        return err
        
    @abc.abstractmethod 
    def _check_params(self):
        """check if all require params is set"""
        pass
    
    @staticmethod
    def _check_var_name(value):
        """Check if value is correct variable name"""
        if isinstance(value, str):
            class A:
                def __init__(self):
                    pass
            a = A()
        try:
            setattr(a, value, 1)
            return getattr(a, value)==1
        except:
            pass
        return False
        
    @staticmethod
    def _check_int(value):
        """Check if value is correct integer"""
        if isinstance(value, int):
            return True
        if isinstance(value, float):
            v1=int(value)
            v2=math.floor(value)
            return v1==v2
        if isinstance(value, str):    
            try:
                int(value)
                return True
            except ValueError:
                pass
        return False
        
    
    @staticmethod
    def _check_float(value):
        """Check if value is correct float"""
        if isinstance(value, int):
            return True
        if isinstance(value, float):
            return True
        if isinstance(value, str):    
            try:
                float(value)
                return True
            except ValueError:
                pass
        return False

    @staticmethod
    def _check_bool(value):
        """Check if value is correct Boolean"""
        if isinstance(value, bool):
            return True
        return False


class ConvertorActionType(BaseActionType, metaclass=abc.ABCMeta):
    def __init__(self, **kwargs):
        super(GeneratorActionType, self).__init__(**kwargs)
        
    def _check_params(self):    
        """check if all require params is set"""
        err = []
        if self.state is ActionStateType.created:
            err.append("Inicialize method should be processed before checking")
        if len(self.inputs)<1:
            err.append("Convertor action require at least one input parameter")
        if len(self.outputs) !=1:
            err.append("Convertor action require exactly one output parameter")
        return err

class GeneratorActionType(BaseActionType, metaclass=abc.ABCMeta):
    def __init__(self, **kwargs):
        super(GeneratorActionType, self).__init__(**kwargs)
        
    def _check_params(self):    
        """check if all require params is set"""
        err = []
        if self.state is ActionStateType.created:
            err.append("Inicialize method should be processed before checking")
        if len(self.inputs)>0:
            err.append("Generator action not use input parameter")
        if len(self.outputs)!=1:
            err.append("Generator action require exactly one output parameter")
        return err
            
class ParametrizedActionType(BaseActionType, metaclass=abc.ABCMeta):
    def __init__(self, **kwargs):
        super(ParametrizedActionType, self).__init__(**kwargs)
        
    def _check_params(self):    
        """check if all require params is set"""
        err = []
        if self.state is ActionStateType.created:
            err.append("Inicialize method should be processed before checking")
        if len(self.inputs)  != 1:
            err.append("Parametrized action require exactly one input parameter")
        return err
            
class WrapperActionType(BaseActionType, metaclass=abc.ABCMeta):
    """
    Wrapper for some action (usualy workflow), that provide cyclic
    procesing
    
    :param BaseActionType WrappedAction: Wrapped action
        this parameter is set after declaration this action by function
        set_wrapped_action 
    """
    def __init__(self, **kwargs):
        super(WrapperActionType, self).__init__(**kwargs)

    def set_wrapped_action(self, action):
        self.variables['WrappedAction']=action
        
    def inicialize(self):
        if self.state.value > ActionStateType.created.value:
            return
        # set state before recursion, inicialize ending if return to this action
        self.state = ActionStateType.initialized
        if  'WrappedAction' in self.variables and \
            isinstance(self.variables['WrappedAction'],  BaseActionType):
                self.variables['WrappedAction'].inicialize()
                if len(self.outputs)==0:
                    self.outputs.append(self.get_output(0))
    
    def _check_params(self):    
        """check if all require params is set"""
        err = []
        if self.state is ActionStateType.created:
            err.append("Inicialize method should be processed before checking")
        if  not 'WrappedAction' in self.variables:
            err.append("Parameter 'WrappedAction' is require")
        else:
            if not isinstance(self.variables['WrappedAction'],  BaseActionType):
                err.append("Parameter 'WrappedAction' must be BaseActionType")            
        if len(self.inputs)  != 1:
            err.append("Wrapper action require exactly one input parameter")
        return err
        
    def _get_variables_script(self):    
        """return array of variables python scripts"""
        var = super(WrapperActionType, self)._get_variables_script()
        if 'WrappedAction' in self.variablesand and \
            isinstance(self.variables['WrappedAction'],  BaseActionType):
            var.append(["WrappedAction={0}".format(self.variables['WrappedAction'].get_instance_name())])

class WorkflowActionType(BaseActionType, metaclass=abc.ABCMeta):
    def __init__(self, **kwargs):
        """
        Class for actions grouping.
        """
        super(WorkflowActionType, self).__init__(**kwargs)
                    
    def _check_params(self):    
        """check if all require params is set"""
        err = []
        if self.state is ActionStateType.created:
            err.append("Inicialize method should be processed before checking")
        return err
    
