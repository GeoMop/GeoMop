import abc
from enum import IntEnum
from .data_types_tree import *
from .code_formater import Formater
import math

class ActionsStatistics:
    def __init__(self):
        self.known_jobs = 0
        """count of known jobs (minimal amount of jobs)"""
        self.estimated_jobs = 0
        """estimated count of jobs"""
        self.finished_jobs = 0
        """count of finished jobs"""
        self.running_jobs = 0
        """count of running jobs"""
        
    def duplicate(self):
        ret = ActionsStatistics()
        ret.known_jobs = self.known_jobs
        ret.estimated_jobs = self.estimated_jobs
        ret.finished_jobs = self.finished_jobs
        ret.running_jobs = self.running_jobs
        return ret
        
    def add(self, astat, multiplied=1):
        self.known_jobs += astat.known_jobs*multiplied
        self.estimated_jobs += astat.estimated_jobs*multiplied
        self.finished_jobs += astat.finished_jobs*multiplied
        self.running_jobs += astat.running_jobs*multiplied

class ActionType(IntEnum):
    """Action type"""
    simple = 0
    complex = 1
    
class ActionRunningState(IntEnum):
    """IAction state after run processing"""
    finished = 0
    """Action is finished, runner is None"""
    repeat = 1
    """action can return next runner, runner is None or value"""
    wait = 2
    """action wait to external job processing"""
    error = 3
    """end processing and send error"""
    
class ActionStateType(IntEnum):
    """Action type"""
    created = 0
    """action is created"""
    initialized = 1
    """action is inicialized"""
    wait = 2
    """action is ready for processing or validation"""
    processed = 3
    """action is processed"""
    finished = 4
    """action is finished"""

class Runner():
    """
    Data crate for action process runner description 
    """
    def __init__(self, action, id):
        self.name = ""
        """Runner name for loging"""
        self.command = ""
        """Command for popen"""
        self.params = {}
        """dictionary names => types of input ports"""
        self.action =  action
        """action"""
        self.id =  id
        """action unique id"""

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
        self._id = __action_counter__
        """unique action number"""
        self._state = ActionStateType.created
        """action state"""
        self._inputs = []
        """list names => base action types on input ports"""        
        self._output = None
        """DTT type on output ports (not settable)"""
        self._variables = {}
        """dictionary names => types of variables"""
        self._type = ActionType.simple
        """action type"""
        self._load_errs = []
        """initializacion or sets errors"""
        self.set_config(**kwargs)

    def set_config(self, **kwargs):
        """set action config variables"""
        for name, value in kwargs.items():
            if name == 'Inputs':
                self.set_inputs(value)
            elif name == 'Output':
               self._load_errs.append("Output variable is not settable.")
            else:
                self._variables[name] = value

    def set_inputs(self, inputs):
        """set action input variables"""
        if not isinstance(inputs, list):
            self._load_errs.append("Inputs parameter must be list.")
            return        
        self._inputs = inputs
        
    def _get_statistics(self):
        """return all statistics for this and child action"""
        ret = ActionsStatistics()
        if self._type == ActionType.complex:
            if self._state is ActionStateType.finished:
                ret.finished_jobs += 1
            elif self._state is ActionStateType.processed:
                ret.running_jobs += 1
            else:
                ret.known_jobs += 1
                ret.estimated_jobs += 1
        return ret
        
    @abc.abstractmethod
    def _inicialize(self):
        """inicialize action run variables"""
        pass
        
    def _get_output(self):
        """return output relevant for set action"""
        return self._output
   
    def get_input_val(self, number):
        """
        Gain input from preceding action, check type and
        duplicate it.
        """
        if len(self._inputs)<=number:
            return None
        input_val = self._inputs[number]._get_output()
        if isinstance( input_val, GDTT):
            input_val =  input_val.duplicate()
        return input_val
    
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
                    res.extend(Formater.format_parameter(var._get_settings_script(), spaces+4))
                elif isinstance(var, BaseActionType):
                    res.append((spaces+4)*" "+"{0},".format(var._get_instance_name()))
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
            res.extend(Formater.format_variable(name, var._get_settings_script(), spaces))
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
        res.append("{0}.set_config(".format(self._get_instance_name()))
        if len(names)==1 and len(values[0]) == 1:
            return ["{0}.set_config({1}={2})".format(
                self._get_instance_name(), names[0], values[0][0])] 
        for i in range(0, len(names)):
            res.extend(Formater.format_variable(names[i], values[i], 4))
        res[-1] = res[-1][:-1]
        res.append(")")
        return res           
            
    def _get_settings_script(self):    
        """return python script, that create instance of this class"""
        lines = []
        lines.append("{0}_{1} = {2}(".format(self.name, str(self._id), self.__class__.__name__))
        lines.extend(self._format_array("Inputs", self._inputs, 4, "Unknown input type"))
        for script in self._get_variables_script():
            lines.extend(Formater.indent(script, 4))
            lines[-1] += ","
        if len(lines)==1:
            lines[0] = lines[0]+')'
        else:
            lines[-1] = lines[-1][:-1]
            lines.append(")")
        return lines
            
    def _get_instance_name(self):
        return "{0}_{1}".format(self.name, str(self._id))
        
    def _get_next_instance_name(self):
        id = __action_counter__ + 1
        return "{0}_{1}".format(self.name, str(id))
        
    def _get_variables_script(self):    
        """
        return array of variables as python scripts
        each item is array of variables in format 'variable=value'
        if value is extend to more lines, value must be closed to bracked
        """
        return []
    
    def _get_runner(self, params):    
        """
        return Runner class with process description
        """        
        return None 
 
    @abc.abstractmethod 
    def _run(self):    
        """
        Process action on client site or prepare process environment and 
        return ActionRunningState and Runner class with  process description 
        or None if action not need externall processing.
        """
        pass
        
    def _after_run(self):    
        """
        Set real output variable and set finished state.
        """
        self._state = ActionStateType.finished

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

