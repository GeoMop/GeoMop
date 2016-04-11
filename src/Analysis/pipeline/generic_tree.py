import abc
from .code_formater import Formater

class PredicatePoint():
    """class for determining predicates"""
    def __init__(self, predicate, path):
        self.path = path
        """path to sortable CompositeDTT"""
        self.predicate = predicate
        """path to predicate"""

class TT(metaclass=abc.ABCMeta):
    """
    Abstract class for defination general tree
    """
    @abc.abstractmethod
    def get_settings_script(self):
        """return python script, that create instance of this class"""
        pass

    @abc.abstractmethod
    def get_predicates(self):
        """return dictionary (path->predicate) of predicates containing in this structure"""
        pass

class GDTT(TT):
    """
    Class for abstract code, wothout acurate determination DTT type
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize generic instance. Parameters are classes, that my be use
        instead this class. If is not set, class not process check during 
        replecement
        """
        self._path=""
        """Path to this variable in generic tree"""
        self._types = []
        """GDDT types for substitution"""
        self._fpredicates = []
        """
        list of GDTT represented predicate functions to this GDTT points 
        """
        self._select_predicate=None        
        """
        if GDTT represent function that use predicate for select, 
        this variable is set to predicate instance
        """
        self._sort_predicate=None        
        """
        if GDTT represent function that use predicate for sort, 
        this variable is set to predicate instance
        """
        self._parent=None
        """Parent GDTT strukture"""
        for value in args:
            self._types.append(value)
        for name, value in kwargs.items():
            if name == "parent":
                self._parent=value
      
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
        """set text describing variable"""
        self._path = value
        
    def get_path(self):
        """get text describing variable"""
        return self._path
        
    def get_main_settings_script(self):
        """return python script, that create only main class of DTT structure"""
        ret = "GDTT("
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
                self.__dict__[name] = GDTT(parent=self)
                self.__dict__[name].set_path(self._path + "." + name)
        return self.__dict__[name]
    
    def set_sort_predicate(self, predicate):
        self._sort_predicate = predicate

    def set_select_predicate(self, predicate):
        self._sort_predicate = predicate

    def get_sort_predicate(self):
        return self._sort_predicate
        
    def get_select_predicate(self):
        return self._sort_predicate

    def get_predicates(self):        
        """return dictionary (path->predicate) of predicates containing in this structure"""
        ret = []
        if self._parent is None:
            return ret
        if self._select_predicate is not None:
           ret.append(PredicatePoint(self._select_predicate, self._parent.get_path()))
        if self._sort_predicate is not None:
            ret.append(PredicatePoint(self._sort_predicate, self._parent.get_path()))
        ret.extend(self._parent.get_predicates())
        return ret        

    def select(self, predicate):
        """GDTT call select function"""
        if type(predicate).__name__ != "Predicate":
            raise ValueError("Unknown type of select predicate '{0}'".format(type(predicate).__name__ ))
        for fp in self._fpredicates:
            if fp.get_select_predicate() == predicate:
                return fp
        fp = GDTT(parent=self)
        self._fpredicates.append(fp)
        fp.set_select_predicate(predicate)
        fp.set_path("{0}.select({1})".format(self._path, predicate.get_instance_name()))
        return fp

    def sort(self, predicate):
        """GDTT call sort function"""
        if type(predicate).__name__ != "Predicate":
            raise ValueError("Unknown type of sort predicate '{0}'".format(type(predicate).__name__ ))
        for fp in self._fpredicates:
            if fp.get_sort_predicate() == predicate:
                return fp
        fp = GDTT(parent=self)
        self._fpredicates.append(fp)
        fp.set_sort_predicate(predicate)
        fp.set_path("{0}.sort({1})".format(self._path, predicate.get_instance_name()))
        return fp

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
        return GDTTFunc(a, b, 'or_')

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
    
    def get_predicates(self):
        """return dictionary (path->predicate) of predicates containing in this structure"""
        ret = []
        if isinstance(self.o1, TT):
            ret.extend(self.o1.get_predicates())
        if isinstance(self.o2, TT):
            ret.extend(self.o2.get_predicates())
        return ret
    
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
            return ["'{0}'".format(o)]
        return ["{0}".format(str(o))]
    
    def get_settings_script(self):
        """return python script, that create instance of this class"""
        s_o1 = self._get_str(self.o1)
        s_o2 = self._get_str(self.o2)
        if len(s_o1)==1:
           if s_o2 is None:
               return ["{0}({1})".format(self.operator, s_o1[0])]
           elif len(s_o2)==1:
                return ["{0}({1},".format(self.operator, s_o1[0]),
                    "    {0}".format( s_o2), ")"]
           else:
                ret = ["{0}({1},".format(self.operator, s_o1[0])]
                ret.extend(Formater.format_parameter(s_o2, 0))
                ret[-1] = ret[-1][:-1]
                ret.append(")")
                return ret   
        else:
            if s_o2 is None:
                ret = ["{0}(".format(self.operator)]
                ret.extend(Formater.format_parameter(s_o1, 4))
                ret.append(")")
                return ret
            elif len(s_o2)==1:
                ret = ["{0}(".format(self.operator)]
                ret.extend(Formater.format_parameter(s_o1, 4))
                ret.append("    {0}".format( s_o2[0]))
                ret.append(")")
                return ret
            else:
                ret = ["{0}(".format(self.operator)]
                ret.extend(Formater.format_parameter(s_o1, 4))                                
                ret.extend(Formater.format_parameter(s_o2, 4))
                ret[-1] = ret[-1][:-1] 
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
                    self.operator == 'and_' or \
                    self.operator == 'or_'

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
        return GDTTFunc(a, b, 'or_')
