from .action_types import InputType
from .generic_tree import GDTT, GDTTFunc

class Predicate(InputType):
    """Class for filter defination"""
    
    def __init__(self, **kwargs):
        """
        :param BaseAction or GDTT DefInputs: Convertor template may have 
            GDTT types for checking. when is set real input, input typ is compare
            with this parameter
        :param GDTTFunc DefOutput: Define output from predicator. Output can contain
            DTT types, their functions, logic operators and inputs. (self.input[0], self.input[1], ...)
            result of this function should be boolean
        """
        super(Predicate, self).__init__(**kwargs)
        
    def _check_params(self):    
        """check if all require params is set"""
        err = []
        for input in self.variables['DefInputs']:
            if not isinstance(input, GDTT):
                err.append("Parameter 'DefInputs' ({0}) must be GDTT".format(
                        self.name))        
        if 'DefOutput' not in self.variables:
            err.append("Predicator require DefOutput parameter")
        else:
            if not isinstance(self.variables['DefOutput'], GDTTFunc):
                err.append("Convertor parameter 'DefOutput' must be GDTTFunc")
        return err
