from .action_types import GeneratorActionType, ActionStateType
from .data_types_tree import Ensemble, Struct, Float, DTT
import copy
from .code_formater import Formater

class VariableGenerator(GeneratorActionType):
    
    name = "VariableGenerator"
    """Display name of action"""
    description = "Generator for creating static DTT variable"
    """Display description of action"""  

    def __init__(self, **kwargs):
        """
        :param DTT Variable: Dictionary that describe struc parameters
        """
        super(VariableGenerator, self).__init__(**kwargs)
       
    def _inicialize(self):
        """inicialize action run variables"""
        if self._get_state().value > ActionStateType.created.value:
            return
        self._output = self._get_valid_output()
        self._set_state(ActionStateType.initialized)
        self._hash.update(bytes(self.__class__.__name__, "utf-8"))
        if "Variable" in self._variables and \
            isinstance(self._variables["Variable"], DTT) and \
            self._variables["Variable"]._is_set():
            self._hash.update(bytes(self._variables['Variable']._get_unique_text(True), "utf-8"))  
        
    def _get_valid_output(self):
        """Construct output from set items"""
        if "Variable" in self._variables and  isinstance(self._variables["Variable"], DTT):
            return self._variables["Variable"]
        
    def _get_variables_script(self):    
        """return array of variables python scripts"""
        var = super(VariableGenerator, self)._get_variables_script()
        variable=Formater.format_variable(
            "Variable", self._variables["Variable"]._get_settings_script(), 0)
        if len(variable)>0 and len(variable[-1])>0: 
            variable[-1] = variable[-1][:-1]
            var.append(variable)
        return var

    def _check_params(self):    
        """check if all require params is set"""
        err = super(VariableGenerator, self)._check_params()
        if "Variable" not in self._variables:
            self._add_error(err, "Variable parameter is required")
        elif not isinstance(self._variables["Variable"], DTT):
            self._add_error(err, "Parameter 'Variable' is not valid DTT variable")
        else:
            if not self._variables["Variable"]._is_set():
                self._add_error(err, "Variable in variable generator must be set")
            if self._output is None:
                self._add_error(err, "Can't determine valid output")
        return err
        
    def validate(self):
        """validate variables, input and output"""
        err = super(VariableGenerator, self).validate()
        return err

