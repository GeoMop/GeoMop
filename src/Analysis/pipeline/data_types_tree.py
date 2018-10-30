import abc
import copy
import math
from .generic_tree import TT, GDTT
from .code_formater import Formater

class DTT(TT, metaclass=abc.ABCMeta):
    """
    Abstract class for defination data tree
    """
    @abc.abstractmethod 
    def _to_string(self):
        """Presentation of type in json yaml"""
        pass
        
    @abc.abstractmethod 
    def _is_set(self):
        """
        return if structure contain real data
        """
        pass
        
    def duplicate(self):
        """
        make deep copy
        """
        pass

class BaseDTT(DTT, metaclass=abc.ABCMeta):
    """
    Abstract class for defination data tree , that is use for
    description structures flow thrue pipeline
    
    :description:
    Structures may be defined as empty (by empty constructor),
    or with data. If structure is empty, it is supossed that is assigned
    later.    
    """
    name = ""
    """Display name of variable type"""
    description = ""
    """Display description of variable type"""

    def __init__(self):
        pass

    def _match_type(self, type_tree):
        """
        Returns True, if 'self' is a data tree or a type tree that is subtree of the type tree 'type'.
        """
        return type_tree.__class__.__name__ == self.__class__.__name__
        
    def __str__(self):
        """return string description"""
        return "\n".join(self._get_settings_script())

    @abc.abstractmethod 
    def _assigne(self, value):
        """
        Assigne appropriate python variable to data     
        """
        pass
        
    @abc.abstractmethod 
    def _getter(self):
        """
        Return appropriate python variable to data     
        """
        pass
        
    @property
    def value(self):
        return self._getter()

    @value.setter
    def value(self, value):
        self._assigne(value)
        
    def _get_unique_text(self, set=False):
        """return unique identifier that describe this variable"""
        if set:
            return self.__class__.__name__ + "#" + self._to_string()
        return self.__class__.__name__
    
    def __lt__(self, other):
        """operators for comparation"""
        if isinstance(other, BaseDTT):
            return Bool(self.value.__lt__(other.value))
        return Bool(self.value.__lt__(other))
        
    def __le__(self, other):
        """operators for comparation"""
        if isinstance(other, BaseDTT):
            return Bool(self.value.__le__(other.value))
        return Bool(self.value.__le__(other))
        
    def __eq__(self, other):
        """operators for comparation"""
        if isinstance(other, BaseDTT):
            return Bool(self.value.__eq__(other.value))
        return Bool(self.value.__eq__(other))
        
    def __ne__(self, other):
        """operators for comparation"""
        if isinstance(other, BaseDTT):
            return Bool(self.value.__ne__(other.value))
        return Bool(self.value.__ne__(other))
        
    def __gt__(self, other):
        """operators for comparation"""
        if isinstance(other, BaseDTT):
            return Bool(self.value.__gt__(other.value))
        return Bool(self.value.__gt__(other))
        
    def __ge__(self, other):
        """operators for comparation"""
        if isinstance(other, BaseDTT):
            return Bool(self.value.__ge__(other.value))
        return Bool(self.value.__ge__(other))
        
    def __and__(self, other):
        if isinstance(other, BaseDTT):
            return Bool(self.value and other.value)
        return Bool(self.value and other)
        
    def __or__(self, other):
        if isinstance(other, BaseDTT):
            return Bool(self.value or other.value)
        return Bool(self.value or other)            

class Int(BaseDTT):
    """
    Integer
    """
    name = "Integer"
    """Display name of variable type"""
    description = "Wrapper for standart python integer variable"    
    """Display description of variable type"""
    
    def __init__(self, integer=None):
        self.__integer = integer
        """value"""
        
    def duplicate(self):
        """
        make deep copy
        """
        return Int(self.__integer)
    
    def _to_string(self):
        """Presentation of type in json yaml"""
        return str(self.__integer)
        
    def _get_settings_script(self):
        """return python script, that create instance of this class"""
        if self.__integer is None:
            return ["Int()"]
        return ["Int({0})".format(str(self.__integer))]
      
    def _is_set(self):
        """
        return if structure contain real data
        """
        return  self.__integer is not None

    def _assigne(self,  value):
        """
        Assigne appropriate python variable to data     
        """
        if isinstance(value, BaseDTT):
            self.__integer = int(value.value) 
        else:
            self.__integer = int(value) 

    def _getter(self):
        """
        Return appropriate python variable to data     
        """
        return self.__integer
        
