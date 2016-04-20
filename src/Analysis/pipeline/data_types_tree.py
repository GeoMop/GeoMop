import abc
from .generic_tree import TT
from .code_formater import Formater

class DTT(TT, metaclass=abc.ABCMeta):
    """
    Abstract class for defination data tree
    """
    @abc.abstractmethod 
    def to_string(self, value):
        """Presentation of type in json yaml"""
        pass
        
    @abc.abstractmethod 
    def is_set(self):
        """
        return if structure contain real data
        """
        pass
        
    def get_predicates(self):
        """return dictionary (path->predicate) of predicates containing in this structure"""
        return []


class BaseDTT(DTT, metaclass=abc.ABCMeta):
    """
    Abstract class for defination data tree , that is use for
    description structures flow thrue pipeline
    
    :description:
    Structures may be defined as empty (by empty constructor),
    or with data. If structure is empty, it is supossed that is assigned
    later.    
    """
    def __init__(self):
        self.name = ""
        """Display name of port"""
        self.description = ""
        """Display description of port"""

    def match_type(self, type_tree):
        """
        Returns True, if 'self' is a data tree or a type tree that is subtree of the type tree 'type'.
        """
        return True
        
    def __str__(self):
        """return string description"""
        return "\n".join(self.get_settings_script())

    @abc.abstractmethod 
    def assigne(self, value):
        """
        Assigne appropriate python variable to data     
        """
        pass
        
    @abc.abstractmethod 
    def getter(self):
        """
        Return appropriate python variable to data     
        """
        pass
        
    @property
    def value(self):
        return self.getter()

    @value.setter
    def my_attr(self, value):
        self.assigne(value)
    
    def __lt__(self, other):
        """operators for comaration"""
        if isinstance(other, BaseDTT):
            return Bool(self.value.__lt__(other.value))
        return Bool(self.value.__lt__(other))
        
    def __le__(self, other):
        """operators for comaration"""
        if isinstance(other, BaseDTT):
            return Bool(self.value.__le__(other.value))
        return Bool(self.value.__le__(other))
        
    def __eq__(self, other):
        """operators for comaration"""
        if isinstance(other, BaseDTT):
            return Bool(self.value.__eq__(other.value))
        return Bool(self.value.__eq__(other))
        
    def __ne__(self, other):
        """operators for comaration"""
        if isinstance(other, BaseDTT):
            return Bool(self.value.__ne__(other.value))
        return Bool(self.value.__ne__(other))
        
    def __gt__(self, other):
        """operators for comaration"""
        if isinstance(other, BaseDTT):
            return Bool(self.value.__gt__(other.value))
        return Bool(self.value.__gt__(other))
        
    def __ge__(self, other):
        """operators for comaration"""
        if isinstance(other, BaseDTT):
            return Bool(self.value.__ge__(other.value))
        return Bool(self.value.__ge__(other))
        
    def __and__(self, other):
        if isinstance(other, BaseDTT):
            return Bool(self.value and other.value)
        return Bool(self.value or other)
        
    def __or__(self, other):
        if isinstance(other, BaseDTT):
            return Bool(self.value or other.value)
        return Bool(self.value or other)            

class Int(BaseDTT):
    """
    Integer
    """
    def __init__(self, integer=None):
        self.integer = integer
        """value"""
    
    def to_string(self, value):
        """Presentation of type in json yaml"""
        return str(value)
        
    def get_settings_script(self):
        """return python script, that create instance of this class"""
        if self.integer is None:
            return ["Int()"]
        return ["Int({0})".format(str(self.integer))]
      
    def is_set(self):
        """
        return if structure contain real data
        """
        return  self.integer is not None

    def assigne(self,  value):
        """
        Assigne appropriate python variable to data     
        """
        if isinstance(value, BaseDTT):
            self.integer = int(value.value) 
        else:
            self.integer = int(value) 

    def getter(self):
        """
        Return appropriate python variable to data     
        """
        return self.integer
        
class String(BaseDTT):
    """
    String
    """
    def __init__(self, string=None):
        self.string = string
        """value"""
    
    def to_string(self):
        """Presentation of type in json yaml"""
        return self.string
        
    def get_settings_script(self):
        """return python script, that create instance of this class"""
        if self.string is None:
            return ["String()"]
        return ["String('{0}')".format(self.string)]
      
    def is_set(self):
        """
        return if structure contain real data
        """
        return  self.string is not None
        
    def assigne(self,  value):
        """
        Assigne appropriate python variable to data     
        """
        if isinstance(value, BaseDTT):
            self.string = str(value.value) 
        else:
            self.string = str(value)            

    def getter(self):
        """
        Return appropriate python variable to data     
        """
        return self.string
        
