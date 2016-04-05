from .action_types import ConvertorActionType, ActionStateType
from .generic_tree import GDTT
from .code_formater import Formater

class CommonConvertor(ConvertorActionType):
    
    _name = "CommonConvertor"
    """Display name of action"""
    _description = "Convertor for base variable manipulation"
    """Display description of action"""  

    def __init__(self, **kwargs):
        """
        :param BaseAction or GDTT DefInputs: Convertor template may have 
            GDTT types for checking. when is set real input, input typ is compare
            with this parameter
        :param DTT output: Define output from convertor. Output can contain
            DTT types, their functions and inputs. (self.input[0], self.input[1], ...)
        """
        super(CommonConvertor, self).__init__(**kwargs)
        if 'DefInputs' not in self.variables:
            self.variables['DefInputs']=[]
        for i in range(0, len(self.variables['DefInputs'])):
            self.variables['DefInputs'][i].set_path("input({0})".format(str(i)))
       
    def inicialize(self):
        """inicialize action run variables"""
        if self.state.value > ActionStateType.created.value:
            return            
        self.state = ActionStateType.initialized

    def input(self, i):
        while len(self.variables['DefInputs'])<=i:
            attr = GDTT()
            attr.set_path("{0}.input({1})".format(self.get_instance_name(), str(i)))
            self.variables['DefInputs'].append(attr)
        return self.variables['DefInputs'][i]
        
    def _get_variables_script(self):    
        """return array of variables python scripts"""
        var = super(CommonConvertor, self)._get_variables_script()
        script = self.variables['Output'].get_settings_script()
        lines=["Output=("]
        lines.extend(Formater.indent(script, 4))
        lines.append(")")
        var.append(lines)        
        return var
        
    def set_config(self, **kwargs):
        """set action config variables"""
        for name, value in kwargs.items():
            if name == 'Inputs':
                self.set_inputs(value)
            else:
                self.variables[name] = value
        
    def _check_params(self):    
        return []
    
    def validate(self):
        return []
    
    def _get_runner(self, params):    
        return None
        
    def run(self):    
        return  self._get_runner(None)
