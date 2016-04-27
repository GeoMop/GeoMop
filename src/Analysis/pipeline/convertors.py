from .generic_tree import GTT, GDTT
from .code_formater import Formater

__convertor_counter__ = 0
"""convertor counter for unique settings in created script for code generation"""

class Convertor():
    """
    Parent class for convertors. Convertors define output
    data structure for connectors or some commposit
    data tree structure function (select, sort each).
    
    Convertor class is use by connector, ancestors have
    some output restrictions and is use by composite DDT
    functions.
    """
    name = "conv"
    """Display name of action"""
    description = "Convertor"
    """Display description of action"""
    
    def __init__(self, def_output):
        """
        Define output structure
        
        :param TT def_output: Define output from convertor. Output can contain
            TT types, their functions and inputs. (Input(0), Input(1), ...)
        """
        global __convertor_counter__
        
        __convertor_counter__ += 1
        self._id = __convertor_counter__
        """unique action number"""
        self._output = def_output
        """output defination"""
        self._convertors = []
        """list of convertors needed for this connector"""
        self._inputs = []
        """list of inputs needed for this connector"""
        self._load_errs = []
        """Contain init state errors"""
        self._inicialize()

    def _get_instance_name(self):
        return "{0}_{1}".format(self.name, str(self._id))

    def _inicialize(self):
        """Inicialize covertor. Convertors are inicialized in constructor"""
        if isinstance(self._output, GTT):
            convertors = self._output._get_convertors()
            self._convertors.extend(convertors)           
            self._inputs = self._output._get_inputs()
        else:
            self._load_errs.append("Invalid input convertor type.")

    def _get_output(self, inputs):
        """inicialize action run variables"""        
        script = '\n'.join(self._output._get_settings_script())
        internal_var = {}
        #inputs are replaced in script by internal dictionary, that is created from inputs
        for input in self._inputs:
            input_str = input._get_path()
            local_str = "input_" + input._num
            internal_var[input_str] = inputs.get_input_val(input._num)
            script = script.replace(input_str, "internal_var["+local_str+"]")
        #convertor are replaced in script by internal dictionary, that is created
        for convertor in self._convertors:
            conv_str = convertor._get_instance_name()
            internal_var[conv_str] = convertor
            script = script.replace(conv_str, "internal_var["+conv_str+"]")        
        try:            
            output = eval(script)
        except Exception as err:
            raise Exception("Output processing error ({0})".format(err))
        return output
        
    def _get_settings_script(self):    
        """return array of variables python scripts"""
        lines = []
        for convertor in self._convertors:
            lines.extend(convertor._get_variables_script())
        lines.append("{0}_{1} = {2}(".format(self.name, str(self._id), self.__class__.__name__))
        lines.extend(Formater.indent(self._output._get_settings_script(), 4))
        lines.append(")")
        return lines
        
    def _check_params(self, inputs):    
        """check if all require params is set"""
        err = []
        num = len(inputs)
        for input in self._inputs:
            if input._num>=num:
                err.append("Requsted input ({0}) is bigger than number of set Inputs ({1})".
                    input._num, num)
        err.extend(self._check_output())    
        return err
        
    def _check_output(self):    
        """check output variable type"""
        err = []
        if not isinstance(self._output, GDTT):
            err.append("Bad connector output type")
        return err

class Predicate(Convertor):
    """Class for filter defination"""
    name = "pred"
    """Display name of action"""
    description = "Predicate"
    """Display description of action"""  
        
    def __init__(self, output):
        """
        convertor for sort action
        """
        super(Predicate, self).__init__(output)
        
    def _check_output(self):    
        """check output variable type"""
        err = []
        if not isinstance(self._output, GTT):
            err.append("Bad predicate output type")
        return err

class KeyConvertor(Convertor):
    """Class for filter defination"""
    name = "key"
    """Display name of action"""
    description = "Convert structuru to key for comaparation"
    """Display description of action"""  
        
    def __init__(self, output):
        """
        convertor for select action
        """
        super(KeyConvertor, self).__init__(output)
        
    def _check_output(self):    
        """check output variable type"""
        err = []
        if not isinstance(self._output, GDTT):
            err.append("Bad selector output type")
        return err