class String(BaseDTT):
    """
    String
    """
    def __init__(self, string=None):
        self.__string = string
        """value"""
        
    def duplicate(self):
        """
        make deep copy
        """
        return String(self.__string)
    
    def _to_string(self):
        """Presentation of type in json yaml"""
        return self.__string
        
    def _get_settings_script(self):
        """return python script, that create instance of this class"""
        if self.__string is None:
            return ["String()"]
        return ["String('{0}')".format(self.__string)]
      
    def _is_set(self):
        """
        return if structure contain real data
        """
        return  self.__string is not None
        
    def _assigne(self,  value):
        """
        Assigne appropriate python variable to data     
        """
        if isinstance(value, BaseDTT):
            self.__string = str(value.value) 
        else:
            self.__string = str(value)            

    def _getter(self):
        """
        Return appropriate python variable to data     
        """
        return self.__string
        
class Float(BaseDTT):
    """
    Float
    """
    name = "Float"
    """Display name of variable type"""
    description = "Wrapper for standart python float variable"    
    """Display description of variable type"""

    def __init__(self, float_value=None):
        self.__float = None
        """value"""
        if float_value is not None:
            self.__float = float(float_value)

    def duplicate(self):
        """
        make deep copy
        """
        return Float(self.__float)
    
    def _to_string(self):
        """Presentation of type in json yaml"""
        return str(self.__float )
        
    def _get_settings_script(self):
        """return python script, that create instance of this class"""
        if self.__float is None:
            return ["Float()"]
        s = str(self.__float)
        if not math.isfinite(self.__float):
            s = "'{}'".format(s)
        return ["Float({0})".format(s)]
      
    def _is_set(self):
        """
        return if structure contain real data
        """
        return self.__float is not None

    def _assigne(self,  value):
        """
        Assigne appropriate python variable to data     
        """
        if isinstance(value, BaseDTT):
            self.__float = float(value.value) 
        else:
            self.__float = float(value)

    def _getter(self):
        """
        Return appropriate python variable to data     
        """
        return self.__float

class Bool(BaseDTT):
    """
    Bool
    """
    name = "Bool"
    """Display name of variable type"""
    description = "Wrapper for standart python Boolean variable"    
    """Display description of variable type"""

    def __init__(self, bool=None):
        self.__bool = bool
        """value"""
        
    def duplicate(self):
        """
        make deep copy
        """
        return Bool(self.__bool)
    
    def _to_string(self):
        """Presentation of type in json yaml"""
        if self.__bool:
            return "True"
        return "False"
        
    def _get_settings_script(self):
        """return python script, that create instance of this class"""
        if self.__bool is None:
            return ["Bool()"]
        if self.__bool:
            return ["Bool(True)"]
        return ["Bool(False)"]
      
    def _is_set(self):
        """
        return if structure contain real data
        """
        return self.__bool is not None

    def _assigne(self,  value):
        """
        Assigne appropriate python variable to data     
        """
        if isinstance(value, BaseDTT):
            self.__bool = value.value 
        else:
            self.__bool = bool(value)

    def _getter(self):
        """
        Return appropriate python variable to data     
        """
        return self.__bool
        
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
    def _get_settings_script(self):
        """return python script, that create instance of this class"""
        pass
        
    def __str__(self):
        """return string description"""
        return "\n".join(self._get_settings_script())


    @abc.abstractmethod
    def _to_string(self):
        """Presentation of type in json yaml"""
        pass
    
    @abc.abstractmethod    
    def _match_type(self, type_tree):
        """
        Returns True, if 'self' is a data tree or a type tree that is subtree of the type tree 'type'.
        """
        pass
    
    @abc.abstractmethod
    def _is_set(self):
        """
        return if structure contain real data
        """
        pass
 
class CompositiIter:
    """Help class for iteration composites"""
    def __init__(self,  composite):
        self.__i = 0
        self.__c=composite
        
    def __iter__(self):
        return self

    def __next__(self):
        ret = self.__c.get_item(self.__i)
        if ret is None:
            raise StopIteration()
        else:
            self.__i += 1
        return ret
 
