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
        :param list of BaseActionType ResultActions: Action that is blined , that created
            pipeline side effects (result)
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
        actions = self._get_child_list()
        try:
            actions  = self._order_child_list(actions)
            actions.reverse()
            for action in actions:
               action.inicialize()
        except:
            pass    

    def get_output(self, number):
        """return output relevant for set action"""
        if isinstance(self.variables['ResultActions'][number],  BaseActionType):
            return self.variables['ResultActions'][number].get_output(self)
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
        err = super(Pipeline, self)._check_params()
        if  not 'ResultActions' in self.variables:
            err.append("Parameter 'ResultActions' is require for pipeline")
        elif isinstance(self.variables['ResultActions'], list):
            err.append("Parameter 'ResultActions' must be list of output actions")
        elif len(self.variables['ResultActions'], list)<1:
            err.append("Parameter 'ResultActions' must contains least one action")
        else:
            for i in range(0, len(self.variables['ResultActions'], list)):
                if not isinstance(self.variables['ResultActions'],  BaseActionType):
                    err.append("Type of parameter 'ResultActions[{0}]'  must be BaseActionType".format(str(i)))                    
        return err
        
    def validate(self):    
        """validate variables, input and output"""
        err = super(Pipeline, self).validate()
        err.extend(self._check_params())
        # existence of output params is make in _get_child_list
        actions = self._get_child_list()            
        for action in actions:
            err.extend(action.validate())
        return err
        
    def _get_child_list(self):
        """check outputAction variable and get list of child actions"""
        actions = []
        if 'ResultActions' in self.variables and \
            isinstance(self.variables['ResultActions'], list) and \
            len(self.variables['ResultActions'])>0 and \
            isinstance(self.variables['ResultActions'][0],  BaseActionType):            
            actions = self._get_action_list(self.variables['ResultActions'][0])
            for i in range(1, len(self.variables['ResultActions'])):
                if isinstance(self.variables['ResultActions'][i], BaseActionType):
                    actions2 = self._get_action_list(self.variables['ResultActions'][i])
                    actions=self._merge_actions_lists(actions, actions2)
        return actions
        
    def get_settings_script(self):    
        """return python script, that create instance of this class"""
        list = self._get_child_list()
        lines=[]
        list.reverse()
        for action in list:
            lines.extend(action.get_settings_script())
        lines.extend(super(Pipeline, self).get_settings_script())
        return lines
        
    def _get_variables_script(self):
        """return array of variables python scripts"""
        var = super(Pipeline, self)._get_variables_script()        
        if 'ResultActions' in self.variables and \
            isinstance(self.variables['ResultActions'], list) and \
            len(self.variables['ResultActions'])>0:
            array = 'ResultActions=['
            first = True
            for out in self.variables['ResultActions']:
                if isinstance(out,  BaseActionType):            
                    if first:
                        first = False
                    else:
                        array += ", "
                    array += out.get_instance_name()                    
            var.append([array+']'])
        # ToDo PipelineResult
        return var
