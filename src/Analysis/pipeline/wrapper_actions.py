from .action_types import WrapperActionType, ActionStateType, BaseActionType, ActionsStatistics, ActionRunningState
from .data_types_tree import Ensemble, DTT
from .generator_actions import VariableGenerator
from .workflow_actions import Workflow

class ForEach(WrapperActionType):
    
    _name = "ForEach"
    """Display name of action"""
    _description = "Cyclic action processor"
    """Display description of action"""  

    def __init__(self, **kwargs):
        """
       Class for cyclic action processing.      
        :param BaseActionType WrappedAction: Wrapped action
        :param Ensemble Output: This variable is compute  from outputs
            WrappedAction and placed in Ensemble
        :param Ensemble Input: Composite of WrappedAction cyclic  inputs, 
            this parameter is set after declaration this action by function
           set_wrapped_action 
        """
        self._wa_instances=[]
        """
        Set wrapper class serve only as template, for run is make
        copy of this class. The variable is for the copies.
        """
        self._procesed_instances = 0
        """How many instances is procesed"""
        super(ForEach, self).__init__(**kwargs)        

    def _set_bridge(self, bridge):
        """redirect bridge to wrapper"""
        bridge._set_new_link(self, self._get_output_to_wrapper)

    def _inicialize(self):
        """inicialize action run variables"""
        super(ForEach, self)._inicialize()
        self.__make_output()

    def _get_output_to_wrapper(self):
        """return output relevant for wrapper action"""
        if 'WrappedAction' in self._variables and \
            isinstance(self._variables['WrappedAction'],  BaseActionType):
            # for wraped action return previous input
            ensemble = self.get_input_val(0)
            if isinstance(ensemble,  Ensemble):
                return ensemble.subtype
        return None

    def __make_output(self):
        """return output relevant for set action"""
        if 'WrappedAction' in self._variables and \
            isinstance(self._variables['WrappedAction'],  BaseActionType):
            output=self._variables['WrappedAction']._get_output()
            if not isinstance(output, DTT):    
                return None
            res=Ensemble(output)
            if not self._is_state(ActionStateType.finished):
                for instance in self._wa_instances:
                    """Running instance, get input from generator"""
                    res.add_item(instance._get_output())
            self._output = res
        
    def _get_variables_script(self):
        """return array of variables python scripts"""
        var = super(ForEach, self)._get_variables_script()        
        if 'WrappedAction' in self._variables:
            wrapper = 'WrapperActions={0}'.format(self._variables['WrappedAction']._get_instance_name())                   
            var.append([wrapper])
        return var
        
    def _set_storing(self, identical_list):
        """set restore id"""
        super(ForEach, self)._set_storing(identical_list)
        if 'WrappedAction' in self._variables:
            self._variables['WrappedAction']._set_storing(identical_list)

    def _plan_action(self, path):
        """
        If next action can be panned, return processed state and 
        this action, else return processed state and null        
        """
        if self._is_state(ActionStateType.processed):
            return ActionRunningState.wait,  None
        if self._is_state(ActionStateType.finished):            
            return ActionRunningState.finished,  self
        if len( self._wa_instances)==0:
            if self._restore_id is not None:
                # restoring - set processed state as in classic action                
                if self._is_state(ActionStateType.processed):
                    return ActionRunningState.wait,  None                        
                self._restore_results(path)
                if self._restore_id is not None:
                    self._set_state(ActionStateType.processed)
                    # send as short action for storing and settings state
                    return ActionRunningState.repeat,  self
            ensemble = []
            for i in range(0, len(self._inputs)):
                ensemble.append(self.get_input_val(i))
            if len(ensemble[0])== 0:
                return ActionRunningState.error,  \
                    ["Empty Ensemble in ForEach input"]
            for i in range(0, len(ensemble[0]._list)):
                inputs = []
                for j in range(0, len(self._inputs)):
                    if len(ensemble[j])<=i:
                        return ActionRunningState.error,  \
                            ["Ensamble in Input({0}) has less items".format(str(i))]
                    gen = VariableGenerator(Variable=ensemble[j]._list[i])
                    gen._inicialize()
                    gen._update()
                    gen._after_update(None)
                    if self._inputs[j]._restore_id is not None:
                        # input is restored => mark generator as restored
                        gen._set_restored()
                    inputs.append(gen) 
                name = self._variables['WrappedAction']._get_instance_name()
                script = self._variables['WrappedAction']._get_settings_script()
                script.insert(0, "from pipeline import *")
                script = '\n'.join(script)
                script = script.replace(name, "new_dupl_workflow")
                exec (script, globals())
                self._wa_instances.append(new_dupl_workflow)
                self._wa_instances[-1].set_inputs(inputs)
                self._wa_instances[-1]._inicialize()
                self._wa_instances[-1]._reset_storing(
                    self._variables['WrappedAction'], self._index_iden +"_"+ str(i)) 
        if self._procesed_instances == len(self._wa_instances):
            for instance in self._wa_instances:
                if not instance._is_state(ActionStateType.finished):
                    return ActionRunningState.wait, None
            self._set_state(ActionStateType.processed)
            return ActionRunningState.repeat, self
        next_wa = self._procesed_instances
        while next_wa < len(self._wa_instances):    
            state, action = self._wa_instances[next_wa]._plan_action(path)
            if state is ActionRunningState.finished:
                if next_wa == self._procesed_instances:
                    self._procesed_instances += 1
                return ActionRunningState.wait, action
            if state is ActionRunningState.repeat:
                return state, action
            if state is ActionRunningState.error:
                return state, action
            if state is ActionRunningState.wait and action is not None:
                return ActionRunningState.repeat, action
            # run return wait, try next
            next_wa += 1            
        return  ActionRunningState.wait, None

    def _after_update(self, store_dir):    
        """
        Set real output variable and set finished state.
        """
        self.__make_output()
        self._store_results(store_dir)
        self._set_state(ActionStateType.finished)

    def _check_params(self):    
        """check if all require params is set"""
        err = super(ForEach, self)._check_params()
        if len(self._inputs) == 0:
            self._add_error(err, "No input action for ForEach")
        if  'WrappedAction' in self._variables:            
            if not isinstance(self._variables['WrappedAction'],  Workflow):
                self._add_error(err, "Parameter 'WrappedAction' must be Workflow")
            
        for i in range(0, len(self._inputs)):
            ensemble = self.get_input_val(i)
            if not isinstance(ensemble,  Ensemble):
                self._add_error(err, "Input action {0} not produce Ensemble type variable".format(str(i)))
        return err
        
    def validate(self):    
        """validate variables, input and output"""
        err = super(ForEach, self).validate()
        if 'WrappedAction' in self._variables and \
            isinstance(self._variables['WrappedAction'],  BaseActionType):
            err.extend(self._variables['WrappedAction'].validate())
        return err
        
    def _get_statistics(self):
        """return all statistics for this and child action"""
        stat = self._variables['WrappedAction']._get_statistics()
        number = 0
        if len(self._wa_instances)>0:
            number = len(self._wa_instances)
        else:
            ensemble = self.get_input_val(0)
            number = len(ensemble)
        ret = ActionsStatistics()
        ret.add(stat, number)
        return ret
