from .data_types_tree import TT
from .code_formater import Formater

class GDTT(TT):
    """
    Class for abstract code, wothout acurate determination DTT type
    """
    def __init__(self, *args):
        """
        Initialize generic instance. Parameters are classes, that my be use
        instead this class. If is not set, class not process check during 
        replecement
        """
        self._path=""
        """Path to this variable in generic tree"""
        self._types = []
        """GDDT types for substitution"""
        for value in args:
            self._types.append(value)
      
    def duplicate(self):
        """Get new GTT with defined types, without addet attributes"""
        new = GDTT(*self._types)
        return new 
        
    def check_type(self, type):
        """Check if set type is in list of supported types"""
        if len(self._types)==0:
            return True
        for t in self._types:
            if type is t:
                return True
        return False
    
    def set_path(self, value):
        self._path = value
           
    def get_main_settings_script(self):
        """return python script, that create only main class of DTT structure"""
        ret = "GDDT("
        for type in self._types:
            ret += type.__name__+","
        ret = ret[:-1]+")"
        return [ret]
        
    def get_settings_script(self):
        """return python script, that create instance of this class"""        
        return [self._path]
    
    def __setattr__(self, name, value): 
        """ assignation"""
        if name[0] != '_':
            raise ValueError("Attribute of generic tree type can't be set")            
        else:            
            self.__dict__[name]=value
            
    def __getattr__(self, name): 
        """save assignation"""
        if name[0] != '_':
            if name not in self.__dict__:
                self.__dict__[name] = GDTT()
                self.__dict__[name].set_path(self._path + "." + name)
        return self.__dict__[name]
        
    def __lt__(a, b):
        return GDTTFunc(a, b, 'lt')
        
    def __le__(a, b):
        return GDTTFunc(a, b, 'le')
        
    def __eq__(a, b):
        return GDTTFunc(a, b, 'eq')
        
    def __ne__(a, b):
        return GDTTFunc(a, b, 'ne')
        
    def __ge__(a, b):
        return GDTTFunc(a, b, 'ge')
        
    def __gt__(a, b):
        return GDTTFunc(a, b, 'gt')

    def __not__(a):
        return GDTTFunc(a, None, 'not')
        
    def __abs__(a):
        return GDTTFunc(a, None, 'abs')
        
    def __and__(a, b):
        return GDTTFunc(a, b, 'and_')
        
    def __mul__(a, b):
        return GDTTFunc(a, b, 'mul')
        
    def __neg__(a, b):
        return GDTTFunc(a, None, 'neg')
        
    def __or__(a, b):
        return GDTTFunc(a, b, 'or')

class GDTTFunc(TT):
    """
    Class for save function code with GDTT variables
    """
    def __init__(self,o1, o2, operator):
        """test"""
        self.o1 = o1
        """first operand"""
        self.o2 = o2
        """second operand"""
        self.operator = operator
        """operator"""
    
    def check_generic_type(self):
        """Check if function is supported for set generic type"""
        return []
        
    def check_type(self):
        """Check if finction is supported for substitued type"""
        return []
    
    @staticmethod
    def _get_str(o):
        """return objecct string presentation for get_settings_script function"""        
        if o is None:
            return None
        if isinstance(o, TT):
            return o.get_settings_script()
        elif isinstance(o, str): 
            return ["'{0}',".format(o)]
        return ["'{0}',".format(str(o))]
    
    def get_settings_script(self):
        """return python script, that create instance of this class"""
        s_o1 = self._get_str(self.o1)
        s_o2 = self._get_str(self.o2)
        if len(s_o1)==1:
           if s_o2 is None:
               return ["{0}({1})".format(self.operand, s_o1)]
           elif len(s_o2)==1:
                return ["{0}({1},".format(self.operand, s_o1),
                    "    {0},".format( s_o2), ")"]
           else:
                ret = ["{0}({1},".format(self.operand, s_o1)]
                ret.append("    (")
                ret.extend(Formater.format_parameter(s_o2, 8))
                ret.append("    )")
                ret.append(")")
                return ret   
        else:
            if s_o2 is None:
                ret = ["{0}(".format(self.operand)]
                ret.extend(Formater.format_parameter(s_o1, 4))
                ret.append(")")
                return ret
            elif len(s_o2)==1:
                ret = ["{0}(".format(self.operand)]
                ret.append("    (")
                ret.extend(Formater.format_parameter(s_o1, 8))
                ret.append("    ),({0})".format(s_o2))                
                ret.append(")")
                return ret
            else:
                ret = ["{0}(".format(self.operand)]
                ret.append("    (")
                ret.extend(Formater.format_parameter(s_o1, 8))
                ret.append("    ),(")                
                ret.extend(Formater.format_parameter(s_o2, 8))
                ret.append("    )")
                ret.append(")")
                return ret

    def return_bool(self):
        """check if function return bool"""
        return self.operator == 'lt' or \
                    self.operator == 'le' or \
                    self.operator == 'eq' or \
                    self.operator == 'ne' or \
                    self.operator == 'ge' or \
                    self.operator == 'gt' or \
                    self.operator == 'not' or \
                    self.operator == 'and' or \
                    self.operator == 'or'

    def __lt__(a, b):
        return GDTTFunc(a, b, 'lt')
        
    def __le__(a, b):
        return GDTTFunc(a, b, 'le')
        
    def __eq__(a, b):
        return GDTTFunc(a, b, 'eq')
        
    def __ne__(a, b):
        return GDTTFunc(a, b, 'ne')
        
    def __ge__(a, b):
        return GDTTFunc(a, b, 'ge')
        
    def __gt__(a, b):
        return GDTTFunc(a, b, 'gt')

    def __not__(a):
        return GDTTFunc(a, None, 'not')
        
    def __abs__(a):
        return GDTTFunc(a, None, 'abs')
        
    def __and__(a, b):
        return GDTTFunc(a, b, 'and_')
        
    def __mul__(a, b):
        return GDTTFunc(a, b, 'mul')
        
    def __neg__(a, b):
        return GDTTFunc(a, None, 'neg')
        
    def __or__(a, b):
        return GDTTFunc(a, b, 'or')
