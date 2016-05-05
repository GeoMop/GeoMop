from .action_types import WrapperActionType, ActionStateType, BaseActionType, ActionsStatistics, ActionRunningState
from .data_types_tree import Ensemble, DTT
from .generator_actions import VariableGenerator

class ForEach(WrapperActionType):
    
    _name = "ForEach"
    """Display name of action"""
    _description = "Cyclic action processor"
    """Display description of action"""  

    def __init__(self, **kwargs):
        """
       Class for cyclic action processing.      
        :param BaseActionType WrappedAction: Wrapped action
        :param Ensemble Output: This variable is ignore,  outputs
            is constructed from WrappedAction and placed in Ensemble
        :param Ensemble Input: Composite of WrappedAction cyclic  inputs, 
            this parameter is set after declaration this action by function
           set_wrapped_action 
        """
        self.wa_instances=[]
        """
        Set wrapper class serve only as template, for run is make
        copy of this class. The variable is for the copies.
        """
        self._procesed_instances
        """How many instances is procesed"""
        super(ForEach, self).__init__(**kwargs)

    def _set_bridge(self, bridge):
        """redirect bridge to wrapper"""
        bridge._set_new_link(self, self._get_output_to_wrapper)

    def _inicialize(self):
        """inicialize action run variables"""
        super(ForEach, self)._inicialize()

    def _get_output_to_wrapper(self):
        """return output relevant for wrapper action"""
        if 'WrappedAction' in self._variables and \
            isinstance(self._variables['WrappedAction'],  BaseActionType):
            # for wraped action return previous input
            ensemble = self.get_input_val(0)
            if isinstance(ensemble,  Ensemble):
                return ensemble.subtype
        return None

    def _get_output(self):
        """return output relevant for set action"""
        if 'WrappedAction' in self._variables and \
            isinstance(self._variables['WrappedAction'],  BaseActionType):
            output=self._variables['WrappedAction']._get_output()
            if not isinstance(output, DTT):    
                return None
            res=Ensemble(output)
            if self._state != ActionStateType.finished:
                for instance in self.wa_instances:
                    """Running instance, get input from generator"""
                    res.add_item(instance._get_output())
            return res
        return None
        
    def _get_variables_script(self):
        """return array of variables python scripts"""
        var = super(ForEach, self)._get_variables_script()        
        if 'WrappedAction' in self._variables:
            wrapper = 'WrapperActions={0}'.format(self._variables['WrappedAction']._get_instance_name())                   
            var.append([wrapper])
        return var

    def _run(self):    
        """
        Process action on client site or prepare process environment and 
        return Runner class with  process description or None if action not 
        need externall processing.
        """
        if self._state == ActionStateType.finished:
            return ActionRunningState.finished,  None
        if len( self.wa_instances)==0:
            ensemble = []
            for i in range(0, len(self._inputs)):
                ensemble.append(self.get_input_val(i))
            if len(ensemble[0])== 0:
                return ActionRunningState.error,  \
                    ["Empty Ensemble in ForEach input"]
            for i in range(0, len(ensemble[0]._list)):
                inputs=[]
                for j in range(0, len(self._inputs)):
                    if len(ensemble[j]._list)<=i:
                        return ActionRunningState.error,  \
                            ["Ensamble in Input({0}) has less items".format(str(i))]
                    inputs.append(VariableGenerator(Variable=ensemble[j]._list[i]))                            
                name = self._variables['WrappedAction']._get_next_instance_name()
                script = self._variables['WrappedAction']._get_settings_script()
                script.insert(0, "from pipeline import *")
                exec ('\n'.join(script), globals())
                self.wa_instances.append(eval(name))
                self.wa_instances[-1].set_inputs(*inputs)
                self.wa_instances[-1]._inicialize()
            self._state = ActionStateType.processed
        if self._procesed_instances == len(self.wa_instances):
            for instance in self.wa_instances:
                if instance._state is not ActionStateType.finished:
                    return ActionRunningState.wait, None
            self._state == ActionStateType.finished
            return ActionRunningState.finished, None
        next_wa = self._procesed_instances   
        while next_wa < len(self.wa_instances):    
            state, runner = self.wa_instances[next_wa]._run()
            if state is ActionRunningState.finished:
                if next_wa == self._procesed_instances:
                    self._procesed_instances += 1
                return ActionRunningState.repeat, runner
            if state is ActionRunningState.repeat:
                return state, runner
            if state is ActionRunningState.error:
                return state, runner
            if state is ActionRunningState.wait and runner is not None:
                return ActionRunningState.repeat, runner
            # run return wait, try next
            next_wa += 1            
        return  ActionRunningState.wait, None        

    def _check_params(self):    
        """check if all require params is set"""
        err = super(ForEach, self)._check_params()
        if len(self._inputs) == 0:
            err.append("No input action for ForEach") 
        for i in range(0, len(self._inputs)):
            ensemble = self.get_input_val(i)
            if not isinstance(ensemble,  Ensemble):
                err.append("Input action {0} not produce Ensemble type variable".format(str(i))) 
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
        stat = self._variables['WrappedAction']._get_statistics
        number = 0
        if len(self.wa_instances)>0:
            number = len(self.wa_instances)
        else:
            ensemble = self.get_input_val(0)
            number = len(ensemble._list)
        ret = ActionsStatistics()
        ret.add(stat, number)
        return
