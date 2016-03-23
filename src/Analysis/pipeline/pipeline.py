from .action_types import WorkflowActionType, ActionStateType, BaseActionType

class PipelineResult(WorkflowActionType):
    def __init__(self, action, output):
        self.action=action
        """Action determine downloading output"""
        self.output=output
        """downloading output id"""

class Pipeline(WorkflowActionType):
    _name = "Pipeline"
    """Display name of action"""
    _description = "Group of all actions"
    """Display description of action"""

    def __init__(self, **kwargs):
        """
        Class for group of all actions, that. Piplane has not
        any input action, and least one output action. Outputs
        action define action contained in pipeline. Otpust action
        would be actions, theirs results will be downloaded
        :param array of BaseActionType OutputActions: Action that is exit from pipeline
        :param BaseActionType Input: This variable is ignore
        :param object Output: This variable is ignore, during inicialize
            is set accoding OutputAction's outputs
        :param array of PipelineResult: Action that is exit from pipeline
        """
        super(Pipeline, self).__init__(**kwargs)
        
    def inicialize(self):
        """inicialize action run variables"""
        if self.state.value > ActionStateType.initialized.value:
            return
        # set state before recursion, inicialize ending if return to this action
        self.state = ActionStateType.initialized
        if 'OutputAction' in self.variables and \
            isinstance(self.variables['OutputAction'],  BaseActionType) and \
            'InputAction' in self.variables and \
            isinstance(self.variables['InputAction'],  BaseActionType):
            actions = self._get_action_list(self.variables['OutputAction'], self.variables['InputAction'])
            try:
                actions  = self._order_child_list(actions)
                actions.reverse()
                for action in actions:
                   action.inicialize()
            except:
                pass    
        if  'InputAction' in self.variables and \
            isinstance(self.variables['InputAction'],  BaseActionType):
            self.inputs=[]
            for input in self.variables['InputAction'].inputs:
                    self.inputs.append(input)

    def get_output(self, action, number):
        """return output relevant for set action"""
        if number>0:
            return None
        if 'OutputAction' in self.variables and \
            isinstance(self.variables['OutputAction'],  BaseActionType):
            return self.variables['OutputAction'].get_output(self, 0)
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
                if self.variables['InputAction'] is ActionStateType.created:
                    err.append("Inicializatin of 'InputAction' is not processed. Is all workflow actions chained?") 
        if  not 'OutputAction' in self.variables:
            err.append("Parameter 'OutputAction' is require")
        else:
            if not isinstance(self.variables['OutputAction'],  BaseActionType):
                err.append("Parameter 'OutputAction' must be BaseActionType")
        return err
        
    def validate(self):    
        """validate variables, input and output"""
        err = self._check_params()
        err.extend(self._check_params())
        if 'OutputAction' in self.variables and \
            isinstance(self.variables['OutputAction'],  BaseActionType):            
            if  'InputAction' in self.variables and \
                isinstance(self.variables['InputAction'],  BaseActionType):
                actions = self._get_action_list(self.variables['OutputAction'], self.variables['InputAction'])
                for action in actions:
                    err.extend(action.validate())
            else:
                err.extend(self.variables['OutputAction'].validate())
        return err
        
    def _get_child_list(self):
        """Get list of child action, ordered by input-output dependency"""
        if  'OutputAction'not in self.variables or \
            not isinstance(self.variables['OutputAction'],  BaseActionType):
            return None
        if  'InputAction' not in self.variables or \
            not isinstance(self.variables['InputAction'],  BaseActionType):
            return None
        if self.variables['OutputAction']==self.variables['InputAction']:
            return [self.variables['OutputAction']]
        actions = self._get_action_list(self.variables['OutputAction'], self.variables['InputAction'])
        try:
            actions  = self._order_child_list(actions)
        except:
            return None
        return actions
        
    def get_settings_script(self):    
        """return python script, that create instance of this class"""
        list = self._get_child_list()
        lines=[]
        list.reverse()
        for action in list:
            lines.extend(action.get_settings_script())
        lines.extend(super(Workflow, self).get_settings_script())
        return lines
        
    def _get_variables_script(self):
        """return array of variables python scripts"""
        var = super(Workflow, self)._get_variables_script()
        if  'InputAction' in self.variables and \
                isinstance(self.variables['InputAction'],  BaseActionType):
            var.append(["InputAction={0}".format(self.variables['InputAction'].get_instance_name())])
        if  'OutputAction' in self.variables and \
                isinstance(self.variables['OutputAction'],  BaseActionType):
            var.append(["OutputAction={0}".format(self.variables['OutputAction'].get_instance_name())])
        return var
