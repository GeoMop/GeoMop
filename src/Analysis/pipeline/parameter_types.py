import abc

class BaseData(metaclass=abc.ABCMeta):
    """
    Abbstract class od port types, that define user for
    validation and translation to string
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

    def contain(self, data):
        """
        return if structure contain set data
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
        
class Int(BaseData):
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
        if isinstance(value, BaseData):
            self.integer = int(value.value) 
        else:
            self.integer = int(value) 

    def getter(self):
        """
        Return appropriate python variable to data     
        """
        return self.integer
        
class String(BaseData):
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
        if isinstance(value, BaseData):
            self.string = str(value.value) 
        else:
            self.string = str(value)            

    def getter(self):
        """
        Return appropriate python variable to data     
        """
        return self.string
        
class Float(BaseData):
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
        if isinstance(value, BaseData):
            self.float = float(value.value) 
        else:
            self.float = float(value)

    def getter(self):
        """
        Return appropriate python variable to data     
        """
        return self.float

class CompositeData(metaclass=abc.ABCMeta):
    """
    Abbstract class od port types, that define user for
    validation and translation to string
    """
    def __init__(self, subtype, *args):
        self.subtype = subtype
        """Contained type"""
        self.list = []
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
            
    def contain(self, data):
        """
        return if structure contain set data
        """
        return True
        
    def is_set(self):
        """
        return if structure contain real data
        """
        return True
 
class Struct(CompositeData):
    """
    Object
    """
    def __init__(self, **kwargs):
        """Contained type"""
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
            
    def contain(self, data):
        """
        return if structure contain set data
        """
        for name, value in data.__dict__.items():
            if not name in self.__dict__:
                return False
            if type(value) is not type(self.__dict__[name]):
                return False
            if isinstance(value, CompositeData):
                if not self.__dict__[name].contain(value):
                    return False
        return True
        
    def is_set(self):
        """
        return if structure contain real data
        """
        for name, value in self.__dict__.items():
            if value is None:
                return False
            if isinstance(value, BaseData):
                if not self.__dict__[name].is_set():
                    return False
        return True
        
    def __setattr__(self, name, value): 
        """save assignation"""
        if name not in self.__dict__:
            if isinstance(value, BaseData) or isinstance(value, CompositeData):
                self.__dict__[name]=value
            else:
                raise ValueError('Not supported assignation type.')
        elif isinstance(self.__dict__[name], BaseData):
            self.__dict__[name].assigne(value)
        else:
            raise ValueError('Not supported reassignation type.')
            
    def __getattr__(self, name): 
        """save assignation"""
        if name not in self.__dict__:
            raise ValueError('Variable is not assignated.')
        return self.__dict__[name].getter()

class List(CompositeData):
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
