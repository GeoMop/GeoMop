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
    """action is created"""
    initialized = 1
    """action is inicialized"""
    wait = 2
    """action is ready for processing or validation"""
    process = 3
    """action is processed"""
    finished = 4
    """action is finished"""

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
"""action counter for unique settings in created script for code generation"""
        
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
        """list names => types of input ports"""
        self.inputs_os = []
        """
        List of integers, where integer is number of output slot 
        where is action join (opposite slot) default is first slot
        """        
        self.outputs = []
        """list names => DTT typse on output ports"""
        self.variables = {}
        """dictionary names => types of variables"""
        self.type = ActionType.simple
        """action type"""
        for name, value in kwargs.items():
            if name == 'Input':
                self.inputs.append(value)
            elif name == 'Inputs':
                self.inputs.extend(value)
            elif name == 'InputOpposite':
                self.inputs_os.append(value)
            elif name == 'InputOpposites':
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
    def get_output(self, number):
        """return output relevant for set action"""
        pass
   
    def get_input_val(self, number):
        """
        if input is action type, return output from previous action,
        else return input. Both action must be inicialized
        """
        if len(self.inputs)>number:
            if isinstance(self.inputs[number],  BaseActionType):
                return self.inputs[number].get_output(self.inputs_os[number])
            else:
                return self.inputs[number]                
        return None
    
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
     
    @classmethod
    def _format_array(cls, name, array, spaces, err):
        """
        return lines with formated array
        """
        res = []
        if len(array)>0: 
            res.append(spaces*" "+name+"=[")
            for var in array:
                if cls._is_DTT(var):
                    res.extend(Formater.format_parameter(var.get_settings_script(), spaces+4))
                elif isinstance(var, BaseActionType):
                    res.append((spaces+4)*" "+"{0},".format(var.get_instance_name()))
                else:
                    raise Exception(err)
            res[-1] = res[-1][:-1]
            res.append(spaces*" "+"],")   
            return res
            
    @classmethod
    def _format_param(cls, name, var, spaces, err):
        """
        return lines with formated param
        """
        res = []
        if cls._is_DTT(var):
            res.extend(Formater.format_variable(name, var.get_settings_script(), spaces))
        elif isinstance(var, BaseActionType):
            res.append(spaces*" "+name + "={0},".format(var.get_instance_name()))
        else:
            raise Exception(err)
        return res

    def get_settings_script(self):    
        """return python script, that create instance of this class"""
        lines = []
        lines.append("{0}_{1} = {2}(".format(self.name, str(self.id), self.__class__.__name__))
        if len(self.inputs)==1:
            lines.extend(self._format_param("Input", self.inputs[0], 4, "Unknown input type"))
        elif len(self.inputs)>1:
            lines.extend(self._format_array("Inputs", self.inputs, 4, "Unknown input type"))
        if len(self.inputs_os)>1:
            nonzer = False
            var="["
            for id in self.inputs_os:
                var += str(id)
                if id!=0:
                    nonzer = True
            if nonzer:
                var = var[:-1]+']'
                lines.extend(Formater._format_variable('InputOpposites', var, 4))
        if len(self.outputs)==1:
            lines.extend(self._format_param("Output", self.outputs[0], 4, "Unknown output type"))
        elif len(self.outputs)>1:
            lines.extend(self._format_array("Outputs", self.outputs, 4, "Unknown output type"))                        
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

    @abc.abstractmethod
    def validate(self):    
        """validate variables, input and output"""
        pass
    
    def _get_dependences(self):
        """return all direct inputs deoendences"""
        dependency=[]
        for input in  self.inputs:
            if isinstance(input,  BaseActionType):
                dependency.append(input)
        return dependency
        
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

