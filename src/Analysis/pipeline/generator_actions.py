from .action_types import GeneratorActionType
from .data_types_tree import Ensemble, Struc, Float

class RangeGenerator(GeneratorActionType):
    
    _name = "RangeGenerator"
    """Display name of action"""
    _description = "Generator for generation parallel list"
    """Display description of action"""  

    def __init__(self, **kwargs):
        """
        :param DTT Output: type of data, that is use in constructor as
            template for resalt structure if empty, type is constructed
            from values as Struct of set names 
        :param Dictionary Items: Dictionary that describe generated
            way how generate result. Values have this attributes::
                - :name(string):require  variable name 
                - :value(float): require variable middle value
                - :step(float): default 1, step for generation
                - :n_plus(integer): default 1, amount of plus steps
                - :n_minus(integer): default 1, amount of minus steps
                - :exponential(bool): default False, if true value is processed exponencially 
        :param AllCases bool: Cartesian product, default value False:
        """
        super(RangeGenerator, self).__init__(**kwargs)
        if self.output is None:
            self.output = self._get_output_from_items()

    def _get_output_from_items(self):
        """Construct output from set items"""
        params = {}
        if 'Items' in self.variables:
            if isinstance(self.variables['Items'], list):
                for item in self.variables['Items']:
                    if isinstance(item,  dict):
                        if 'name' in item:
                            try:
                                params[item['name']] = Float()
                            except:
                                pass
        if len(params)>1:                    
            self.output = Ensemble(Struc(params)) 
 
    def _get_variables_script(self):    
        """return array of variables python scripts"""
        var = super(RangeGenerator, self)._get_variables_script()
        if self.variables["AllCases"]:
            var.append("AllCases=True")            
        return var

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
        # ToDo generate ensemble
        return  self._get_runner(None)

    def _check_params(self):    
        """check if all require params is set"""
        err = super(RangeGenerator, self)._check_params()
        if self.output is None:
            err.append("Can't determine output from items parameter")
        else:            
            if not isinstance(self.variables['Output'],Ensemble):
                err.append("Output type must be Ensemble type")
        if 'Items' not in self.variables:
            err.append("Parameter 'Items' must have at least one item")
        else:    
            if not isinstance(self.variables['Items'], list):
                err.append("Items parameter must be List")
            else:
                if len(self.variables['Items'])<1:
                    err.append("Items parameter must be List")
                else:
                    i=0
                    for item in self.variables['Items']:
                        if not isinstance(item,  dict):
                            err.append("Item[{0}] in Items list is not Dictionary".format(str(i)))
                        else:
                            if not 'name' in item:
                                err.append("Parameter 'name' in item[{0}] is required".format(str(i)))
                            if not 'value' in item:
                                err.append("Parameter 'value' in item[{0}] is required".format(str(i)))
                        i += 1
        return err
        
    def validate(self):    
        """validate variables, input and output"""
        err = self._check_params()
        if self.output is None:
            if not self.output.match_type(self._get_output_from_items):
                err.append("Comparation of output type and items fails")
        return err
