import abc
from enum import IntEnum
from .data_types_tree import *
from .generic_tree import GDTT
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
__initialized_predicators__ = []
"""This variable guard duplicit inicialization of predicators"""
        
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
        """list names => base action types on input ports"""        
        self.output = None
        """DTT type on output ports (not settable)"""
        self.variables = {}
        """dictionary names => types of variables"""
        self.type = ActionType.simple
        """action type"""
        self._load_errs = []
        """initialiyacion or sets errors"""
        self.set_config(**kwargs)

    def set_config(self, **kwargs):
        """set action config variables"""
        for name, value in kwargs.items():
            if name == 'Inputs':
                self.set_inputs(value)
            elif name == 'Output':
               self._load_errs.append("Output variable is not settable.")
            else:
                self.variables[name] = value

    def set_inputs(self, inputs):
        """set action input variables"""
        if not isinstance(inputs, list):
            self._load_errs.append("Inputs parameter must be list.")
            return        
        self.inputs = inputs

    @abc.abstractmethod
    def inicialize(self):
        """inicialize action run variables"""
        pass
        
    def get_output(self):
        """return output relevant for set action"""
        return self.output
   
    def get_input_val(self, number):
        """
        if input is action type, return output from previous action,
        else return input. Both action must be inicialized
        """
        return self.inputs[number].get_output()
    
    @property
    def name(self):
        return self._name
        
    @property
    def description(self):
        return self._description
     
    @classmethod
    def _format_array(cls, name, array, spaces, err):
        """
        return lines with formated array
        """
        res = []
        if len(array)>0: 
            res.append(spaces*" "+name+"=[")
            for var in array:
                if isinstance(var, DTT):
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
        if  isinstance(var, DTT):
            res.extend(Formater.format_variable(name, var.get_settings_script(), spaces))
        elif isinstance(var, BaseActionType):
            res.append(spaces*" "+name + "={0},".format(var.get_instance_name()))
        else:
            raise Exception(err)
        return res
 
    def _format_config_to_setter(self, names, values):
        """
        return lines with formated setter with set config params
        
        length of value and names paramer must be same
        :param list names: list of config parameter names, 
            that will be formated in setter
        :param list names: list of config parameter values, 
            value is next list, that can have more lines            
        """
        if len(names)<1:
            return
        res = []
        res.append("{0}.set_config(".format(self.get_instance_name()))
        if len(names)==1 and len(values[0]) == 1:
            return ["{0}.set_config({1}={2})".format(
                self.get_instance_name(), names[0], values[0][0])] 
        for i in range(0, len(names)):
            res.extend(Formater.format_variable(names[i], values[i], 4))
        res[-1] = res[-1][:-1]
        res.append(")")
        return res           
            
    def get_settings_script(self):    
        """return python script, that create instance of this class"""
        lines = []
        lines.append("{0}_{1} = {2}(".format(self.name, str(self.id), self.__class__.__name__))
        lines.extend(self._format_array("Inputs", self.inputs, 4, "Unknown input type"))
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

    def validate(self):    
        """validate variables, input and output"""
        err = []
        err.extend(self._load_errs)
        err.extend(self._check_params())        
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
        
    @staticmethod
    def clear_predicates():
        """delete all predicates"""
        global __initialized_predicators__
        __initialized_predicators__ = []
        
    @staticmethod
    def add_predicate(predicate):
        """add predicate if not exist and return if is added"""
        global __initialized_predicators__
        if not predicate in __initialized_predicators__:
            __initialized_predicators__.append(predicate)
            return True
        return False

