from .action_types import WorkflowActionType, ActionStateType, BaseActionType, Bridge

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
        :param BaseActionType Input: This variable is input action,
            for direct link to previous action, or may be omited for using in
            wrapper action
        :param object Output: This variable is ignore, during inicialize
            is set accoding OutputAction's outputs
        """
        super(Workflow, self).__init__(**kwargs)
        self.bridge = Bridge(self)
        """link to bridge class"""
      
    def input(self):
        """ Return input type"""
        return self.bridge
       
    def _get_child_list(self):
        """check outputAction variable and get list of child actions"""
        actions = []
        if 'OutputAction' in self.variables and \
            isinstance(self.variables['OutputAction'],  BaseActionType) and \
            'InputAction' in self.variables and \
            isinstance(self.variables['InputAction'],  BaseActionType):
            actions = self._get_action_list(self.variables['OutputAction'], self.variables['InputAction'])        
        if 'ResultActions' in self.variables and \
            isinstance(self.variables['ResultActions'], list) and \
            len(self.variables['ResultActions'])>0 and \
            isinstance(self.variables['ResultActions'][0],  BaseActionType) and \
           'InputAction' in self.variables and \
            isinstance(self.variables['InputAction'],  BaseActionType):
            for i in range(1, len(self.variables['ResultActions'])):
                if isinstance(self.variables['ResultActions'][i], BaseActionType):
                    actions2 = self._get_action_list(self.variables['ResultActions'][i], self.variables['InputAction'])
                    actions=self._merge_actions_lists(actions, actions2)
        return actions

    def inicialize(self):
        """inicialize action run variables"""
        if self.state.value > ActionStateType.initialized.value:
            return
        # set state before recursion, inicialize ending if return to this action
        self.state = ActionStateType.initialized
        actions = self._get_child_list()
        try:
            actions  = self._order_child_list(actions)
            actions.reverse()
            for action in actions:
               action.inicialize()
        except:
            pass    
        if  len(self.inputs)==1:
            self._set_bridge(self.variables['Inputs'][0])            
                    
    def get_settings_script(self):    
        """return python script, that create instance of this class"""
        lines = super(Workflow, self).get_settings_script()
        list = self._get_child_list()
        list.reverse()
        names=['OutputAction', 'InputAction']
        values=[
                ["{0}".format(self.variables['OutputAction'].get_instance_name())], 
                ["{0}".format(self.variables['InputAction'].get_instance_name())]
            ]
        for action in list:
            lines.extend(action.get_settings_script())
        if 'ResultActions' in self.variables and len(self.variables['ResultActions'])>0:
            names.append('ResultActions')
            value = '['
            for action in self.variables['ResultActions']:
                value += "{0},".format(action.get_instance_name())
            value = value[:-1]+"]"
            values.append([value])
        lines.extend(self._format_config_to_setter(names, values))
        return lines

    def get_output(self):
        """return output relevant for set action"""
        if 'OutputAction' in self.variables and \
            isinstance(self.variables['OutputAction'],  BaseActionType):
            return self.variables['OutputAction'].get_output()
        return None

    def _get_runner(self, params):    
        """
        return Runner class with process description
        """        
        return None
        
    def run(self):    
        """
        Process action on client site or prepare process environment and 
        return Runner class with  process description or None if action not 
        need externall processing.
        """
        return  self._get_runner(None)        

    def _check_params(self):    
        """check if all require params is set"""
        err = super(Workflow, self)._check_params()
        if  not 'InputAction' in self.variables:
            err.append("Parameter 'InputAction' is require")
        else:            
            if not isinstance(self.variables['InputAction'],  BaseActionType):
                err.append("Parameter 'InputAction' must be BaseActionType") 
            else:
                # during inicialiyation should be processed all chain action
                if len(self.variables['InputAction'])!=1:
                    err.append("Workflow require 'InputAction' with exactly one input parameter.") 
                if self.variables['InputAction'] is ActionStateType.created:
                    err.append("Inicialization of 'InputAction' is not processed. Is all workflow actions chained?") 
        if  not 'OutputAction' in self.variables:
            err.append("Parameter 'OutputAction' is require")
        else:
            if not isinstance(self.variables['OutputAction'],  BaseActionType):
                err.append("Parameter 'OutputAction' must be BaseActionType")
        return err
        
    def validate(self):    
        """validate variables, input and output"""
        err = super(Workflow, self).validate()
        err.extend(self._check_params())
        actions = self._get_child_list()
        for action in actions:
            err.extend(action.validate())
        return err
        

