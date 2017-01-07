import abc
from enum import IntEnum
from .data_types_tree import *
from .code_formater import Formater
import math
import uuid
import threading
import hashlib
import os

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

class QueueType(IntEnum):
    """Action type"""
    internal = 0
    external = 1
    
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
    processed = 2
    """action is processed"""
    finished = 3
    """action is finished"""

class Runner():
    """
    Data crate for action process runner description 
    """
    def __init__(self, action):
        self.name = ""
        """Runner name for loging"""
        self.command = []
        """Command for popen"""        
        self.action =  action
        """action"""
        self.id = uuid.uuid4()
        """action unique id"""

__action_counter__ = 0
"""action counter for unique settings in created script for code generation"""
        
class BaseActionType(metaclass=abc.ABCMeta):
    """
    Abstract class of action type, that define tasks method for
    tasks classes
    
    Thread safety and processing rules:
    Action in state less processed state is use only from
    one thread. Functions _get_variables_script and
    validate return right result only in initialized state.
    Action in processed state can be processed from 
    one partcular thread.
    Action dat in finished state can't be changed.
    State and priority variables are changed in _state_lock 
    and can be accessed from any thread by defined functions.
    """

    name = ""
    """Display name of action"""
    description = ""
    """Display description of action"""

    def __init__(self, **kwargs):
        global __action_counter__
        
        __action_counter__ += 1
        self._id = __action_counter__
        """unique action number"""
        self._store_id = str(self._id)
        """unique store number"""
        self._restore_id = None
        """unique restore number, if is None, restore is not processed"""
        self._state = ActionStateType.created
        """action state"""
        self._inputs = []
        """list names => base action types on input ports"""
        self._priority = 5
        """priority this action"""          
        self._output = None
        """DTT type on output ports (not settable)"""
        self._variables = {}
        """dictionary names => types of variables"""
        self._logical_queue = QueueType.internal
        """action type"""
        self._load_errs = []
        """initializacion or sets errors"""
        self._state_lock = threading.Lock()
        """lock for state changing, assignation rules for single 
        states is described above in class help"""
        self._hash = hashlib.sha512()
        """
        Unique hash that describe this action,
        this hash depends to inputs, action type and 
        sometimes to dependent data sources as is
        settings files. Hash is compute during 
        inicialization
        """ 
        self._was_processed = False
        """
        Action is set as processed, if its result is
        ready, and have same hash as action that was
        started in last time. This variable is only helper
        variable that is used during last run result 
        evaluation by pipeline.
        """
        self.set_config(**kwargs)
        
    def _set_state(self, new_state):
        """Secure state changing"""
        self._state_lock.acquire()
        self._state = new_state
        self._state_lock.release()
        
    def _get_state(self):
        """Secure state changing"""
        self._state_lock.acquire()
        new_state = self._state
        self._state_lock.release()
        return new_state
        
    def _set_priority(self, new_priority):
        """Secure priority changing"""
        self._state_lock.acquire()
        self._priority = new_priority
        self._state_lock.release()
        
    def _get_priority(self):
        """Secure priority getting"""
        self._state_lock.acquire()
        new_priority = self._priority
        self._state_lock.release()
        return new_priority
        
    def _is_state(self, state):
        """Secure state changing"""
        self._state_lock.acquire()
        res = self._state is state
        self._state_lock.release()
        return res

    def set_config(self, **kwargs):
        """set action config variables"""
        for name, value in kwargs.items():
            if name == 'Inputs':
                self.set_inputs(value)
            elif name == 'Output':
               self._add_error(self._load_errs, "Output variable is not settable.")
            else:
                self._variables[name] = value

    def set_inputs(self, inputs):
        """set action input variables"""
        if not isinstance(inputs, list):
            self._add_error(self._load_errs, "Inputs parameter must be list.")
            return        
        self._inputs = inputs
        
    def _get_statistics(self):
        """return all statistics for this and child action"""
        ret = ActionsStatistics()
        self._state_lock.acquire()
        if self._state is ActionStateType.finished:
            ret.finished_jobs += 1
        elif self._state is ActionStateType.processed:
            ret.running_jobs += 1
        else:
            ret.known_jobs += 1
            ret.estimated_jobs += 1
        self._state_lock.release()
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
                elif isinstance(var, str):
                    res.append((spaces+4)*" "+"'{0}',".format(var))
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
        inputs = []
        for input in self._inputs:
            if not isinstance(input, WrapperActionBridge):
                inputs.append(input)
        lines.extend(self._format_array("Inputs", inputs, 4, "Unknown input type"))
        for script in self._get_variables_script():
            lines.extend(Formater.indent(script, 4))
            lines[-1] += ","
        if len(lines)==1:
            lines[0] = lines[0]+')'
        else:
            lines[-1] = lines[-1][:-1]
            lines.append(")")
        return lines
        
    def _get_hash(self):
        """return unique hash that describe this action"""
        return self._hash.hexdigest()

    def _get_hashes_list(self):
        """return list of store_id->hash this and nested actions"""
        return {self._store_id: self._hash.hexdigest()}
        
    def _process_base_hash(self):
        """return hash compute from name and inputs"""
        self._hash.update(bytes(self.__class__.__name__, "utf-8"))
        for input in self._inputs:
            self._hash.update(bytes(input._get_hash(), "utf-8"))
        return self._hash

    def _set_restore_id(self, identical_list):
        """set restore_id from identical_list"""
        self._restore_id = identical_list.get_old_iname(self._store_id)

    def _store(self, path):
        """
        make all needed serialization processess and
        return text data for storing
        """
        res = self._output._get_settings_script()
        return res
        
    def _store_results(self, path):
        """
        Call store function for saving resalt data and write
        data to file in set path. If path is None, storing is not
        needed
        """
        if path is None:
            return
        if self._output is None:
            data = ""
        else:
            data = self._store(path)
        file = os.path.join(path, "store", "{0}_{1}".format(self.name, self._store_id))
        try:
            file_d = open(file, 'w')
            file_d.write('\n'.join(data))
            file_d.close()
        except (RuntimeError, IOError) as err:
            raise Exception("Can't save result to file {0} ({1})".format(path , str(err)))
    
    def _set_storing(self, identical_list):
        """set restore id"""
        name = self._get_instance_name()
        if name in identical_list:
            prefix = self.name + "_"
            if prefix == identical_list[name][:len(prefix)]:
                self._restore_id = identical_list[name][len(prefix):]
    
    def _restore(self, text, path):
        """
        make all needed deserialization processess and
        return text data for storing
        """
        self._output = eval(text)

    def _restore_results(self, path):
        """
        If restore is needed and restore data is available, read data 
        from file in set path and call restore function for restoring. If
        data is not available set restore_id to None, and related actin
        won't be processed
        """
        if self._restore_id is None:
            return
        for input in self._inputs:
            if isinstance(input, Bridge):
                input = input._link
            if input._restore_id is None:
                self._restore_id = None
                return
        self._restore_id
        file = os.path.join(path, "restore",  "{0}_{1}".format(self.name, self._restore_id))   
        try:
            file_d = open(file, 'r')
            data = file_d.read()
            file_d.close()
            self._restore(data, path)
        except (RuntimeError, IOError):
            self._restore_id = None

    def _get_instance_name(self):
        return "{0}_{1}".format(self.name, str(self._id))
        
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
 
    def _plan_action(self, path):
        """
        If next action can be panned, return processed state and 
        this action, else return processed state and null        
        """
        if self._is_state(ActionStateType.processed):
            return ActionRunningState.wait,  None
        if self._state == ActionStateType.finished:
            return ActionRunningState.finished,  self
        self._set_state(ActionStateType.processed)
        self._restore_results(path)
        if self._restore_id is not None:
            # send as short action for storing and settings state
            self._store_results(path)
            self._set_state(ActionStateType.finished)
            return ActionRunningState.finished,  self
        return  ActionRunningState.repeat,  self
 
    def _update(self):    
        """
        Process action on client site and return None or prepare process 
        environment and return Runner class with  process description if 
        action is set for externall processing.        
        """
        return None
        
    def _after_update(self, store_dir):    
        """
        Set real output variable and set finished state.
        """
        self._store_results(store_dir)
        self._set_state(ActionStateType.finished)

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

    def _add_error(self, err, message):
        """Append error message to err list"""
        err.append("{0}: {1}".format(self._get_instance_name(), message))

    def _extend_error(self, err, new_err):
        """Extend err list with new err list"""
        for message in new_err:
            self._add_error(err, message)

    def get_resources(self):
        """Return list of resource files"""
        return []