class Bridge(BaseActionType):
    """Action that directed output to output method of link class"""
    
    def __init__(self, workflow):
        self.workflow =workflow
        """Workflow action"""        
        self.link=None
        """Real action for gaining output"""
        self.get_func =None
        
    def set_new_link(self, link, get_func):
        self.link=link
        self.get_func = link.get_output
        if get_func is not None:
            self.get_func = get_func

    def inicialize(self):
        pass
        
    def get_output(self, number):
        if self.link is not None:
            return self.get_func(number)

    def _check_params(self):    
        return []
    
    def validate(self):
        return []
    
    def _get_runner(self, params):    
        return None
        
    def run(self):    
        return  self._get_runner(None) 
 
    def get_instance_name(self):
        return "{0}.input()".format(self.workflow.get_instance_name())

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
    
    :param WorkflowActionType WrappedAction: Wrapped action
        that is processed by wrapper action.
    """
    
    def _set_bridge(self, bridge):
        """redirect bridge to wrapper"""
        bridge.set_new_link(self)
    
    def __init__(self, **kwargs):
        super(WrapperActionType, self).__init__(**kwargs)
        
    def inicialize(self):
        """inicialize action run variables"""
        if self.state.value > ActionStateType.created.value:
            return
        # set state before recursion, inicialize ending if return to this action
        self.state = ActionStateType.initialized
        if  'WrappedAction' in self.variables and \
            isinstance(self.variables['WrappedAction'],  WorkflowActionType):
                self.variables['WrappedAction'].inicialize()
                #set workflow bridge to special wrapper action bridge
                self._set_bridge(self.variables['WrappedAction'].bridge)
 
    def _check_params(self):    
        """check if all require params is set"""
        err = []
        if self.state is ActionStateType.created:
            err.append("Inicialize method should be processed before checking")
        if  not 'WrappedAction' in self.variables:
            err.append("Parameter 'WrappedAction' is require")
        else:
            if not isinstance(self.variables['WrappedAction'],  WorkflowActionType):
                err.append("Parameter 'WrappedAction' must be WorkflowActionType")            
        if len(self.inputs)  != 1:
            err.append("Wrapper action require exactly one input parameter")
        return err

    def get_settings_script(self):    
        """return python script, that create instance of this class"""
        lines = []
        if 'WrappedAction' in self.variables and \
            isinstance(self.variables['WrappedAction'],  WorkflowActionType):
            lines.extend(self.variables['WrappedAction'].get_settings_script())
        lines.extend(super(WrapperActionType, self).get_settings_script())
        return lines

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
        
    @classmethod
    def _order_child_list(cls, actions):
        """
        return ordered list from actions. If all dependencies is not
        in list, raise exception. First action in list must be one of 
        end actions. If list is partly ordered, function is faster
        """
        last_count = len(actions)
        ordered_action=[actions.pop(0)]
        while len(actions)>0:
            if last_count==len(actions):
                raise Exception("All Dependencies aren't in list")
            last_count=len(actions)
            for i in range(0, len(actions)):
                if cls._check_action_dependencies(actions[i], ordered_action):
                    ordered_action.append(actions.pop(i))
                    break
        return ordered_action

    @staticmethod 
    def _get_action_list(action, stop_action=None):
        """
        get not-ordered list of dependent action. If stop 
        action is set, list end in this action
        """
        before_end=stop_action is None
        actions=[action]
        if action == stop_action:
            return actions
        process=[]
        while True: 
            for action_next in action._get_dependences():
                if stop_action and action_next==stop_action:
                    before_end=True
                    continue
                if action_next in actions:
                    continue                
                process.append(action_next)
                actions.append(action_next)
            if len(process)==0:
                if not before_end:
                    return []
                if stop_action is not None:
                    actions.append(stop_action)
                break
            action=process.pop(0)
        return actions

    @staticmethod 
    def _merge_actions_lists(list1, list2):
        """
        get not-ordered list of dependent action. If stop 
        action is set, list end in this action
        """
        for action in list2:
            if action in list1:
                break
            else:
                list1.insert(0, action)
        return list1

    @staticmethod
    def _check_action_dependencies(action, list):
        """check if all direct dependecies is in set action list"""
        for dep_action in action._get_dependences():
            if dep_action not in list:
                return False
        return True

    