class Struct(CompositeDTT):
    """
    Object
    """
    name = "Struct"
    """Display name of variable type"""
    description = "Composite structure variable"    
    """Display description of variable type"""

    def __init__(self, *args,  **kwargs):
        """Contained type"""
        if len(args) > 0 and isinstance(args[0], dict):
            for name, value in args[0].items():
                setattr(self, name, value)
        for name, value in kwargs.items():
            setattr(self, name, value)
            
    def duplicate(self):
        """
        make deep copy
        """
        new_dict={}
        for name, value in self.__dict__.items():
            if name[:2] == '__' and name[-2:] == '__':
                continue
            if isinstance(value, DTT):
                new_dict[name] = value.duplicate()
            else:
                new_dict[name]=copy.deepcopy(value)
        return Struct(new_dict)
   
    def _to_string(self):
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
                res += value._to_string()
                res += "}\n"
        except:
            return None
        return res
            
    def _get_settings_script(self):
        """return python script, that create instance of this class"""
        try:
            lines = ["Struct("]
            is_emty=True
            for name in sorted(self.__dict__):
                if name[:2] == '__' and name[-2:] == '__':
                    continue
                is_emty=False
                param = self.__dict__[name]._get_settings_script()
                lines.extend(Formater.format_variable(name, param, 4))
            if not is_emty:
                lines[-1] = lines[-1][:-1]
            lines.append(")")
        except Exception as ex:
            raise Exception("Unknown input type " +str(ex))
        return lines
        
    def _get_unique_text(self, set=False):
        """return unique identifier that describe this variable"""
        ret = self.__class__.__name__
        for name in sorted(self.__dict__):
            if name[:2] == '__' and name[-2:] == '__':
                continue
            ret += "#" + name + "#" + self.__dict__[name]._get_unique_text(set)
        return ret
            
    def _match_type(self, type_tree):
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
                if not type_tree.__dict__[name]._match_type(value):
                    return False
        return True
        
    def _get_generics(self):
        """return list of generic contained in this structure"""
        ret = []
        for name, value in self.__dict__.items():
            if name[:2] == '__' and name[-2:] == '__':
                continue
            if isinstance(value, GDTT):
                ret.append(value)
                continue
            if isinstance(value, TT):
                ret.extend(value._get_generics())
        return ret
        
    def _is_set(self):
        """
        return if structure contain real data
        """
        for name, value in self.__dict__.items():
            if name[:2] == '__' and name[-2:] == '__':
                continue
            if value is None:
                return False
            if isinstance(value, DTT):
                if not self.__dict__[name]._is_set():
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
            self.__dict__[name]._assigne(value)
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
            raise ValueError("Variable '{0}' is not assignated.".format(name))
        return self.__dict__[name]._getter()
        
    def __contains__(self, key):
        return key in self.__dict__

