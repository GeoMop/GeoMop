from .action_types import WorkflowActionType, ActionStateType, BaseActionType

class Workflow(WorkflowActionType):
    _name = "Workflow"
    """Display name of action"""
    _description = "Series of action"
    """Display description of action"""

    def __init__(self, **kwargs):
        """
        Class for actions grouping.      
        :param BaseActionType InputAction: Action that is enter to workflow
        :param BaseActionType OutputAction: Action that is exit from workflow
        :param BaseActionType Input: This variable is ignore, during inicialize
            is set accoding InputAction
        :param object Output: This variable is ignore, during inicialize
            is set accoding OutputAction's outputs
        """
        super(Workflow, self).__init__(**kwargs)
        
    def inicialize(self):
        """inicialize action run variables"""
        if self.state.value > ActionStateType.initialized.value:
            return
        # set state before recursion, inicialize ending if return to this action
        self.state = ActionStateType.initialized
        if  'OutputAction' in self.variables and \
            isinstance(self.variables['OutputAction'],  BaseActionType):
                self.variables['OutputAction'].inicialize()
                self.outputs=[]
                for output in self.variables['OutputAction'].outputs:
                    self.outputs.append(output)
        if  'InputAction' in self.variables and \
            isinstance(self.variables['InputAction'],  BaseActionType):
            self.inputs=[]
            for input in self.variables['InputAction'].inputs:
                    self.inputs.append(input)

    def get_output(self, number):
        """return output relevant for set action"""
        if number>0:
            return None
        return self.outputs[0].get_output(0)

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
        err = super(Workflow, self).validate()
        err.extend(self._check_params())
        if 'OutputAction' in self.variables and \
            isinstance(self.variables['OutputAction'],  BaseActionType):
            err.extend(self.variables['OutputAction'].validate())
        return err
