"""Classes for handing messages over net"""

import abc
import logging
import sys
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
        self.output.write(msg.pack()+"\n")
        self.output.flush()
        
    def receive(self,  wait=60):
        """
        Receive message from input stream
        
        Function wait for answer for set time in seconds
        """
        try:
            fd = fdpexpect.fdspawn(self.input)
            txt = fd.read_nonblocking(size=10000, timeout=wait)
        except pexpect.TIMEOUT:
            return None
        try:
            mess = tdata.Message(txt)
        except(tdata.MessageError) as err:
            txt = str(txt, 'utf-8').strip()
            logging.warning("Error(" + str(err) + ") during parsing input message: " + txt)
        return mess

if sys.platform == "win32":
    import helpers.winssh as wssh
    class SshOutputComm(OutputComm):
        """Ancestor of communication classes"""
        
        def __init__(self, host,  name,  password=''):
            super( SshOutputComm, self).__init__(host)
            self.name = name
            """login name for ssh connection"""
            self.password = password
            """password name for ssh connection"""
            self.ssh = wssh.Wssh(self.host, self.name, self.password)
            """Ssh subprocessed instance"""
            
        def connect(self):
            """connect session"""
            self.ssh.connect()
            
        def disconnect(self):
            """disconnect session"""
            
        def install(self):
            """make installation"""
            self.installation.create_install_dir(self.ssh)
             
        def exec_(self, python_file):
            """run set python file in ssh"""
            
            mess = self.ssh.cd(self.installation.copy_path)
            if mess != "":
                logging.warning("Exec python file: " + mess) 
            mess = self.ssh.exec_(self.installation.get_command(python_file))
            if mess != "":
                logging.warning("Run python file: " + mess)  

        def send(self,  mess):
            """send json message"""
            m = mess.pack()
            self.ssh.write(m)
            self.last_mess = m

        def receive(self, timeout=60):
            """receive json message"""
            txt = self.ssh.read(timeout, self.last_mess)
            try:
                mess =tdata.Message(txt)
                return mess
            except(tdata.MessageError) as err:
                logging.warning("Receive message (" + txt + ") error: " + str(err))
            return None    
     
        def get_file(self, file_name):
            """download file from installation folder"""
else:
    import pxssh
    import fdpexpect
    import pexpect
    
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
            self.last_mess = None

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
            self.ssh.sendline("cd " + self.installation.copy_path)
            if self.ssh.prompt():
                mess = str(self.ssh.before, 'utf-8').strip()
                if mess != ("cd " + self.installation.copy_path):
                    logging.warning("Exec python file: " + mess) 
            self.ssh.sendline(self.installation.get_command(python_file))
            self.ssh.expect(dinstall.__python_exec__ + ".*\r\n")
            if len(self.ssh.before)>0:
                txt = str(self.ssh.before, 'utf-8').strip()
                logging.warning("Run python file: " + txt)  

        def send(self,  mess):
            """send json message"""
            m = mess.pack()
            self.ssh.sendline(m)
            self.last_mess = m

        def receive(self, timeout=60):
            """receive json message"""
            try:
                txt = str(self.ssh.read_nonblocking(size=10000, timeout=timeout), 'utf-8').strip()
            except pexpect.TIMEOUT:
                return None
            try:
                txt += str(self.ssh.read_nonblocking(size=10000, timeout=2), 'utf-8').strip()
            except pexpect.TIMEOUT:
                pass
            if self.last_mess is not None:
                # delete sended message
                if self.last_mess == txt [:len(self.last_mess)]:
                    txt = txt[len(self.last_mess):].strip()
                    if len(txt) == 0:                    
                        self.last_mess = None
                        return self.receive(timeout)
            self.last_mess = None
            try:
                mess =tdata.Message(txt)
                return mess
            except(tdata.MessageError) as err:
                logging.warning("Receive message (" + txt + ") error: " + str(err))
            return None
     
        def get_file(self, file_name):
            """download file from installation folder"""
            

