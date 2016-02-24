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
        
class String(BaseData):
    """
    String
    """
    def __init__(self, string=None):
        self.string = string
        """value"""
    
    def to_string(self):
        """Presentation of type in json yaml"""
        return string
      
    def is_set(self):
        """
        return if structure contain real data
        """
        return  self.integer is not None
        
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


class CompositeType(BaseData, metaclass=abc.ABCMeta):
    """
    Abbstract class od port types, that define user for
    validation and translation to string
    """
    def __init__(self, subtype, *args):
        self.subtype = subtype
        """Contained type"""
        self.list = []
        for arg in args:
            self.list.append(args)
   
    @abc.abstractmethod 
    def to_string(self, value):
        """Presentation of type in json yaml"""
        pass
    
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

class DictionaryType(CompositeType):
    """
    Dictionary
    """
    def __init__(self, subtype=None):
        self.comp_name = "Dictionary"
        """Display name of port"""
        self.comp_description = "Dictionary"
        """Display description of port"""
        self.subtype = subtype
        """Contained type"""
        
    @abc.abstractmethod 
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

    @abc.abstractmethod
    def validate(self, value):
        """
        validate value, and return string with problem        
        
        :return: None if validation is ok
        """
        if self.subtype is None:
            return "Typ contained in {0} type must be set".format(self.comp_name)
        for subvalue in value:
            res = self.subtype.validate(value[subvalue])
            if res is not None:
                return res
        return None
        
class ArrayType(CompositeType):
    """
    Array
    """
    
    def __init__(self, subtype=None):
        self.comp_name = "Array"
        """Display name of port"""
        self.comp_description = "Array"
        """Display description of port"""
        self.subtype = subtype
        """Contained type"""
        
    @abc.abstractmethod 
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

    @abc.abstractmethod
    def validate(self, value):
        """
        validate value, and return string with problem        
        
        :return: None if validation is ok
        """
        if self.subtype is None:
            return "Typ contained in {0} type must be set".format(self.comp_name)
        for subvalue in value:
            res = self.subtype.validate(subvalue)
            if res is not None:
                return res
        return None