class Tuple(CompositeDTT):
    """
    Object
    """
    name = "Tuple"
    """Display name of variable type"""
    description = "Composite tuple variable like python tuple"    
    """Display description of variable type"""

    def __init__(self, *args):
        """Contained type"""
        self._list = []
        for arg in args:
            if isinstance(arg, TT):
                self._list.append(arg)
            else:
                raise ValueError('Not supported assignation type.')
                
    def duplicate(self):
        """
        make deep copy
        """
        new_list=[]
        for value in self._list:
            if isinstance(value, DTT):
                new_list.append(value.duplicate())
            else:
                new_list.append(copy.deepcopy(value))
        return Tuple(*new_list)
   
    def _to_string(self, value):
        """Presentation of type in json yaml"""
        try:
            res = "(\n"
            first = True
            for value in self._list:
                if first:
                    first = False
                else:
                    res += ",\n"
                res += value._to_string()
            res += ")\n"
        except:
            return None
        return res
    
    def _get_settings_script(self):
        """return python script, that create instance of this class"""
        try:
            lines = ["Tuple("]
            for value in self._list:
                param = value._get_settings_script()
                lines.extend(Formater.format_parameter(param, 4))
            lines[-1] = lines[-1][:-1]
            lines.append(")")
        except Exception as ex:
            raise Exception("Unknown input type ({0})".format(str(ex)))
        return lines
        
    def _get_unique_text(self, set=False):
        """return unique identifier that describe this variable"""
        ret = self.__class__.__name__
        for value in self._list:
            ret += "#" + value._get_unique_text(set)
        return ret
            
    def _match_type(self, type_tree):
        """
        Returns True, if 'self' is a data tree or a type tree that is subtree of the type tree 'type'.
        """
        if len(self._list) != len(type_tree._list):
                return False
        for i in range(0, len(self._list)):
            if type(self._list[i]) is not type(type_tree._list[i]):
                return False
            if isinstance(self._list[i], CompositeDTT):
                if not type_tree._list[i]._match_type(self._list[i]):
                    return False
        return True
        
    def _get_generics(self):
        """return list of generic contained in this structure"""
        ret = []
        for item in self._list:
            if isinstance(item, GDTT):
                ret.append(item)
                continue
            if isinstance(item, TT):
                ret.extend(item._get_generics())
        return ret
        
    def _is_set(self):
        """
        return if structure contain real data
        """
        for item in self._list:
            if item is None:
                return False
            if isinstance(item, DTT):
                if not item._is_set():
                    return False
        return True
        
    def __getitem__(self, i):       
        if i < len(self._list):
            return self._list[i]
        raise IndexError()
        
    def __setitem__(self, i,  value): 
        """save assignation"""
        if i >= len(self._list):
            raise IndexError()
        if isinstance(self._list[i], BaseDTT):
            self._list[i]._assigne(value)
            return
        raise ValueError('Not supported reassignation type.')
        
    def __len__(self):
        return len(self._list)

class ListDTT(CompositeDTT, metaclass=abc.ABCMeta):
    """Sortable composite data tree"""
    
    def __init__(self, subtype, *args):
        self.subtype = subtype
        """iterator possition"""
        self._list = []
    
    @abc.abstractmethod
    def _get_template(self, func_name, adaptor=None):
        """return template of nested structure"""
        pass

    @abc.abstractmethod
    def each(self):
        """Adapt list items structure"""
        pass
        
    def _get_unique_text(self, set=False):
        """return unique identifier that describe this variable"""
        ret = self.__class__.__name__ + "#" + self.subtype._get_unique_text()
        if set:
            for value in self._list:
                ret += "#" + value._get_unique_text(set)
        return ret

        
