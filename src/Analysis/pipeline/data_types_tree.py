import abc

class BaseDTT(metaclass=abc.ABCMeta):
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
    
    @abc.abstractmethod 
    def to_string(self, value):
        """Presentation of type in json yaml"""
        pass

    def match_type(self, type_tree):
        """
        Returns True, if 'self' is a data tree or a type tree that is subtree of the type tree 'type'.
        """
        return True
        
    @abc.abstractmethod 
    def is_set(self):
        """
        return if structure contain real data
        """
        pass
    
    @abc.abstractmethod 
    def assigne(self):
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
      
    def is_set(self):
        """
        return if structure contain real data
        """
        return  self.float is not None

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

class CompositeDTT(metaclass=abc.ABCMeta):
    """
    Abbstract class od port types, that define user for
    validation and translation to string
    """
    def __init__(self, subtype, *args):
        self.subtype = subtype
        """Contained type"""
        self.list = []
        if len(args) == 1 and isinstance(args[0], list):
            for value in args[0]:
                self.list.append(value)
        else:
            for arg in args:
                self.list.append(arg)
   
    @abc.abstractmethod 
    def merge(self, composite):
        """merge to composite types of same type"""
        pass
        
    @abc.abstractmethod 
    def reduce_values(self, *values):
        """delete all values diferent from set"""
        pass

    def add(self, *values):
        """add values to composite"""
        for arg in values:
            self.list.append(arg)
    
    def to_string(self, value):
        """Presentation of type in json yaml"""
        if self.subtype is None:
            return None
        try:
            res = "[\n"
            first = True
            for subvalue in value:
                if first:
                    first = False
                else:
                    res += ",\n"
                res += self.subtype.to_string(subvalue)
            res += "]\n"
        except:
            return None    
            
    def match_type(self, type_tree):
        """
        Returns True, if 'self' is a data tree or a type tree that is subtree of the type tree 'type'.
        """
        return True
        
    def is_set(self):
        """
        return if structure contain real data
        """
        return True
 
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
   
    def merge(self, composite):
        """merge to composite types of same type"""
        for name, value in composite.__dict__.items():
            setattr(self, name, value)
        
    def reduce_values(self, *values):
        """delete all values diferent from set"""
        dell_list=[]
        for name, value in self.__dict__.items():
            if value not in values: 
                dell_list.append(name)
        for name in dell_list:
            delattr(self, name)

    def reduce_keys(self, *values):
        """delete all keys diferent from set"""
        dell_list=[]
        for name, value in self.__dict__.items():
            if name not in values: 
                dell_list.append(name)
        for name in dell_list:
            delattr(self, name)

    def add(self, **values):
        """add values to composite"""
        for name, value in values.items():
            setattr(self, name, value)
    
    def to_string(self, value):
        """Presentation of type in json yaml"""
        if self.subtype is None:
            return None
        try:
            res = "{\n"
            first = True
            for subvalue in value:
                if first:
                    first = False
                else:
                    res += ",\n"
                res += subvalue 
                res += ":"
                res += self.subtype.to_string(value[subvalue])
            res += "}\n"
        except:
            return None
            
    def match_type(self, type_tree):
        """
        Returns True, if 'self' is a data tree or a type tree that is subtree of the type tree 'type'.
        """
        for name, value in self.__dict__.items():
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
            if value is None:
                return False
            if isinstance(value, BaseDTT):
                if not self.__dict__[name].is_set():
                    return False
        return True
        
    def __setattr__(self, name, value): 
        """save assignation"""
        if name not in self.__dict__:
            if isinstance(value, BaseDTT) or isinstance(value, CompositeDTT):
                self.__dict__[name]=value
            else:
                raise ValueError('Not supported assignation type.')
        elif isinstance(self.__dict__[name], BaseDTT):
            self.__dict__[name].assigne(value)
        else:
            raise ValueError('Not supported reassignation type.')
            
    def __getattr__(self, name): 
        """save assignation"""
        if name not in self.__dict__:
            raise ValueError('Variable is not assignated.')
        return self.__dict__[name].getter()

class List(CompositeDTT):
    """
    Array
    """
    def __init__(self, subtype, *args):
        super(List, self).__init__()
   
    def merge(self, composite):
        """merge to composite types of same type"""
        for arg in composite.list:
                self.list.append(arg)
        
    def reduce_values(self, *values):
        """delete all values diferent from set"""
        new_list=[]
        for arg in self.list:
            if arg in values: 
                new_list.append(arg)
        self.list=new_list
