"""Classes for handing messages over net"""

import abc
import logging
import pxssh
import fdpexpect
import pexpect
import data.transport_data as tdata
import data.installation as dinstall

class OutputComm(metaclass=abc.ABCMeta):
    """Ancestor of output communication classes"""
    
    def __init__(self, host):
        self.host=host
        """ip or dns of host for communication"""
        self.installation = dinstall.Installation()
        """installation where is copied files"""
    
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
        self.output.write(msg.pack() + "\n")
        
    def receive(self,  wait=60):
        """
        Receive message from input stream
        
        Function wait for answer for set time in seconds
        """
        fd = fdpexpect.fdspawn(self.input)
        try:
            txt = fd.read_nonblocking(size=1000, timeout=wait)
        except pexpect.TIMEOUT:
            return None
        mess = tdata.Message(txt) 
        return mess

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
        
    def install(self):
        """make installation"""
        sftp = pexpect.spawn('sftp ' + self.name + "@" + self.host)
        sftp.expect('.*assword:')
        sftp.sendline(self.password)
        sftp.expect('.*')
        res = sftp.expect(['Permission denied','Connected to .*'])
        if res == 0:
            sftp.kill(0)
            raise Exception("Permission denied for user " + self.name) 
        self.installation.create_install_dir(sftp)
        sftp.close()
        
    def exec_(self, python_file):
        """run set python file in ssh"""
        self.ssh.sendline(self.installation.get_command(python_file))
        if self.ssh.prompt():
            mess = str(self.ssh.before, 'utf-8').strip()
            logging.warning("Exec python file: " + mess) 

    def send(self,  mess):
        """send json message"""
        self.ssh.sendline(mess.pack())
        
    def receive(self, timeout=60):
        """receive json message"""
        if self.ssh.prompt(timeout):
            mess =tdata.Message(self.ssh.before)
            return mess
        return None

    def get_file(self, file_name):
        """download file from installation folder"""
