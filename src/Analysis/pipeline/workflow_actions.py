from .action_types import WorkflowActionType, ActionStateType, BaseActionType, Bridge, WrapperActionType

class Workflow(WorkflowActionType):
    _name = "Workflow"
    """Display name of action"""
    _description = "Series of action"
    """Display description of action"""

    def __init__(self, **kwargs):
        """
        Class for actions grouping.      
        :param BaseActionType InputAction: Action that is enter to workflow 
            is set by set_output_action after class defination 
        :param BaseActionType OutputAction: Action that is exit from workflow
            is set by set_output_action after class defination
        :param list of BaseActionType ResultActions: Action that is blined , that created
            pipeline side effects (result)
        is set by set_output_action after class defination
        :param BaseActionType Inputs: This variable is input action,
            for direct link to previous action, or may be omited for using in
            wrapper action
        """
        super(Workflow, self).__init__(**kwargs)
        self.bridge = Bridge(self)
        """link to bridge class"""
        self._actions=[]
        """action list sorted in order by creation time"""
      
    def input(self):
        """ Return input type"""
        return self.bridge
       
    def _get_child_list(self):
        """check outputAction variable and get list of child actions"""
        actions = []
        if 'OutputAction' in self._variables and \
            isinstance(self._variables['OutputAction'],  BaseActionType) and \
            'InputAction' in self._variables and \
            isinstance(self._variables['InputAction'],  BaseActionType):
            actions = self._get_action_list(self._variables['OutputAction'], self._variables['InputAction'])        
        if 'ResultActions' in self._variables and \
            isinstance(self._variables['ResultActions'], list) and \
            len(self._variables['ResultActions'])>0 and \
            isinstance(self._variables['ResultActions'][0],  BaseActionType) and \
           'InputAction' in self._variables and \
            isinstance(self._variables['InputAction'],  BaseActionType):
            for i in range(1, len(self._variables['ResultActions'])):
                if isinstance(self._variables['ResultActions'][i], BaseActionType):
                    actions2 = self._get_action_list(self._variables['ResultActions'][i], self._variables['InputAction'])
                    actions=self._merge_actions_lists(actions, actions2)
        return actions

    def _inicialize(self):
        """inicialize action run variables"""
        if self._get_state().value > ActionStateType.initialized.value:
            return
        # set state before recursion, inicialize ending if return to this action
        self._set_state(ActionStateType.initialized)
        actions = self._get_child_list()
        self._process_base_hash()
        try:
            actions  = self._order_child_list(actions)
            actions.reverse()
            for action in actions:
               action._inicialize()
               self._hash.update(bytes(action._get_hash(), "utf-8"))
            self._actions = sorted(actions , key=lambda item: item._id)
        except Exception as err:
            self._load_errs.append("Inicialize child workflow action error ({0})".format(err))   
        if  len(self._inputs)==1:
            self.bridge._set_new_link(self._inputs[0])
                    
    def _get_settings_script(self):    
        """return python script, that create instance of this class"""
        lines = super(Workflow, self)._get_settings_script()
        list = self._actions
        names=['OutputAction', 'InputAction']
        values=[
                ["{0}".format(self._variables['OutputAction']._get_instance_name())], 
                ["{0}".format(self._variables['InputAction']._get_instance_name())]
            ]
        for action in list:
            lines.extend(action._get_settings_script())
        if 'ResultActions' in self._variables and len(self._variables['ResultActions'])>0:
            names.append('ResultActions')
            value = '['
            for action in self._variables['ResultActions']:
                value += "{0},".format(action._get_instance_name())
            value = value[:-1]+"]"
            values.append([value])
        lines.extend(self._format_config_to_setter(names, values))
        return lines

    def _get_output(self):
        """return output relevant for set action"""
        if 'OutputAction' in self._variables and \
            isinstance(self._variables['OutputAction'],  BaseActionType):
            return self._variables['OutputAction']._get_output()
        return None

    def _check_params(self):    
        """check if all require params is set"""
        err = super(Workflow, self)._check_params()
        if len(self._inputs)  != 1:
            if len(self._inputs)>1 or self.bridge._link is None:
                err.append("Workflow action requires exactly one input parameter")
        else:
            for input in self._inputs:
                if not isinstance(input, BaseActionType):
                    err.append("Parameter 'Inputs' ({0}) must be BaseActionType".format(
                        self.name))        
        if  not 'InputAction' in self._variables:
            err.append("Parameter 'InputAction' is require")
        else:            
            if not isinstance(self._variables['InputAction'],  BaseActionType):
                err.append("Parameter 'InputAction' must be BaseActionType") 
            else:
                # during inicialiyation should be processed all chain action
                if self._variables['InputAction'] is ActionStateType.created:
                    err.append("Inicialization of 'InputAction' is not processed. Is all workflow actions chained?") 
        if  not 'OutputAction' in self._variables:
            err.append("Parameter 'OutputAction' is require")
        else:
            if not isinstance(self._variables['OutputAction'],  BaseActionType):
                err.append("Parameter 'OutputAction' must be BaseActionType")
                
        return err
        
    def validate(self):    
        """validate variables, input and output"""
        err = super(Workflow, self).validate()
        actions = self._get_child_list()        
        actions  = self._order_child_list(actions)
        for action in actions:
            err.extend(action.validate())
        return err
        
    def _reset_storing(self, template, iden):
        """
        Constract store and restore id from template action ids and index
        this action in  parent wrapper action. This indexes will be unique and
        equal for repeating processing
        """
        self._store_id = template._store_id + iden
        if template._restore_id is not None:
            self._restore_id = template._restore_id + iden
        for i in range(0, len(self._actions)):
            if len(template._actions)>i:
                self._actions[i]._store_id = template._actions[i]._store_id + iden
                if template._actions[i]._restore_id is not None:
                    self._actions[i]._restore_id = template._actions[i]._restore_id + iden
                if isinstance(self._actions[i], WrapperActionType):
                    self._index_iden = iden