class InputType(BaseActionType, metaclass=abc.ABCMeta):
    def __init__(self, **kwargs):
        """
        :param GDTT DefInputs: Convertor template may have 
            GDTT types for checking. when is set real input, input typ is compare
            with this parameter
        """
        super(InputType, self).__init__(**kwargs)
        if 'DefInputs' not in self.variables:
            self.variables['DefInputs']=[]
        for i in range(0, len(self.variables['DefInputs'])):
            self.variables['DefInputs'][i].set_path("{0}.input({1})".format(
                self.get_instance_name(),str(i)))

    def set_output(self, preinit_script=[]):
        """inicialize action run variables"""
        try:            
            script = '\n'.join(self.variables['DefOutput'].get_settings_script())
            script = script.replace(self.get_instance_name()+".input", "self.input")
            if len(preinit_script)>0:
                prescript = '\n'.join(preinit_script)
                exec(prescript, globals())
            self.output = eval(script)
        except Exception as err:
            raise Exception("Output processing error ({0})".format(err))

    def input(self, i):
        """Function for generic input defination"""
        if len(self.inputs)>i and self.state.value > ActionStateType.created.value:
            return self. get_input_val(i)
        while len(self.variables['DefInputs'])<=i:
            attr = GDTT()
            attr.set_path("{0}.input({1})".format(self.get_instance_name(), str(i)))
            self.variables['DefInputs'].append(attr)
        return self.variables['DefInputs'][i]
    
    def get_settings_script(self):    
        """return python script, that create instance of this class"""
        lines = super( InputType, self).get_settings_script()
        names=['DefOutput']
        values=[self.variables['DefOutput'].get_settings_script()]
        lines.extend(self._format_config_to_setter(names, values))
        return lines
    
    def _get_variables_script(self):    
        """return array of variables python scripts"""
        var = super( InputType, self)._get_variables_script()
        
        lines=["DefInputs=["]
        for input in self.variables['DefInputs']:
            script = input.get_main_settings_script()
            lines.extend(Formater.format_parameter(script, 4))
        lines[-1] = lines[-1][:-1]
        lines.append("]")
        var.append(lines)        
        return var

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
        
    def get_output(self):
        if self.link is not None:
            return self.get_func()

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

class ConvertorActionType(InputType, metaclass=abc.ABCMeta):
    def __init__(self, **kwargs):
        super(ConvertorActionType, self).__init__(**kwargs)
        
    def _check_params(self):    
        """check if all require params is set"""
        err = []
        if self.state is ActionStateType.created:
            err.append("Inicialize method should be processed before checking")
        if len(self.inputs)<1:
            err.append("Convertor action requires at least one input parameter")
        else:
            for input in self.inputs:
                if not isinstance(input, BaseActionType):
                    err.append("Parameter 'Inputs' ({0}) must be BaseActionType".format(
                        self.name))

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
            err.append("Parametrized action requires exactly one input parameter")
        else:
            for input in self.inputs:
                if not isinstance(input, BaseActionType):
                    err.append("Parameter 'Inputs' ({0}) must be BaseActionType".format(
                        self.name))
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
            err.append("Parameter 'WrappedAction' is required")
        else:
            if not isinstance(self.variables['WrappedAction'],  WorkflowActionType):
                err.append("Parameter 'WrappedAction' must be WorkflowActionType")            
        if len(self.inputs)  != 1:
            err.append("Wrapper action requires exactly one input parameter")
        else:
            for input in self.inputs:
                if not isinstance(input, BaseActionType):
                    err.append("Parameter 'Inputs' ({0}) must be BaseActionType".format(
                        self.name))

        return err

    def get_settings_script(self):    
        """return python script, that create instance of this class"""
        lines = []
        lines.extend(self.variables['WrappedAction'].get_settings_script())
        lines.extend(super(WrapperActionType, self).get_settings_script())
        return lines

class WorkflowActionType(BaseActionType, metaclass=abc.ABCMeta):
    def __init__(self, **kwargs):
        """
        Class for actions grouping.
        :param list of BaseActionType ResultActions: Action that is blined , that created
            pipeline side effects (result)
        """
        super(WorkflowActionType, self).__init__(**kwargs)
        
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
            for action_next in action.inputs:
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
        for dep_action in action.inputs:
            if dep_action not in list:
                return False
        return True
        
    def _check_params(self):           
        """check if all require params is set"""
        err = []
        if self.state is ActionStateType.created:
            err.append("Inicialize method should be processed before checking")
        if  'ResultActions' in self.variables:
            if isinstance(self.variables['ResultActions'], list):
                err.append("Parameter 'ResultActions' must be list of output actions")
            elif len(self.variables['ResultActions'], list)<1:
                err.append("Parameter 'ResultActions' must contains least one action")
            else:
                for i in range(0, len(self.variables['ResultActions'], list)):
                    if not isinstance(self.variables['ResultActions'],  BaseActionType):
                        err.append("Type of parameter 'ResultActions[{0}]'  must be BaseActionType".format(str(i)))                    
        return err
    
    @staticmethod
    def clear_predicates():
        global __initialized_predicators__
        __initialized_predicators__ = []
