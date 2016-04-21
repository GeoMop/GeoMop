from .action_types import InputType
from .generic_tree import GDTT, GDTTFunc
from .code_formater import Formater

class Predicate(InputType):
    """Class for filter defination"""
    _name = "Predicate"
    """Display name of action"""
    _description = "Predicate"
    """Display description of action"""  
        
    def __init__(self, **kwargs):
        """
        :param  GDTT DefInput: Convertor template may contain 
            GDTT types for checking. when is set real input, input typ is compare
            with this parameter
        :param GDTTFunc DefOutput: Define output from predicator. Output can contain
            DTT types, their functions, logic operators and inputs. (self.input[0], self.input[1], ...)
            result for select should be boolean
        """
        super(Predicate, self).__init__(**kwargs)
        
    def set_config(self, **kwargs):
        """set action config variables"""
        if "DefInput" in kwargs:
            kwargs["DefInputs"]=[kwargs["DefInput"]]
            del kwargs["DefInput"]
        super(Predicate, self).set_config(**kwargs)
        
    def _check_params(self):    
        """check if all require params is set"""
        err = []
        if len(self._variables['DefInputs']) != 1:
            err.append("Predicate requires 'DefInput' parameter")        
        else:
            if not isinstance(self._variables['DefInputs'][0], GDTT):
                err.append("Parameter 'DefInput' ({0}) GDTT".format(
                        self.name))        
        if 'DefOutput' not in self._variables:
            err.append("Predicator require DefOutput parameter")
        else:
            if not isinstance(self._variables['DefOutput'], GDTTFunc):
                err.append("Convertor parameter 'DefOutput' must be GDTTFunc")
        return err
        
    def _get_variables_script(self):    
        """return array of variables python scripts"""
        var = super( InputType, self)._get_variables_script()
        script=self._variables['DefInputs'][0]._get_main_settings_script()
        lines = Formater.format_variable('DefInput', script,0)
        lines[-1] = lines[-1][:-1]        
        var.append(lines)        
        return var
    
    def input(self, i):
        """Function for generic input defination"""
        if len(self._inputs)>i:
            # predicator input is structure
            return self._inputs[i]
        return super(Predicate, self).input(i)


    def validate(self):
        """
        validate variables and output, input is set in function that use predicator and 
        is not validate in this phase,        
        """
        err = super(Predicate, self).validate()
        return err
        
    def _inicialize(self):
        """
        Predicate is make so that not need this function becose inputs is change during
        using this class, and result is return after each set by process funcion
        """
        pass
        
    def process(self, input):
        """use predicate"""
        self.set_inputs([input])
        self.set_output()
        return self._get_output()
        
    def get_key(self, input):
        """return output suitable for sorte function"""
        return self.process(input)
        
        
    def get_bool(self, input):
        """return output suitable for select function"""
        return self.process(input)

    def _get_runner(self, params):    
        return None
        
    def _run(self):    
        return  self._get_runner(None) 