class SortableDTT(ListDTT, metaclass=abc.ABCMeta):
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
    name = "Ensemble"
    """Display name of variable type"""
    description = "Not ordered type list"    
    """Display description of variable type"""

    def __init__(self, subtype, *args):
        super(Ensemble, self).__init__(subtype, *args)
        """Items is save internaly as list"""
        if len(args) == 1 and isinstance(args[0], list):
            for value in args[0]:
                self.add_item(value)
        else:
            for arg in args:
                self.add_item(arg)
                
    def duplicate(self):
        """
        make deep copy
        """
        new_list=self._duplicate_list()
        return Ensemble(*new_list)

    def _duplicate_list(self):
        new_list=[]
        for value in self._list:
            if isinstance(value, DTT):
                new_list.append(value.duplicate())
            else:
                new_list.append(copy.deepcopy(value))
        return new_list

                
    def add_item(self, value):
        if not isinstance(value, BaseDTT) and \
            not isinstance(value, CompositeDTT):
                if isinstance(value, GDTT):
                    self._list.append(value)
                    return
                raise ValueError('Ensemble must have DTT value type.')
        if self.subtype._match_type(value):
            self._list.append(value)
        else:
            raise ValueError('Not supported ensemble type ({0}).'.format(str(value)))     

    def _to_string(self):
        """Presentation of type in json yaml"""
        try:
            res = "[\n"
            first = True
            for value in self._list:
                if first:
                    first = False
                else:
                    res += ",\n"
                res += value._to_string()
            res += "]\n"
        except:
            return None
        return res
    
    def _get_settings_script(self):
        """return python script, that create instance of this class"""
        try:
            lines = [self.__class__.__name__+"("]
            param = self.subtype._get_settings_script()
            lines.extend(Formater.format_parameter(param, 4))
            for value in self._list:
                param = value._get_settings_script()
                lines.extend(Formater.format_parameter(param, 4))
            lines[-1] = lines[-1][:-1]
            lines.append(")")
        except Exception as ex:
            raise Exception("Unknown input type ({0})".format(str(ex)))
        return lines

    def _match_type(self, type_tree):
        """
        Returns True, if 'self' is a data tree or a type tree that is subtree of the type tree 'type'.
        """
        return  self.subtype._match_type(type_tree.subtype)
        
    def _is_set(self):
        """
        return if structure contain real data
        """
        for value in self._list:
            if not value._is_set():
                return False
        return True
    
    def _get_generics(self):
        """
        return list of generic contained in this structure
        
        Ensemble can have generic type only in value.        
        """
        ret = []
        for value in self._list:
            if isinstance(value, GDTT):
                ret.append(value)
                continue
            if isinstance(value, TT):
                ret.extend(value._get_generics())
        return ret

    def __iter__(self):
        return CompositiIter(self)
        
    def __len__(self):
        return len(self._list)

    def get_item(self, i):       
        if i < len(self._list):
            return self._list[i]
        return None
    
    def each(self, adapter):
        """Adapt list items structure"""
        new_subtype = adapter._get_adapted_item(self.subtype)
        adapted = Ensemble(new_subtype)
        for item in self._list:
            new_item = adapter._get_adapted_item(item)
            adapted.add_item(new_item)
        return adapted
    
    def sort(self, key_selector):
        """return sorted Sequence accoding set predicate"""
        sorted = Sequence(self.subtype, self._list)
        sorted._list.sort(key=lambda item: key_selector._get_key(item))
        return sorted

    def select(self, predicate):
        """return selected Ensamble accoding set predicate"""
        selected = Ensemble(self.subtype)
        for item in self._list:
            if predicate._get_bool(item):
                selected.add_item(item)
        return selected
    
    def _get_template(self, func_name, adapter=None):
        """return validation template returned by specified function
        name. Return None if not return defined"""
        if func_name == "each":
            try:
                subtype = adapter._get_adapted_item(self.subtype) 
            except Exception as error:
                return ["Get adapted item error: " + str(error)], None
            return [], Ensemble(subtype)
        if func_name == "select":
            return [], Ensemble(self.subtype)
        if func_name == "sort":
            return [], Sequence(self.subtype)
        return ["Unknown template function {0}".format(func_name)], None        

class Sequence(Ensemble):
    name = "Sequence"
    """Display name of variable type"""
    description = "Ordered type list"    
    """Display description of variable type"""

    """Display name of variable type"""
    description = "Ordered type list"    
    """Display description of variable type"""
        
    def __init__(self, subtype, *args):
        super(Sequence, self).__init__(subtype, *args)
        
    def duplicate(self):
        """
        make deep copy
        """
        new_list=self._duplicate_list()
        return Sequence(*new_list)

    def head(self):
        if len(self._list) > 0:
            return self._list[0]
        else:
            return self.subtype
        
    def tail(self):
        if len(self._list) > 0:
            return self._list[-1]
        else:
            return self.subtype

    def select(self, predicate):
        """return selected Ensamble accoding set predicate"""
        selected = Sequence(self.subtype)
        for item in self._list:
            if predicate._get_bool(item):
                selected.add_item(item)
        return selected
        
    def each(self, adapter):
        """Adapt list items structure"""
        new_subtype = adapter._get_adapted_item(self.subtype)
        adapted = Sequence(new_subtype)
        for item in self._list:
            new_item = adapter._get_adapted_item(item)
            adapted.add_item(new_item)
        return adapted
        
    def _get_template(self, func_name, adapter=None):
        """return error and  validation template returned by specified function
        name. Return None if not return defined"""
        if func_name == "each":
            try:
                subtype = adapter._get_adapted_item(self.subtype) 
            except Exception as error:
                return ["Get adapted item error: " + str(error)], None
            return [], Sequence(subtype)
        if func_name == "select" or func_name == "sort":
            return [],  Sequence(self.subtype)
        if func_name == "tail" or func_name == "head":
            return [], self.subtype
        return ["Unknown template function {0}".format(func_name)], None
