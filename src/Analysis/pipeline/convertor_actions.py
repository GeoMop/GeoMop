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
        #duplicate DefOutput
        if 'DefOutput' in self._variables:
            self.__inicialize_predicates()
            try:
                script = '\n'.join(self._variables['DefOutput']._get_settings_script())
                script = script.replace(self._get_instance_name()+".input", "new.input")
                if len(self._predicates_script)>0:
                    prescript = '\n'.join(self._predicates_script)
                    exec(prescript, globals())
                new._variables['DefOutput'] = eval(script)
            except Exception as err:
                new._load_errs.append("Duplicate output error ({0})".format(err))    
        #duplicate inputs
        for input in self._inputs:
            new._inputs.append(input)
        new._state = ActionStateType.created
        return new
 
    def _check_params(self):    
        """check if all require params is set"""
        err = super(CommonConvertor, self)._check_params()
        for input in self._variables['DefInputs']:
            if not isinstance(input, GDTT):
                err.append("Parameter 'DefInputs' ({0}) must be GDTT".format(
                        self.name))
        if len(self._inputs)<len(self._variables['DefInputs']):
            err.append("Convertor require more input parameters ({0})".format(
                str(len(self._variables['DefInputs']))))
        if 'DefOutput' not in self._variables:
            err.append("Convertor action require DefOutput parameter")
        else:
            if not isinstance(self._variables['DefOutput'], TT):
                err.append("Convertor parameter 'DefOutput' must be TT")
        return err
    
    def validate(self):
        """validate variables, input and output"""
        err = super(CommonConvertor, self).validate()
        return err
    
    def _get_runner(self, params):
        """
        return Runner class with process description
        """    
        return None
    
    def _inicialize(self):
        """inicialize action run variables"""
        if self._state.value > ActionStateType.created.value:
            return
        self.__inicialize_predicates()
        try:
            self._set_output(self._predicates_script)
        except Exception as err:
            self._load_errs.append(str(err))
        self._state = ActionStateType.initialized

    def __inicialize_predicates(self):
        """inicialize predicates variables"""
        self._predicates=[]
        self._predicates_script=[]
        self._predicates = self._variables['DefOutput']._get_predicates()
        if len(self._predicates)>0:
            self._predicates_script.append("from .predicate import Predicate")
        for predicate in self._predicates:
            self._predicates_script.extend(predicate.predicate._get_settings_script())

    def _run(self):
        """
        Process action on client site or prepare process environment and 
        return Runner class with  process description or None if action not 
        need externall processing.
        """
        self._set_output(self._predicates_script)
        return  self._get_runner(None)
        
    def _get_settings_script(self):    
        """return python script, that create instance of this class"""
        lines = []
        for predicate in self._predicates:
            if self._add_predicate(predicate):
                lines.extend(predicate.predicate._get_settings_script())
        lines.extend(super(CommonConvertor, self)._get_settings_script())
        return lines