class Float(BaseDTT):
    """
    String
    """
    def __init__(self, float=None):
        self.float = float
        """value"""
    
    def to_string(self):
        """Presentation of type in json yaml"""
        return float 
        
    def get_settings_script(self):
        """return python script, that create instance of this class"""
        if self.float is None:
            return ["Float()"]
        return ["Float({0})".format(str(self.float))]
      
    def is_set(self):
        """
        return if structure contain real data
        """
        return self.float is not None

    def assigne(self,  value):
        """
        Assigne appropriate python variable to data     
        """
        if isinstance(value, BaseDTT):
            self.float = float(value.value) 
        else:
            self.float = float(value)

    def getter(self):
        """
        Return appropriate python variable to data     
        """
        return self.float

class Bool(BaseDTT):
    """
    String
    """
    def __init__(self, bool=None):
        self.bool = bool
        """value"""
    
    def to_string(self):
        """Presentation of type in json yaml"""
        if self.bool:
            return "True"
        return "False"
        
    def get_settings_script(self):
        """return python script, that create instance of this class"""
        if self.bool is None:
            return ["Bool()"]
        if self.bool:
            return ["Bool(True)"]
        return ["Bool(False)"]
      
    def is_set(self):
        """
        return if structure contain real data
        """
        return self.bool is not None

    def assigne(self,  value):
        """
        Assigne appropriate python variable to data     
        """
        if isinstance(value, BaseDTT):
            self.bool = value.value 
        else:
            self.bool = bool(value)

    def getter(self):
        """
        Return appropriate python variable to data     
        """
        return self.bool
        
    def __bool__(self):
        return self.value


class CompositeDTT(DTT, metaclass=abc.ABCMeta):
    """
    Abbstract class od port types, that define user for
    validation and translation to string
    """
    def __init__(self, *args):
        pass
                
    
    @abc.abstractmethod
    def get_settings_script(self):
        """return python script, that create instance of this class"""
        pass
        
    def __str__(self):
        """return string description"""
        return "\n".join(self.get_settings_script())


    @abc.abstractmethod
    def to_string(self, value):
        """Presentation of type in json yaml"""
        pass
    
    @abc.abstractmethod    
    def match_type(self, type_tree):
        """
        Returns True, if 'self' is a data tree or a type tree that is subtree of the type tree 'type'.
        """
        pass
    
    @abc.abstractmethod
    def is_set(self):
        """
        return if structure contain real data
        """
        pass
 
class CompositiIter:
    """Help class for iteration composites"""
    def __init__(self,  composite):
        self.i = 0
        self.c=composite
        
    def __iter__(self):
        return self

    def __next__(self):
        ret = self.c.get_item(self.i)
        if ret is None:
            raise StopIteration()
        else:
            self.i += 1
        return ret
 
class Struct(CompositeDTT):
    """
    Object
    """
    def __init__(self, *args,  **kwargs):
        """Contained type"""
        if len(args) > 0 and isinstance(args[0], dict):
            for name, value in args[0].items():
                setattr(self, name, value)
        for name, value in kwargs.items():
            setattr(self, name, value)
   
    def to_string(self):
        """Presentation of type in json yaml"""
        try:
            res = "{\n"
            first = True
            for name, value in self.__dict__.items():
                if name[:2] == '__' and name[-2:] == '__':
                    continue
                if first:
                    first = False
                else:
                    res += ",\n"
                res += name 
                res += ":"
                res += self.subtype.to_string(value)
                res += "}\n"
        except:
            return None
            
    def get_predicates(self):
        """return dictionary (path->predicate) of predicates containing in this structure"""
        ret=[]
        for name, value in self.__dict__.items():
            if isinstance(value, TT):
                ret.extend(value.get_predicates())
        return ret
            
    def get_settings_script(self):
        """return python script, that create instance of this class"""
        try:
            lines = ["Struct("]
            is_emty=True
            for name in sorted(self.__dict__):
                if name[:2] == '__' and name[-2:] == '__':
                    continue
                is_emty=False
                param = self.__dict__[name].get_settings_script()
                lines.extend(Formater.format_variable(name, param, 4))
            if not is_emty:
                lines[-1] = lines[-1][:-1]
            lines.append(")")
        except Exception as ex:
            raise Exception("Unknown input type " +str(ex))
        return lines
            
    def match_type(self, type_tree):
        """
        Returns True, if 'self' is a data tree or a type tree that is subtree of the type tree 'type'.
        """
        for name, value in self.__dict__.items():
            if name[:2] == '__' and name[-2:] == '__':
                continue
            if not name in type_tree.__dict__:
                return False
            if type(value) is not type(type_tree.__dict__[name]):
                return False
            if isinstance(value, CompositeDTT):
                if not type_tree.__dict__[name].match_type(value):
                    return False
        return True
        
    def is_set(self):
        """
        return if structure contain real data
        """
        for name, value in self.__dict__.items():
            if name[:2] == '__' and name[-2:] == '__':
                continue
            if value is None:
                return False
            if isinstance(value, BaseDTT):
                if not self.__dict__[name].is_set():
                    return False
        return True
        
    def __setattr__(self, name, value): 
        """save assignation"""
        if name not in self.__dict__:
            if isinstance(value, TT):
                self.__dict__[name]=value
            else:
                raise ValueError('Not supported assignation type.')
        elif isinstance(self.__dict__[name], BaseDTT):
            self.__dict__[name].assigne(value)
        elif name[:2] == '__' and name[-2:] == '__':
            self.__dict__[name]=value
        else:
            raise ValueError('Not supported reassignation type.')
            
    def __getattr__(self, name): 
        """save assignation"""
        if name[:2] == '__' and name[-2:] == '__':
            if name in self.__dict__:
                return self.__dict__[name]
            else:
                raise AttributeError(name)
        if name not in self.__dict__:
            raise ValueError('Variable is not assignated.')
        return self.__dict__[name].getter()
        
    def __contains__(self, key):
        return key in self.__dict__