class Bridge(BaseActionType):
    """Action that directed output to output method of link class"""
    
    def __init__(self, workflow):
        self._workflow =workflow
        """Workflow action"""        
        self._link=None
        """Real action for gaining output"""
        self._get_func =None
        
    def _set_new_link(self, link, get_func):
        self._link=link
        self._get_func = link._get_output
        if get_func is not None:
            self._get_func = get_func

    def _inicialize(self):
        pass
        
    def _get_output(self):
        if self._link is not None:
            return self._get_func()

    def _check_params(self):    
        return []
    
    def validate(self):
        return []
        
    def _run(self):    
        return  ActionRunningState.finished, self._get_runner(None) 
 
    def _get_instance_name(self):
        return "{0}.input()".format(self._workflow._get_instance_name())

class ConnectorActionType(BaseActionType, metaclass=abc.ABCMeta):
    def __init__(self, **kwargs):
        super(ConnectorActionType, self).__init__(**kwargs)
        
    def _check_params(self):    
        """check if all require params is set"""
        err = []
        if self._state is ActionStateType.created:
            err.append("Inicialize method should be processed before checking")
        if len(self._inputs)<1:
            err.append("Convertor action requires at least one input parameter")
        else:
            for input in self._inputs:
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
        if self._state is ActionStateType.created:
            err.append("Inicialize method should be processed before checking")
        if len(self._inputs)>0:
            err.append("Generator action not use input parameter")
        return err

class ParametrizedActionType(BaseActionType, metaclass=abc.ABCMeta):
    def __init__(self, **kwargs):
        super(ParametrizedActionType, self).__init__(**kwargs)
        
    def _check_params(self):    
        """check if all require params is set"""
        err = []
        if self._state is ActionStateType.created:
            err.append("Inicialize method should be processed before checking")
        if len(self._inputs)  != 1:
            err.append("Parametrized action requires exactly one input parameter")
        else:
            for input in self._inputs:
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
        bridge._set_new_link(self)
    
    def __init__(self, **kwargs):
        super(WrapperActionType, self).__init__(**kwargs)
        
    def _inicialize(self):
        """inicialize action run variables"""
        if self._state.value > ActionStateType.created.value:
            return
        # set state before recursion, inicialize ending if return to this action
        self._state = ActionStateType.initialized
        if  'WrappedAction' in self._variables and \
            isinstance(self._variables['WrappedAction'],  WorkflowActionType):
                self._variables['WrappedAction']._inicialize()
                #set workflow bridge to special wrapper action bridge
                self._set_bridge(self._variables['WrappedAction'].bridge)
 
    def _check_params(self):    
        """check if all require params is set"""
        err = []
        if self._state is ActionStateType.created:
            err.append("Inicialize method should be processed before checking")
        if  not 'WrappedAction' in self._variables:
            err.append("Parameter 'WrappedAction' is required")
        else:
            if not isinstance(self._variables['WrappedAction'],  WorkflowActionType):
                err.append("Parameter 'WrappedAction' must be WorkflowActionType")            
        if len(self._inputs)  != 1:
            err.append("Wrapper action requires exactly one input parameter")
        else:
            for input in self._inputs:
                if not isinstance(input, BaseActionType):
                    err.append("Parameter 'Inputs' ({0}) must be BaseActionType".format(
                        self.name))

        return err

    def _get_settings_script(self):    
        """return python script, that create instance of this class"""
        lines = []
        lines.extend(self._variables['WrappedAction']._get_settings_script())
        lines.extend(super(WrapperActionType, self)._get_settings_script())
        return lines

