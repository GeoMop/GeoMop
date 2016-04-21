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
    def _get_settings_script(self):
        """return python script, that create instance of this class"""
        pass

    @abc.abstractmethod
    def _get_predicates(self):
        """return dictionary (path->predicate) of predicates containing in this structure"""
        pass

class GDTT_Operators(TT):
    def __lt__(a, b):
        return GDTTFunc('<', a, b)
        
    def __le__(a, b):
        return GDTTFunc('<=', a, b)
        
    def __eq__(a, b):
        return GDTTFunc('==', a, b)
        
    def __ne__(a, b):
        return GDTTFunc( '!=', a, b)
        
    def __ge__(a, b):
        return GDTTFunc('>=', a, b)
        
    def __gt__(a, b):
        return GDTTFunc('>', a, b)

    def __not__(a):
        return GDTTFunc('not', a)
        
    def _And(self, *args):
        return GDTTFunc('And', *args)
        
    def _Or(self, *args):
        return GDTTFunc('Or', *args)
        
def And(*args):
    """Global and opperator"""
    for arg in args:
        if isinstance(arg, GDTT_Operators):
            return arg._And(*args)
    ret = True
    try:
        for arg in args:
            ret = ret and arg
    except Exception as ex:
        raise Exception("And parameter error " +str(ex))            

    return ret
    
def Or(*args):
    """Global or opperator"""
    for arg in args:
        if isinstance(arg, GDTT_Operators):
            return arg._Or(*args)
    ret = False
    try:
        for arg in args:
            ret = ret or arg
    except Exception as ex:
        raise Exception("And parameter error " +str(ex))            
    return ret

class GDTT(GDTT_Operators):
    """
    Class for abstract code, wothout acurate determination DTT type
    """
    def __init__(self, parent=None):
        """
        Initialize generic instance. Parameters are classes, that my be use
        instead this class. If is not set, class not process check during 
        replecement
        """
        self.__path=""
        """Path to this variable in generic tree"""
        self.__fpredicates = []
        """
        list of GDTT represented predicate functions to this GDTT points 
        """
        self.__select_predicate=None        
        """
        if GDTT represent function that use predicate for select, 
        this variable is set to predicate instance
        """
        self.__sort_predicate=None        
        """
        if GDTT represent function that use predicate for sort, 
        this variable is set to predicate instance
        """
        self.__parent=parent
        """Parent GDTT strukture"""
    
    def _set_path(self, value):
        """set text describing variable"""
        self.__path = value
        
    def _get_path(self):
        """get text describing variable"""
        return self.__path
        
    def _get_main_settings_script(self):
        """return python script, that create only main class of DTT structure"""
        ret = "GDTT()"
        return [ret]
        
    def _get_settings_script(self):
        """return python script, that create instance of this class"""        
        return [self.__path]
    
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
                self.__dict__[name]._set_path(self.__path + "." + name)
        return self.__dict__[name]
    
    def _set_sort_predicate(self, predicate):
        self.__sort_predicate = predicate

    def _set_select_predicate(self, predicate):
        self.__sort_predicate = predicate

    def _get_sort_predicate(self):
        return self.__sort_predicate
        
    def _get_select_predicate(self):
        return self.__sort_predicate

    def _get_predicates(self):        
        """return dictionary (path->predicate) of predicates containing in this structure"""
        ret = []
        if self.__parent is None:
            return ret
        if self.__select_predicate is not None:
           ret.append(PredicatePoint(self.__select_predicate, self.__parent._get_path()))
        if self.__sort_predicate is not None:
            ret.append(PredicatePoint(self.__sort_predicate, self.__parent._get_path()))
        ret.extend(self.__parent._get_predicates())
        return ret        

    def select(self, predicate):
        """GDTT call select function"""
        if type(predicate).__name__ != "Predicate":
            raise ValueError("Unknown type of select predicate '{0}'".format(type(predicate).__name__ ))
        for fp in self.__fpredicates:
            if fp._get_select_predicate() == predicate:
                return fp
        fp = GDTT(parent=self)
        self.__fpredicates.append(fp)
        fp._set_select_predicate(predicate)
        fp._set_path("{0}.select({1})".format(self.__path, predicate._get_instance_name()))
        return fp

    def sort(self, predicate):
        """GDTT call sort function"""
        if type(predicate).__name__ != "Predicate":
            raise ValueError("Unknown type of sort predicate '{0}'".format(type(predicate).__name__ ))
        for fp in self.__fpredicates:
            if fp._get_sort_predicate() == predicate:
                return fp
        fp = GDTT(parent=self)
        self.__fpredicates.append(fp)
        fp._set_sort_predicate(predicate)
        fp._set_path("{0}.sort({1})".format(self.__path, predicate._get_instance_name()))
        return fp

