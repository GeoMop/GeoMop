import abc
from .code_formater import Formater

class TT(metaclass=abc.ABCMeta):
    """
    Abstract class for defination general tree
    """
    @abc.abstractmethod
    def _get_settings_script(self):
        """return python script, that create instance of this class"""
        pass

class GTT(TT):
    @abc.abstractmethod
    def _get_convertors(self):
        """return array of convertors containing in this structure"""
        pass

    @abc.abstractmethod
    def _get_inputs(self):
        """return array of inputs containing in this structure"""
        pass

    
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
        if isinstance(arg, GTT):
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
        if isinstance(arg, GTT):
            return arg._Or(*args)
    ret = False
    try:
        for arg in args:
            ret = ret or arg
    except Exception as ex:
        raise Exception("And parameter error " +str(ex))            
    return ret

class GDTT(GTT):
    """
    Class for abstract code, wothout acurate determination DTT type
    """
    def __init__(self, parent):
        """
        Initialize generic instance. Parameters are classes, that my be use
        instead this class. If is not set, class not process check during 
        replecement
        """
        self._path=""
        """Path to this variable in generic tree"""
        self.__predicate = None        
        """
        if GDTT represent function that use predicate for sort, 
        this variable is set to predicate instance
        """
        self.__selector = None        
        """
        if GDTT represent function that use selector for select, 
        this variable is set to selector instance
        """
        self.__convertor = None        
        """
        if GDTT represent function that use convertor for each, 
        this variable is set to convertor instance
        """
        self.__parent=parent
        """Parent GDTT strukture"""
    
    def _set_path(self, value):
        """set text describing variable"""
        self._path = value
        
    def _get_path(self):
        """get text describing variable"""
        return self._path
        
    def _get_main_settings_script(self):
        """return python script, that create only main class of DTT structure"""
        ret = "GDTT()"
        return [ret]
        
    def _get_settings_script(self):
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
            ret = GDTT(parent=self)
            ret._set_path(self._path + "." + name)
        return self.__dict__[name]
    
    def _set_predicate(self, predicate):
        self.__predicate = predicate

    def _set_selector(self, selector):
        self.__selector = selector
        
    def _set_convertor(self, convertor):
        self.__convertor = convertor

    def _get_predicate(self):
        return self.__predicate
        
    def _get_selector(self):
        return self.__selector

    def _get_convertor(self):
        return self.__convertor

    def _get_convertors(self):
        """return array of convertors containing in this structure"""
    
        ret = []
        if self.__parent is None:
            return ret
        if self.__selector is not None:
           ret.append(self.__selector)
           ret.extend(self.__selector._get_convertors())
        if self.__predicate is not None:
           ret.append(self.__predicate)
           ret.extend(self.__predicate._get_convertors())
        if self.__convertor is not None:
           ret.append(self.__convertor)
           ret.extend(self.__convertor._get_convertors())
        ret.extend(self.__parent._get_convertors())
        return ret 
 
    def _get_inputs(self):
        if self.__parent is None:
            return [self]
        return self.__parent._get_inputs()

    def select(self, predicate):
        """GDTT call select function"""
        if type(predicate).__name__ != "Predicate":
            raise ValueError("Unknown type of select predicate '{0}'".format(type(predicate).__name__ ))
        fp = GDTT(parent=self)
        fp._set_predicate(predicate)
        fp._set_path("{0}.select({1})".format(self._path, predicate._get_instance_name()))
        return fp

    def sort(self, selector):
        """GDTT call sort function"""
        if type(selector).__name__ != "Selector":
            raise ValueError("Unknown type of sort selector '{0}'".format(type(selector).__name__ ))
        fp = GDTT(parent=self)
        fp._set_selector(selector)
        fp._set_path("{0}.sort({1})".format(self._path, selector._get_instance_name()))
        return fp
        
    def each(self, convertor):
        """GDTT call sort function"""
        if type(convertor).__name__ != "Convertor":
            raise ValueError("Unknown type of sort convertor '{0}'".format(type(convertor).__name__ ))
        fp = GDTT(parent=self)
        fp._set_convertor(convertor)
        fp._set_path("{0}.each({1})".format(self._path, convertor._get_instance_name()))
        return fp

class GDTTFunc(GTT):
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
    
    def _get_convertors(self):
        """return array of convertors containing in this structure"""
        ret = []
        for o in self.o:
            if isinstance(o, GTT):
                ret.extend(o._get_convertors())
        return ret
        
    def _get_inputs(self):
        """return array of inputs containing in this structure"""
        ret = []
        for o in self.o:
            if isinstance(o, GTT):
                ret.extend(o._get_inputs())
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
        super(Input, self).__init__(None)
        self._num = num
        """Number of input"""
        self._set_path("Input({0})".format(str(num)))