class WorkflowActionType(BaseActionType, metaclass=abc.ABCMeta):
    def __init__(self, **kwargs):
        """
        Class for actions grouping.
        :param list of BaseActionType ResultActions: Action that is blined , that created
            pipeline side effects (result)
        """
        super(WorkflowActionType, self).__init__(**kwargs)
        self.__processed_actions = None
        """Action that wait for next procesing"""
        self.__next_action = 0
        """Action that will be processed in next calling of run function"""


    def _get_statistics(self):
        """return all statistics for this and child action"""
        actions = self._get_child_list()
        ret = ActionsStatistics()
        for action in actions:
            stat = action._get_statistics()
            ret.add(stat)
        return ret
    
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
            for action_next in action._inputs:
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
        for dep_action in action._inputs:
            if dep_action not in list:
                return False
        return True
        
    def _check_params(self):           
        """check if all require params is set"""
        err = []
        if self._state is ActionStateType.created:
            err.append("Inicialize method should be processed before checking")
        if  'ResultActions' in self._variables:
            if not isinstance(self._variables['ResultActions'], list):
                err.append("Parameter 'ResultActions' must be list of output actions")
            else:
                for i in range(0, len(self._variables['ResultActions'])):
                    if not isinstance(self._variables['ResultActions'][i],  BaseActionType):
                        err.append("Type of parameter 'ResultActions[{0}]'  must be BaseActionType".format(str(i)))                    
        return err  
       
    @staticmethod
    def _is_independent(action):
        """check if all direct dependecies is in set action list"""
        for dep_action in action._inputs:
            if dep_action._state is not ActionStateType.finished:
                return False
        return True
     
    @staticmethod
    def _will_be_independent(action):
        """check if all direct dependecies is in set action list"""
        for dep_action in action._inputs:
            if dep_action._state is not ActionStateType.processed or \
                dep_action._state is not ActionStateType.finished:
                return False
        return True
 
    def _run(self):    
        """
        Process action on client site or prepare process environment and 
        return Runner class with  process description or None if action not 
        need externall processing.
        """
        if  self.__processed_actions is None:
            self.__processed_actions =self._get_child_list()
            self._state = ActionStateType.processed
        if len(self.__processed_actions) == 0:
            self._state = ActionStateType.finished
            return ActionRunningState.finished, None
        if self.__next_action>=len(self.__processed_actions):
            self.__next_action = 0
        start_action = self.__next_action
        all_dependent = True
        while True:
            if self._is_independent(self.__processed_actions[self.__next_action]):
                all_dependent = False
                state, runner = self.__processed_actions[self.__next_action]._run()
                if state is ActionRunningState.finished:
                    del self.__processed_actions[self.__next_action]
                    return ActionRunningState.repeat, runner
                if state is ActionRunningState.repeat:
                    return state, runner
                if state is ActionRunningState.error:
                    return state, runner 
                if state is ActionRunningState.wait and runner is not None:
                    return ActionRunningState.repeat, runner
                # run return wait, try next
            if all_dependent and \
                self. _will_be_independent(self.__processed_actions[self.__next_action]):
                all_dependent = False        
            self.__next_action += 1
            if self.__next_action>=len(self.__processed_actions):
                self.__next_action = 0
            if start_action == self.__next_action:
                break
        if all_dependent:
            return ActionRunningState.error,  \
                ["No independent action in workflow"]
        return ActionRunningState.wait, None        