class GDTTFunc(GDTT_Operators):
    """
    Class for save function code with GDTT variables
    """
    def __init__(self, operator,  *o):
        """test"""
        self.o = []
        for arg in o:
            self.o.append(arg)
        """second operand"""
        self.operator = operator
        """operator"""
    
    def _get_predicates(self):
        """return dictionary (path->predicate) of predicates containing in this structure"""
        ret = []
        for o in self.o:
            if isinstance(o, TT):
                ret.extend(o._get_predicates())
        return ret
    
    @staticmethod
    def _get_str(o):
        """return objecct string presentation for _get_settings_script function"""        
        if isinstance(o, TT):
            return o._get_settings_script()
        elif isinstance(o, str): 
            return ["'{0}'".format(o)]
        return ["{0}".format(str(o))]
    
    def _get_settings_script(self):
        """return python script, that create instance of this class""" 
        if self.operator == "And" or self.operator == "Or":
            return self.__get_func_settings_script()
        elif len(self.o)<1:
            return self.__get_simple_settings_script()
        else:
            return self.__get_dual_settings_script()

    def __get_dual_settings_script(self):
        """script two member operators"""
        s_o1 = self.__get_str(self.o[0])
        s_o2 = self.__get_str(self.o[1])
        if len(s_o1)==1:
           if len(s_o2)==1:
                if (len(s_o1)+len(s_o2))<Formater.__ROW_LEN__:
                    return ["{0}{1}{2}".format(s_o1[0], self.operator, s_o2[0])]
                else:
                    return ["{0}{1}(".format(s_o1[0], self.operator),
                        "    {0}".format( s_o2[0]), ")"]
           else:
                ret = ["{0}{1}(".format(self.operator, s_o1[0])]
                ret.extend(Formater.indent(s_o2, 4))
                ret.append(")")
                return ret   
        else:
            if len(s_o2)==1:
                ret = ["("]
                ret.extend(Formater.indent(s_o1, 4))
                ret.append("){0}{1}".format(self.operator, s_o2[0]))
                return ret
            else:
                ret = ["("]
                ret.extend(Formater.indent(s_o1, 4))                                
                ret.append("){0}(".format(self.operator))
                ret.extend(Formater.indent(s_o2, 4))
                ret.append(")")
                return ret
                
    def __get_simple_settings_script(self):
        """Script for one member operators"""
        s = self.__get_str(self.o[0])
        if len(s)==1:
            return ["{0} {1}".format(self.operator, s[0])]
        else:
            ret = ["{0}(".format(self.operator)]
            ret.extend(Formater.format_parameter(s[0], 4))
            ret.append(")")
            return ret

    def __get_func_settings_script(self):
        """Script for more member operators"""
        ret=["{0}(".format(self.operator)]
        s_len=0
        multiline=False
        for o in self.o:
            s_o = self.__get_str(o)
            if len(s_o)>1:
                multiline=True
                return
            s_len += len(s_o[0])
        if not multiline and s_len > Formater.__ROW_LEN__ :
            multiline=True
        for o in self.o:
            s_o = self.__get_str(o)
            if len(s_o)==1:
                if multiline:
                    ret.append("    {0},".format(s_o[0]))
                else:
                    ret[-1] += " {0},".format(s_o[0])
            else:
                ret.extend(Formater.format_parameter(s_o, 4))
        ret[-1] = ret[-1][:-1]
        if multiline:
            ret.append(")")
        else:
            ret[0] += ")"
        return ret

class Input(GDTT):
    """Class for defination connector input and its number"""
    def __init__(self, num=0):
        super(Input, self).__init__()
        self.__num = num
        """Number of input"""
        self.__tts = None
        """Generic data trees represented this input"""
