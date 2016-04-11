from .action_types import ConvertorActionType, ActionStateType
from .generic_tree import TT, GDTT
from .data_types_tree import *

class CommonConvertor(ConvertorActionType):
    
    _name = "CommonConvertor"
    """Display name of action"""
    _description = "Convertor for base variable manipulation"
    """Display description of action"""  

    def __init__(self, **kwargs):
        """
        :param GDTT DefInputs: Convertor template may have 
            GDTT types for checking. when is set real input, input typ is compare
            with this parameter
        :param TT DefOutput: Define output from convertor. Output can contain
            TT types, their functions and inputs. (self.input[0], self.input[1], ...)
        """
        super(CommonConvertor, self).__init__(**kwargs)
        self._predicates=[]
        """list of predicates in DefInputs"""
        self._predicates_script=[]
        """Script for predicates inicialization"""
       
    def duplicate(self):
        """Duplicate convertor. Returned convertor is not inicialized and checked"""
        new = CommonConvertor()
        #duplicate DefInputs
        for i in range(0, len(self.variables['DefInputs'])):
            def_input = self.variables['DefInputs'][i].duplicate()
            def_input.set_path("{0}.input({1})".format(
                new.get_instance_name(),str(i)))
            new.variables['DefInputs'].append(def_input)            
        #duplicate DefOutput
        try:
            script = '\n'.join(self.variables['DefOutput'].get_settings_script())
            script = script.replace(self.get_instance_name()+".input", "new.input")
            if len(self._predicates_script)>0:
                prescript = '\n'.join(self._predicates_script)
                exec(prescript, globals())
            new.variables['DefOutput'] = eval(script)
        except Exception as err:
            new._load_errs.append("Duplicate output error ({0})".format(err))    
        #duplicate inputs
        for input in self.inputs:
            new.inputs.append(input)
        new.state = ActionStateType.created
        return new
 
    def _check_params(self):    
        """check if all require params is set"""
        err = super(CommonConvertor, self)._check_params()
        for input in self.variables['DefInputs']:
            if not isinstance(input, GDTT):
                err.append("Parameter 'DefInputs' ({0}) must be GDTT".format(
                        self.name))
        if len(self.inputs)<len(self.variables['DefInputs']):
            err.append("Convertor require more input parameters ({0})".format(
                str(len(self.variables['DefInputs']))))
        if 'DefOutput' not in self.variables:
            err.append("Convertor action require DefOutput parameter")
        else:
            if not isinstance(self.variables['DefOutput'], TT):
                err.append("Convertor parameter 'DefOutput' must be TT")
        return err
    
    def validate(self):
        """validate variables, input and output"""
        err = super(CommonConvertor, self).validate()
        if len(self.inputs)>=len(self.variables['DefInputs']):
            for i in range(len(self.variables['DefInputs'])):
                if not self.variables['DefInputs'][i].check_type(type(self.get_input_val(i))):
                    err.append("Convertor input '{0}' return wrong type variable '{1}'".format(
                str(i), self.variables['DefInputs'][i].get_main_settings_script()))
        return err
    
    def _get_runner(self, params):
        """
        return Runner class with process description
        """    
        return None
    
    def inicialize(self):
        """inicialize action run variables"""
        if self.state.value > ActionStateType.created.value:
            return
        self._predicates_script=[]
        self._predicates = self.variables['DefOutput'].get_predicates()
        if len(self._predicates)>0:
            self._predicates_script.append("from .predicate import Predicate")
        for predicate in self._predicates:
            self._predicates_script.extend(predicate.predicate.get_settings_script())
        try:
            self.set_output(self._predicates_script)
        except Exception as err:
            self._load_errs.append(str(err))
        self.state = ActionStateType.initialized

    def run(self):
        """
        Process action on client site or prepare process environment and 
        return Runner class with  process description or None if action not 
        need externall processing.
        """
        self.set_output(self._predicates_script)
        return  self._get_runner(None)
        
    def get_settings_script(self):    
        """return python script, that create instance of this class"""
        lines = []
        for predicate in self._predicates:
            if self.add_predicate(predicate):
                lines.extend(predicate.predicate.get_settings_script())
        lines.extend(super(CommonConvertor, self).get_settings_script())
        return lines
