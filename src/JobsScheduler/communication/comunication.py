"""Classes for handing messages over net"""

import abc
import pxssh
import data.transport_data as tdata 

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
        pass
        
    @abc.abstractmethod
    def exec_(self,  command):
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

    def send(self, msg):
        """send message to output stream"""
        
    def receive(self,  wait=60):
        """
        Receive message from input stream
        
        Function wait for answer for set time in seconds
        """


class SshOutputComm(OutputComm):
    """Ancestor of communication classes"""
    
    def __init__(self, host,  name,  password=''):
        super( SshOutputComm, self).__init__(host)
        self.name = name
        """login name for ssh connection"""
        self.password = password
        """password name for ssh connection"""
        self.ssh = None
        """Ssh subprocessed instance"""
        
    def connect(self):
        """connect session"""
        self.ssh = pxssh.pxssh()
        self.ssh.login(self.host, self.name, self.password)

    def disconnect(self):
        """disconnect session"""
        self.ssh.logout()
        
    def install(self,  installation,  path="./"):
        """copy installation"""
        
    def exec_(self,  command):
        """run command"""
        self.ssh.sendline(command)

    def send(self,  json):
        """send json message"""
        self.ssh.sendline(json)
        
    def receive(self, timeout=60):
        """receive json message"""
        if self.ssh.prompt(timeout):
            mess = tdata.Message(self.ssh.before)
            return mess
        return None

    def get_file(self, file_name):
        """download file from installation folder"""
