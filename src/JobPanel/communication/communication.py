"""Classes for handing messages over net"""

import abc
import communication.installation as dinstall

class OutputComm(metaclass=abc.ABCMeta):
    """Ancestor of output communication classes"""
    
    def __init__(self, host, mj_name, an_name):
        self.host=host
        """ip or dns of host for communication"""
        self.installation = dinstall.Installation(mj_name, an_name)
        """installation where is copied files"""
       
    def set_version_params(self, app_version, data_version):
        self.installation.set_version_params(app_version, data_version)
        
    def get_instalation_fails_mess(self):
        return self.installation.instalation_fails_mess
        
    def lock_installation(self):
        """Set installation locks, return if should installation continue"""
        self.installation.lock_installation()
        
    def unlock_installation(self):
        """Unset installation locks"""
        self.installation.unlock_installation()
        
    def install_job_libs(self):
        """Install libs for jobs"""
        self.installation.install_job_libs()
        
    def delete(self):
        """delete all app data for current multijob"""
        self.installation.delete()
    
    @abc.abstractmethod    
    def isconnected(self):
        """Connection is opened"""
        pass
    
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
    def exec_(self,  command, mj_id):
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
        
    @abc.abstractmethod
    def save_state(self, state):
        """save state to variable"""
        pass
        
    @abc.abstractmethod
    def load_state(self, state):
        """load state from variable"""
        pass
        
    @abc.abstractmethod
    def is_running_next(self):
        """Return if next communicator run"""
        pass
        
    @abc.abstractmethod
    def kill_next(self):
        """kill next communicator"""
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
    def isconnected(self):
        """Connection is opened"""
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
        
    @abc.abstractmethod
    def save_state(self, state):
        """save state to variable"""
        pass
        
    @abc.abstractmethod
    def load_state(self, state):
        """load state from variable"""
        pass            

