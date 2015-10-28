"""Classes for handing messages over net"""

import abc
import communication.installation as dinstall

class OutputComm(metaclass=abc.ABCMeta):
    """Ancestor of output communication classes"""
    
    def __init__(self, host, mj_name):
        self.host=host
        """ip or dns of host for communication"""
        self.installation = dinstall.Installation(mj_name)
        """installation where is copied files"""
    
    def set_install_params(self, python_exec,  scl_enable_exec):
        self.installation.set_install_params(python_exec,  scl_enable_exec)
        
    def install_job_libs(self):
        """Install libs for jobs"""
        self.installation.install_job_libs()
    
    @abc.abstractmethod
    def connect(self):
        """connect session"""
        pass
    
    @abc.abstractmethod
    def disconnect(self):
        """disconnect session"""
        pass

    @abc.abstractmethod
    def install(self):
        """copy installation"""
        pass
        
    @abc.abstractmethod
    def exec_(self,  command, mj_name, mj_id):
        """run command"""
        pass

    @abc.abstractmethod
    def send(self,  msg):
        """send json message"""
        pass
        
    @abc.abstractmethod
    def receive(self):
        """receive json message"""
        pass
        
    @abc.abstractmethod
    def download_result(self):
        """download result files from installation folder"""
        pass

class InputComm(metaclass=abc.ABCMeta):
    """Input communication abstract class"""
    
    def __init__(self):
        pass
    
    @abc.abstractmethod
    def connect(self):
        """connect session"""
        pass
        
    @abc.abstractmethod
    def send(self, msg):
        """send message to output"""
        pass
    
    @abc.abstractmethod
    def receive(self):
        """
        Receive message from input
        
        Function wait for answer for set time in seconds
        """
        pass
    
    @abc.abstractmethod
    def disconnect(self):
        """disconnect session"""
        pass


        


            