class SortableDTT(CompositeDTT, metaclass=abc.ABCMeta):
    """Sortable composite data tree"""
    
    @abc.abstractmethod
    def sort(self, predicate):
        """return sorted Ensamble accoding set predicate"""
        pass
        
    @abc.abstractmethod
    def select(self, predicate):
        """return selected Ensamble accoding set predicate"""
        pass

class Ensemble(SortableDTT):
    """
    Array
    """
    def __init__(self, subtype, *args):
        self.subtype = subtype
        """iterator possition"""
        self.list = []
        """Items is save internaly as list"""
        if len(args) == 1 and isinstance(args[0], list):
            for value in args[0]:
                self.add_item(value)
        else:
            for arg in args:
                self.add_item(arg)
                
    def add_item(self, value):
        if not isinstance(value, BaseDTT) and \
            not isinstance(value, CompositeDTT):
                raise ValueError('Ensemble must have DTT value type.')
        if self.subtype.match_type(value):
            self.list.append(value)
        else:
            raise ValueError('Not supported ensemble type ({0}).'.format(str(value)))     
    
    def get_predicates(self):
        """return dictionary (path->predicate) of predicates containing in this structure"""
        ret=[]
        for value in self.list:
            if isinstance(value, TT):
                ret.extend(value.get_predicates())
        return ret

    def to_string(self, value):
        """Presentation of type in json yaml"""
        try:
            res = "[\n"
            first = True
            for value in self.list:
                if first:
                    first = False
                else:
                    res += ",\n"
                res += self.value.to_string()
            res += "]\n"
        except:
            return None    
    
    def get_settings_script(self):
        """return python script, that create instance of this class"""
        try:
            lines = ["Ensemble("]
            param = self.subtype.get_settings_script()
            lines.extend(Formater.format_parameter(param, 4))
            for value in self.list:
                param = value.get_settings_script()
                lines.extend(Formater.format_parameter(param, 4))
            lines[-1] = lines[-1][:-1]
            lines.append(")")
        except Exception as ex:
            raise Exception("Unknown input type ({0})".format(str(ex)))
        return lines

    def match_type(self, type_tree):
        """
        Returns True, if 'self' is a data tree or a type tree that is subtree of the type tree 'type'.
        """
        return  self.subtype.match_type(type_tree.subtype)
        
    def is_set(self):
        """
        return if structure contain real data
        """
        for value in self.list:
            if not value.is_set():
                return False
        return True
        
    def __iter__(self):
        return CompositiIter(self)

    def get_item(self, i):       
        if i < len(self.list):
            return self.list[i]
        return None
    
    def sort(self, predicate):
        """return sorted Ensamble accoding set predicate"""
        sorted = Ensemble(self.subtype, self.list)
        sorted.list.sort(key=lambda item: predicate.get_key(item))
        return sorted

    def select(self, predicate):
        """return selected Ensamble accoding set predicate"""
        selected = Ensemble(self.subtype)
        for item in self.list:
            if predicate.get_bool():
                selected.add_item(item)
        return selected
