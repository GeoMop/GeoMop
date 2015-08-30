"""Classes for handing messages over net"""

import abc
import logging
import sys
import data.transport_data as tdata
import data.installation as dinstall
import socket
import subprocess

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

class StdInputComm(InputComm):
    """Input communication over stdout and in"""
    
    def __init__(self, input, output):
        super( StdInputComm, self).__init__()
        self.input = input
        """Input Stream"""
        self.output = output
        """Output Stream"""

    def connect(self):
        """connect session"""
        pass

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
    
    def disconnect(self):
        """disconnect session"""
        pass
        
class SocketInputComm(InputComm):
    """Socket server connection"""
    
    def __init__(self, port):
        super( SocketInputComm, self).__init__()
        self.port = port
        """port for server communacion"""
        self.conn = None
        """Socket connection"""

    def connect(self):
        """connect session"""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("", self.port))
        s.listen(1)
        self.conn, addr = s.accept()
        logging.debug("Server is listened on port" + str(self.port) +" by " + str(addr)) 
  
    def send(self, msg):
        """send message to output stream"""
        b = bytes(msg.pack(), "us-ascii")
        self.conn.sendall(b)
        
    def receive(self,  wait=60):
        """
        Receive message from socket
        
        Function wait for answer for set time in seconds
        """
        self.conn.settimeout(wait)
        try:
            data = self.conn.recv(1024*1024)
        except socket.timeout:
            return None
        txt =str(data, "us-ascii")
        try:
            mess = tdata.Message(txt)
        except(tdata.MessageError) as err:
            logging.warning("Error(" + str(err) + ") during parsing input message: " + txt)
            return None
        return mess
        
    def disconnect(self):
        """disconnect session"""
        self.conn.close()

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
            self.conn.close()
            
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
                txt = str(self.ssh.read_nonblocking(size=10000, timeout=timeout), 'utf-8')
            except pexpect.TIMEOUT:
                return None
                
            timeout = False
            while not timeout:    
                try:
                    txt += str(self.ssh.read_nonblocking(size=10000, timeout=2), 'utf-8')
                except pexpect.TIMEOUT:
                    timeout = True
            txt = txt.strip()
            lines = txt.splitlines(False)
            txt = None
            last_mess_processed = False
            for i in range(0, len(lines)):
                if lines[i][-1:] == "=": 
                    if self.last_mess is not None and lines[i].strip() == self.last_mess:
                        last_mess_processed = True
                        self.last_mess = None
                        del lines[i]
                    else:
                        txt = lines[i]
                        del lines[i]
                        break                    
            if len(lines) > 0:
                logging.warning("Error in message:" + "\n".join(lines))
            if last_mess_processed and txt is None:
                return self.receive(timeout)
            if txt is None:
                return None
            self.last_mess = None
            try:
                mess =tdata.Message(txt)
                return mess
            except(tdata.MessageError) as err:
                logging.warning("Receive message (" + txt + ") error: " + str(err))
            return None
     
        def get_file(self, file_name):
            """download file from installation folder"""
            
class ExecOutputComm(OutputComm):
    """Ancestor of communication classes"""
    
    def __init__(self, port):
        super(ExecOutputComm, self).__init__("localhost")
        self.port = port
        """port for server communacion"""
        self.conn = None
        """Socket connection"""

    def connect(self):
        """connect session"""
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((self.host, self.port))
        logging.debug("Client is connected to " + self.host + ":" + str(self.port)) 
         
    def disconnect(self):
        """disconnect session"""
        self.conn.close()
        
    def install(self):
        """make installation"""
        self.installation.local_copy_path()
        
    def exec_(self, python_file):
        """run set python file in ssh"""
        subprocess.Popen(self.installation.get_args(python_file))

    def send(self,  mess):
        """send json message"""        
        b = bytes(mess.pack(), "us-ascii")
        self.conn.sendall(b)

    def receive(self, timeout=60):
        """receive json message"""
        self.conn.settimeout(timeout)
        try:
            data = self.conn.recv(1024*1024)
        except socket.timeout:
            return None

        txt =str(data, "us-ascii")
        try:
            mess = tdata.Message(txt)
        except(tdata.MessageError) as err:
            logging.warning("Error(" + str(err) + ") during parsing output answer: " + txt)
            return None
        return mess
 
    def get_file(self, file_name):
        """download file from installation folder"""