class Bridge(BaseActionType):
    """Action that directed output to output method of link class"""
    
    def __init__(self, workflow):
        self._workflow =workflow
        """Workflow action"""        
        self._link = None
        """Real action for gaining output"""
        self.action_checkable = True
        """Is possible check linke action (output is not parssed  from previous action)"""
        self._get_func = None 
        
    def _set_new_link(self, link, get_func=None):
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
        
    def _get_instance_name(self):
        return "{0}.input()".format(self._workflow._get_instance_name())
    
    def _set_state(self, new_state):
        """Secure state changing"""
        return  self._link._set_state(new_state)
        
    def _get_state(self):
        """Secure state changing"""
        return  self._link._get_state()
        
    def _is_state(self, state):
        return  self._link._is_state(state)
        
    def _get_hash(self):
        """return unique hash that describe this action"""
        return self._link._get_hash()
        
    def _get_hashes_list(self):
        """return list of store_id->hash this and nested actions"""
        return self._link._get_hashes_list()

    def check_action(self, actions):
        """return True if bridge direct to one of set actions"""
        if not self.action_checkable:
            # input is OK, is check in parent action
            return True
        return self._link in actions
       
class ConnectorActionType(BaseActionType, metaclass=abc.ABCMeta):
    def __init__(self, **kwargs):
        super(ConnectorActionType, self).__init__(**kwargs)
        
    def _check_params(self):    
        """check if all require params is set"""
        err = []
        if self._is_state(ActionStateType.created):
            self._add_error(err, "Inicialize method should be processed before checking")
        if len(self._inputs)<1:
            self._add_error(err, "Convertor action requires at least one input parameter")
        else:
            for input in self._inputs:
                if not isinstance(input, BaseActionType):
                    self._add_error(err, "Parameter 'Inputs' must be BaseActionType")

        return err

