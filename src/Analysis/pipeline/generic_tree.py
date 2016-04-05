from .data_types_tree import DTT

class GDTT(DTT):
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
          
    def set_path(self, value):
        self._path = value
           
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
        
class GDTTFunc():
    """
    Class for save function code with GDTT variables
    """
    def __init__(self, *args):
        """test"""
        pass
    
