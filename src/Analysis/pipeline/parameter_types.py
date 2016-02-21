import abc
import re
from copy import deepcopy

class PortTypes:
    """Container for base, composite and used types"""
    def __init__(self):
        self.base_types = []
        """dictionary of base types"""
        self.base_types.add(IntType())
        self.base_types.add(StringType())
        
        self.composite_types = []
        """dictionary of composite types"""
        self.composite_types.add(IntType())
        self.composite_types.add(StringType())
        
        self.used_types = deepcopy(self.base_types)
        """Base and composed class for assignation"""
  
    def _get_composite_type(self, name):
        """return new composite typy from set type"""
        for type in self.composite_types:
            if name == type.name:
                return deepcopy(type)
        return None
    
    def _get_composed_type(self, name):
        """get new type compose from composite type and subtype"""
        res = re.search(r'^([^<])<(*+)>$',name)
        if res is None:
            return None
        comp_type = self._get_composite_type(res.group(1))
        if comp_type is None:   
            return None
        sub_type = self._get_existing_used_type(res.group(2))
        if sub_type is None:
            sub_type = self._get_composed_type(res.group(2))
            if sub_type is None:
                return None
        comp_type.set_subtype(sub_type)
        return comp_type
            
    def _get_existing_used_type(self, name):
        """try find type accoding set name"""
        for type in self.used_types:
            if name == type.name:
                return type
        return None
     
    def  get_used_type(self, name):
        """try find type accoding set name or create new type"""
        type = self._get_existing_used_type(name)
        if type is not None:
            return type
        type = self._get_composed_type(name)  
        self.used_types.add(type)
        return type 

    def  get_type_list(self):
        """get list all types"""
        list = {}
        for type in self.used_types:
            list[type.name]=type    
        for type in self.composite_types:
            list[type.name]=type    
        return list

class BaseType(metaclass=abc.ABCMeta):
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
      
    @abc.abstractmethod 
    def validate(self, value):
        """
        validate value, and return string with problem        
        
        :return: None if validation is ok
        """
        pass
        
class IntType(BaseType):
    """
    Integer
    """
    def __init__(self):
        self.name = "int"
        """Display name of port"""
        self.description = "Integer"
        """Display description of port"""
    
    def to_string(self, value):
        """Presentation of type in json yaml"""
        return str(value)
      
    @abc.abstractmethod 
    def validate(self, value):
        """
        validate value, and return string with problem        
        
        :return: None if validation is ok
        """
        try:
            ret = str(value)
            ret = int(value)
        except Exception as err:
            return str(err)
        return None
        
class StringType(BaseType):
    """
    String
    """
    def __init__(self):
        self.name = "string"
        """Display name of port"""
        self.description = "String"
        """Display description of port"""
    
    def to_string(self, value):
        """Presentation of type in json yaml"""
        return value
      
    @abc.abstractmethod 
    def validate(self, value):
        """
        validate value, and return string with problem        
        
        :return: None if validation is ok
        """
        try:
            ret = str(value)
        except Exception as err:
            return str(err)
        return None

class CompositeType(BaseType, metaclass=abc.ABCMeta):
    """
    Abbstract class od port types, that define user for
    validation and translation to string
    """
    def __init__(self, subtype=None):
        self.comp_name = ""
        """Display name of port"""
        self.comp_description = ""
        """Display description of port"""
        self.subtype = subtype
        """Contained type"""
        
    def set_subtype(self, subtype):        
       self.subtype = subtype
       
    @property
    def name(self):
        if self.subtype is None:
            return self.comp_name + "<None>"
        return self.comp_name + "<" + self.subtype.name + ">"

    @property
    def description(self):
        if self.subtype is None:
            return self.comp_description + "<None>"
        return self.comp_description + "<" + self.subtype.description + ">"
    
    @abc.abstractmethod 
    def to_string(self, value):
        """Presentation of type in json yaml"""
        pass
    
    @abc.abstractmethod
    def validate(self, value):
        """
        validate value, and return string with problem        
        
        :return: None if validation is ok
        """
        pass
        
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
