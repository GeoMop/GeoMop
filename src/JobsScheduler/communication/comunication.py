"""Classes for handing messages over net"""

import abc

class OutputComm(metaclass=abc.ABCMeta):
    """Ancestor of output communication classes"""
    
    def __init__(self, host):
        self.host=host
        """ip or dns of host for communication"""
        self.install_path=None
        """path where is copied files"""
    
    @abc.abstractmethod
    def connect(self):
        """connect session"""
        pass
    
    @abc.abstractmethod
    def disconnect(self):
        """disconnect session"""
        pass

    @abc.abstractmethod
    def install(self,  installation,  path="./"):
        """copy installation"""
        self.install_path = path
        
    @abc.abstractmethod
    def exec_(self,  command):
        """run command"""
        pass

    @abc.abstractmethod
    def send_mess(self,  msg):
        """send json message"""
        pass
        
    @abc.abstractmethod
    def receive_mess(self):
        """receive json message"""
        pass
        
    @abc.abstractmethod
    def get_file(self, file_name):
        """download file from installation folder"""
        pass

class InputComm():
    """Input communication"""
    
    def __init__(self, input, output):
        self.input = input
        """Input Stream"""
        self.output = output
        """Output Stream"""

    def send_message(self, msg):
        """send message to output stream"""
        
    def receive_message(self):
        """Receive message from input stream"""


class SshOutputComm(OutputComm):
    """Ancestor of communication classes"""
    
    def __init__(self, host,  name,  password):
        super( SshOutputComm, self).__init__(host)
        self.name = name
        """login name for ssh connection"""
        self.password = password
        """password name for ssh connection"""
        
    def connect(self):
        """connect session"""
    
    def disconnect(self):
        """disconnect session"""

    def install(self,  installation,  path="./"):
        """copy installation"""
        
    def exec_(self,  command):
        """run command"""

    def send_json(self,  json):
        """send json message"""
        
    def receive_json(self):
        """receive json message"""
        
    def get_file(self, file_name):
        """download file from installation folder"""
