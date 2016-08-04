import logging
import data.transport_data as tdata
import socket
import subprocess
import re
import sys
import time
from communication.communication import OutputComm

logger = logging.getLogger("Remote")

class ExecOutputComm(OutputComm):
    """Ancestor of communication classes"""
    
    def __init__(self, mj_name, an_name, port):
        super(ExecOutputComm, self).__init__("localhost", mj_name, an_name)
        self.port = port
        """port for server communacion"""
        self.conn = None
        """Socket connection"""
        self.initialized = False
        """Is ready to connect"""
        self._connected = False
        """socket is connected"""
        self._proc = None
        """process for cheching and killing"""

    def is_running_next(self):
        """
        Return if next communicator run
        
        this method is not work for restore communicator
        """
        if self._proc is None:
            return False
        return_code = self._proc.poll()
        return return_code is None        
        
    def kill_next(self):
        """
        kill next communicator
        
        this method is not work for restored communicator 
        """
        if self.is_running_next():
            self._proc.kill()

    def connect(self):
        """connect session"""        
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logger.debug("Client try connect to " + self.host + ":" + str(self.port)) 
        self.conn.connect((self.host, self.port))
        logger.debug("Client is connected to " + self.host + ":" + str(self.port)) 
        self._connected = True       
         
    def disconnect(self):
        """disconnect session"""
        if self.conn is not None:
            self.conn.close()
        self._connected = False        
        
    def isconnected(self):
        """Connection is opened"""
        return self._connected
        
    def install(self):
        """make installation"""
        #ToDo: scl, module add support
        self.installation.local_copy_path()
        
    def exec_(self, python_file, mj_id):
        """run set python file in ssh"""
        self.installation.local_copy_path()
        self.installation.prepare_popen_env()
        si = None
        if sys.platform == "win32":
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        args = self.installation.get_args(python_file, mj_id)
        if args[0] is None or args[0]=="":
            raise Exception("Python interpreter can't be empty")
        logger.debug("Run "+" ".join(args))
        self._proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, startupinfo=si)
        logger.debug("PID: " + str(self._proc.pid)) 
        # wait for port number
        time.sleep(0.5)
        return_code = self._proc.poll()
        if return_code is not None:
            out = self._proc.stdout.read()
            if out is None or len(out)==0:
                out = "no output"
            else:
                out = str(out, 'utf-8')
            if return_code == 0:
                logger.warning("Too short run time of next communicator. Output:" + out) 
            else:   
                self._proc = None
                raise Exception("Can not start next communicator " + python_file + 
                    " (return code: " + str(return_code) + "): " + out)        
        out = self._proc.stdout.readline()
        port = re.match( 'PORT:--(\d+)--', str(out, 'utf-8'))
        if port is not None:
            logger.debug("Next communicator return socket port:" + port.group(1)) 
            self.port = int(port.group(1))
        self.initialized=True
 
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
            logger.warning("Error(" + str(err) + ") during parsing output answer: " + txt)
            return None
        return mess
 
    def download_result(self):
        """download result files from installation folder"""
        return True
        
    def save_state(self, state):
        """save state to variable"""
        state.inicialized = self.initialized
        state.output_port = self.port
        state.output_host = self.host  
        
    def load_state(self, state):
        """load state from variable"""
        self.initialized = False
        if hasattr(state, 'output_port'):
            self.inicialized = state.inicialized
            self.port = state.output_port
            self.host = state.output_host 