class RangeGenerator(GeneratorActionType):
    
    name = "RangeGenerator"
    """Display name of action"""
    description = "Generator for generation parallel list"
    """Display description of action"""  

    def __init__(self, **kwargs):
        """
        :param Dictionary Items: Dictionary that describe generated
            way how generate result. Values have this attributes::
                - :name(string):require  variabvar.append(["AllCases=True"])le name 
                - :value(float): require variable middle value
                - :step(float): default 1, step for generation
                - :n_plus(integer): default 1, amount of plus steps
                - :n_minus(integer): default 1, amount of minus steps
                - :exponential(bool): default False, if true value is processed exponencially 
        :param AllCases bool: Cartesian product, default value False:
        """
        super(RangeGenerator, self).__init__(**kwargs)
       
            
    def _inicialize(self):
        """inicialize action run variables"""
        if self._get_state().value > ActionStateType.created.value:
            return
        self._output = self.__get_output_from_items()
        template = copy.deepcopy(self._output.subtype)
        # first is middle
        self._output.add_item(template)
        for item in self._variables['Items']:
            if not isinstance(item,  dict):
                continue                
            if 'name' in item and item['name'] in template:
                if 'name' in item:
                    setattr(template, item['name'], item['value'])
        # Output computation is made in inicialize time, count of cycles
        # is known for statistics (easier get_statiscics function)
        for item in self._variables['Items']:
            if 'AllCases' in self._variables and self._variables['AllCases']:
                ready = copy.deepcopy(self._output)
                for template_i in ready:
                    self._generate_step(template_i, item)
            else:
                self._generate_step(template, item)
        self._set_state(ActionStateType.initialized)
        self._hash.update(bytes(self.__class__.__name__, "utf-8"))
        self._hash.update(bytes(self._output._get_unique_text(True), "utf-8"))
        
    def __get_output_from_items(self):
        """Construct output from set items"""
        params = {}
        if 'Items' in self._variables:
            if isinstance(self._variables['Items'], list):
                for item in self._variables['Items']:
                    if isinstance(item,  dict):
                        if 'name' in item:
                            try:
                                params[item['name']] = Float()
                            except:
                                pass
        if len(params)>1:                    
            return Ensemble(Struct(params))
        return None
 
    def _get_variables_script(self):    
        """return array of variables python scripts"""
        var = super(RangeGenerator, self)._get_variables_script()
        i=1
        items=['Items = [']
        for item in self._variables['Items']:
            if not 'name' in item or not 'value' in item:
                continue
            items.append("    {0}'name':'{1}'".format('{', item['name']))
            if 'value' in item:
                items[i] += (", 'value':{0}".format(str(item['value'])))
            if 'step' in item:
                items[i] += (", 'step':{0}".format(str(item['step'])))
            if 'n_plus' in item:
                items[i] += (", 'n_plus':{0}".format(str(item['n_plus'])))
            if 'n_minus' in item:
                items[i] += (", 'n_minus':{0}".format(str(item['n_minus'])))
            if 'exponential' in item and item['exponential']:
                items[i] += (", 'exponential':True")
            items[i] += "},"
            i += 1
        if i>1:
            items[i-1]=items[i-1][:-1]
            items.append(']')
            var.append(items)
        if 'AllCases' in self._variables and self._variables["AllCases"]:
            var.append(["AllCases=True"])
            
        return var
        
    def _generate_step(self, template, item):
        """generate plus and minus variants for one item"""
        plus = 1
        if 'n_plus' in item:
            plus = item['n_plus']
        minus = 1
        if 'n_minus' in item:
            minus = item['n_minus']
        step = 1
        if 'step' in item:
            step = item['step']
        for i in range(0, plus):
            template2 =copy.deepcopy(template)
            rstep = (i+1)*step
            if 'exponential' in item and item['exponential']:
                rstep = 2**i*step
            setattr(template2, item['name'], 
                getattr(template2, item['name']).value+rstep)    
            self._output.add_item(template2)
        for i in range(0, minus):
            template2 =copy.deepcopy(template)
            rstep = (i+1)*step
            if 'exponential' in item and item['exponential']:
                rstep = 2**i*step
            setattr(template2, item['name'], 
                getattr(template2, item['name']).value-rstep)    
            self._output.add_item(template2)                

    def _check_params(self):    
        """check if all require params is set"""
        err = super(RangeGenerator, self)._check_params()
        if self._output is None:
            self._add_error(err, "Can't determine output from items parameter")
        else:            
            if not isinstance(self._output, Ensemble):
                self._add_error(err, "Output type must be Ensemble type")
        if 'Items' not in self._variables:
            self._add_error(err, "Items parameter is required")
        else:    
            if not isinstance(self._variables['Items'], list):
                self._add_error(err, "Items parameter must be List")
            else:
                if len(self._variables['Items'])<1:
                    self._add_error(err, "Parameter 'Items' must have at least one item")
                else:
                    i=0
                    for item in self._variables['Items']:
                        if not isinstance(item,  dict):
                            self._add_error(err, "Item[{0}] in Items list is not Dictionary".format(str(i)))
                        else:
                            if not 'name' in item:
                                self._add_error(err, "Parameter 'name' in item[{0}] is required".format(str(i)))
                            else:
                                if not self._check_var_name(item['name']):
                                    self._add_error(err, "Parameter 'name' in item[{0}] is not valid attribute name".format(str(i)))
                            if not 'value' in item:
                                self._add_error(err, "Parameter 'value' in item[{0}] is required".format(str(i)))
                            else:
                                if not self._check_float(item['value']):
                                    self._add_error(err, "Parameter 'value' in item[{0}] is not valid float".format(str(i)))
                            if 'step' in item:
                                if not self._check_float(item['step']):
                                    self._add_error(err, "Parameter 'step' in item[{0}] is not valid float".format(str(i)))
                            if 'n_plus' in item:
                                if not self._check_int(item['n_plus']):
                                    self._add_error(err, "Parameter 'n_plus' in item[{0}] is not valid integer".format(str(i)))
                            if 'n_minus' in item:
                                if not self._check_int(item['n_minus']):
                                    self._add_error(err, "Parameter 'n_minus' in item[{0}] is not valid integer".format(str(i)))
                            if 'exponential' in item:
                                if not self._check_bool(item['exponential']):
                                    self._add_error(err, "Parameter 'exponential' in item[{0}] is not valid boolean".format(str(i)))
                        i += 1
        return err
        
    def validate(self):    
        """validate variables, input and output"""
        err = super(RangeGenerator, self).validate()
        return err