class GeneratorActionType(BaseActionType, metaclass=abc.ABCMeta):
    def __init__(self, **kwargs):
        super(GeneratorActionType, self).__init__(**kwargs)
        
    def _check_params(self):    
        """check if all require params is set"""
        err = []
        if self._is_state(ActionStateType.created):
            self._add_error(err, "Inicialize method should be processed before checking")
        if len(self._inputs)>0:
            self._add_error(err, "Generator action not use input parameter")
        return err
        
    def _store_results(self, path):
        """
        Not store
        """
        pass
        
    def _restore_results(self, path):
        """
        Not restore
        """
        pass
        
    def _set_restored(self):
        """set generator action as processed in last procesing and succesfully restored"""
        self._restore_id = self._store_id

class ParametrizedActionType(BaseActionType, metaclass=abc.ABCMeta):
    def __init__(self, **kwargs):
        super(ParametrizedActionType, self).__init__(**kwargs)
        
    def _check_params(self):    
        """check if all require params is set"""
        err = []
        if self._is_state(ActionStateType.created):
            self._add_error(err, "Inicialize method should be processed before checking")
        if len(self._inputs)  != 1:
            self._add_error(err, "Parametrized action requires exactly one input parameter")
        else:
            for input in self._inputs:
                if not isinstance(input, BaseActionType):
                    self._add_error(err, "Parameter 'Inputs' must be BaseActionType")
        return err


class OutputActionType(BaseActionType, metaclass=abc.ABCMeta):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _check_params(self):
        """check if all require params is set"""
        err = []
        if self._is_state(ActionStateType.created):
            self._add_error(err, "Inicialize method should be processed before checking")
        if len(self._inputs)  != 1:
            self._add_error(err, "Output action requires exactly one input parameter")
        else:
            for input in self._inputs:
                if not isinstance(input, BaseActionType):
                    self._add_error(err, "Parameter 'Inputs' must be BaseActionType")
        return err


