from .action_types import ConnectorActionType, ActionStateType

class Connector(ConnectorActionType):
    
    _name = "Conn"
    """Display name of action"""
    _description = "Convertor for base variable manipulation"
    """Display description of action"""  

    def __init__(self, **kwargs):
        """
        :param Convertor Convertor: Convertor output defination
        """        
        super(Connector, self).__init__(**kwargs)
        if 'Convertor' not in self._variables: 
            self._variables['Convertor'] = None
       
    def duplicate(self):
        """Duplicate convertor. Returned convertor is not inicialized and checked"""
        new = Connector()
        #set Convertor
        new._variables['Convertor'] = self._variables['Convertor']
        #duplicate inputs
        for input in self._inputs:
            new._inputs.append(input)
        new._set_state(ActionStateType.created)
        return new
 
    def _check_params(self):    
        """check if all require params is set"""
        err = super(Connector, self)._check_params()

        if 'Convertor' not in self._variables or self._variables['Convertor'] is None:
            self._add_error(err, "Convertor parameter is not set")
        else:
            self._extend_error(err, self._variables['Convertor']._check_params(self._inputs))
        return err
    
    def validate(self):
        """validate variables, input and output"""
        err = super(Connector, self).validate()
        return err
    
    def _get_runner(self, params):
        """
        return Runner class with process description
        """    
        return None
    
    def _inicialize(self):
        """inicialize action run variables"""
        try:
            self._output = self._variables['Convertor']._get_output(self._inputs) 
        except Exception as err:
            self._load_errs.append(str(err))
        self._set_state(ActionStateType.initialized)
        self._process_base_hash()
        if 'Convertor' in self._variables:
            self._hash.update(bytes(self._variables['Convertor']._get_unique_text(), "utf-8"))        

    def _update(self):    
        """
        Process action on client site and return None or prepare process 
        environment and return Runner class with  process description if 
        action is set for externall processing.        
        """
        try:
            self._output = self._variables['Convertor']._get_output(self._inputs) 
        except Exception as err:
            self._load_errs.append(str(err))
        return self._get_runner(None)
        
    def _get_settings_script(self):    
        """return python script, that create instance of this class"""
        lines = []
       
        lines.extend(self._variables['Convertor']._get_settings_script())
        lines.extend(super(Connector, self)._get_settings_script())
        return lines
        
    def _get_variables_script(self):
        """return array of variables python scripts"""
        var = super(Connector, self)._get_variables_script()        
        if 'Convertor' in self._variables:
            wrapper = 'Convertor={0}'.format(self._variables['Convertor']._get_instance_name())                   
            var.append([wrapper])
        return var    