class WrapperActionBridge(Bridge):
    """Action that provide output to wrapped action"""

    name = "WrapperActionBridge"
    """Display name of action"""
    description = "WrapperActionBridge"
    """Display description of action"""

    def __init__(self):
        super().__init__(None)

    def _get_instance_name(self):
        #return BaseActionType._get_instance_name(self)
        return self.name


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
        """String identificator for construction inner store names"""
        self._index_iden = ""
        super(WrapperActionType, self).__init__(**kwargs)
        self.bridge = WrapperActionBridge()
        """bridge that provide output to wrapped action"""
        
    def _inicialize(self):
        """inicialize action run variables"""
        if self._get_state().value > ActionStateType.created.value:
            return
        # set state before recursion, inicialize ending if return to this action
        self._set_state(ActionStateType.initialized)
        self._process_base_hash()
        if  'WrappedAction' in self._variables and \
            isinstance(self._variables['WrappedAction'],  WorkflowActionType):            
            #set workflow bridge to special wrapper action bridge
            self._set_bridge(self.bridge)
            self.bridge.action_checkable = False
            self._variables['WrappedAction'].set_config(Inputs=[self.bridge])
            self._variables['WrappedAction']._inicialize()
            self._hash.update(bytes(self._variables['WrappedAction']._get_hash(), "utf-8"))
 
    def _check_params(self):    
        """check if all require params is set"""
        err = []
        if self._is_state(ActionStateType.created):
            self._add_error(err, "Inicialize method should be processed before checking")
        if  not 'WrappedAction' in self._variables:
            self._add_error(err, "Parameter 'WrappedAction' is required")
        if len(self._inputs)  != 1:
            self._add_error(err, "Wrapper action requires exactly one input parameter")
        else:
            for input in self._inputs:
                if not isinstance(input, BaseActionType):
                    self._add_error(err, "Parameter 'Inputs' must be BaseActionType")
        return err

    def _get_settings_script(self):    
        """return python script, that create instance of this class"""
        lines = []
        lines.extend(self._variables['WrappedAction']._get_settings_script())
        lines.extend(super(WrapperActionType, self)._get_settings_script())
        return lines

    def _get_hashes_list(self):
        """return list of store_id->hash this and nested actions"""
        ret = super()._get_hashes_list()
        ret.update(self._variables['WrappedAction']._get_hashes_list())
        return ret

    def _set_restore_id(self, identical_list):
        """set restore_id from identical_list"""
        super()._set_restore_id(identical_list)
        self._variables['WrappedAction']._set_restore_id(identical_list)

    def get_resources(self):
        """Return list of resource files"""
        return self._variables['WrappedAction'].get_resources()


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
    def _order_child_list(cls, actions, inputs=[]):
        """
        return ordered list from actions. If all dependencies is not
        in list, raise exception. First action in list must be one of 
        end actions. If list is partly ordered, function is faster
        """
        last_count = 0
        ordered_action=[]
        while len(actions)>0:
            if last_count==len(actions):
                raise Exception("All Dependencies aren't in list")
            last_count=len(actions)
            for i in reversed(range(len(actions))):
                if cls._check_action_dependencies(actions[i], ordered_action, inputs):
                    ordered_action.insert(0, actions.pop(i))
                    break
        return ordered_action  

    @staticmethod 
    def _get_action_list(action, stop_action=None, must_has_stop=True):
        """
        get not-ordered list of dependent action. If stop 
        action is set, list end in this action, and not continue
        to action in stop action inputs. If stop action is not 
        found, emty list is returned.
        """
        before_end = stop_action is None or not must_has_stop
        actions=[action]
        if stop_action and action == stop_action: 
            stop_action = None
            before_end = True
        process=[]
        while True: 
            for action_next in action._inputs:
                if stop_action and action_next==stop_action:
                    before_end=True
                    continue
                if action_next in actions:
                    continue
                if isinstance(action_next, Bridge):
                    continue
                process.append(action_next)
                actions.append(action_next)
            if len(process)==0:
                if not before_end:
                    # error, action end action not defined
                    return []
                if stop_action is not None and action != stop_action:
                    actions.append(stop_action)
                break
            action=process.pop(0)
        return actions

    @staticmethod 
    def _merge_actions_lists(list1, list2):
        """
        add unique items from list2 to end of list1 
        """
        for action in list2:
            if action in list1:
                continue
            else:
                list1.append(action)
        return list1

    @staticmethod
    def _check_action_dependencies(action, list, inputs):
        """check if all direct dependecies is in set action list"""
        for dep_action in action._inputs:
            if isinstance(dep_action, Bridge):
                if not dep_action.check_action(inputs):
                    return False
            else:
                if dep_action not in list and dep_action not in inputs:
                    return False
        return True
        
    def _check_params(self):           
        """check if all require params is set"""
        err = []
        if self._is_state(ActionStateType.created):
            self._add_error(err, "Inicialize method should be processed before checking")
        if  'ResultActions' in self._variables:
            if not isinstance(self._variables['ResultActions'], list):
                self._add_error(err, "Parameter 'ResultActions' must be list of output actions")
            else:
                for i in range(0, len(self._variables['ResultActions'])):
                    if not isinstance(self._variables['ResultActions'][i],  BaseActionType):
                        self._add_error(err, "Type of parameter 'ResultActions[{0}]' must be BaseActionType".format(str(i)))
        return err  
       
    @staticmethod
    def _is_independent(action):
        """check if all direct dependecies is in set action list"""
        for dep_action in action._inputs:
            if not dep_action._is_state(ActionStateType.finished):
                return False
        return True
     
    @staticmethod
    def _will_be_independent(action):
        """check if all direct dependecies is in set action list"""
        for dep_action in action._inputs:
            if not dep_action._is_state(ActionStateType.processed) and \
                not dep_action._is_state(ActionStateType.finished):
                return False
        return True
 
    def _set_storing(self, identical_list):
        """set restore id"""
        super(WorkflowActionType, self)._set_storing(identical_list)
        actions = self._get_child_list()
        for action in actions:
            action._set_storing(identical_list)

 
    def _plan_action(self, path):
        """
        If next action can be panned, return processed state and 
        this action, else return processed state and null        
        """
        if  self.__processed_actions is None:
            self.__processed_actions =self._get_child_list()
        if len(self.__processed_actions) == 0:
            self._set_state(ActionStateType.finished)
            return ActionRunningState.finished, self
        if self.__next_action>=len(self.__processed_actions):
            self.__next_action = 0
        start_action = self.__next_action
        all_dependent = True
        while True:
            if self._is_independent(self.__processed_actions[self.__next_action]):
                all_dependent = False
                state, action = self.__processed_actions[self.__next_action]._plan_action(path)
                if state is ActionRunningState.finished:
                    if action._restore_id is None and self._restore_id is not None:
                        # action can't be restored, all next action will be processed
                        self._restore_id = None
                        for rest_action in self.__processed_actions:
                            rest_action._restore_id = None
                    del self.__processed_actions[self.__next_action]                    
                    return ActionRunningState.repeat, None
                if state is ActionRunningState.repeat:
                    return state, action
                if state is ActionRunningState.error:
                    return state, action 
                if state is ActionRunningState.wait and action is not None:
                    self.__next_action += 1
                    return state, action
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

    def _get_hashes_list(self):
        """return list of store_id->hash this and nested actions"""
        ret = super()._get_hashes_list()
        for action in self._get_child_list():
            ret.update(action._get_hashes_list())
        return ret

    def _set_restore_id(self, identical_list):
        """set restore_id from identical_list"""
        super()._set_restore_id(identical_list)
        for action in self._get_child_list():
            action._set_restore_id(identical_list)

    def get_resources(self):
        """Return list of resource files"""
        ret = []
        for action in self._get_child_list():
            ret.extend(action.get_resources())
        return ret
