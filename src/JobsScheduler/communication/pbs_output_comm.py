import logging
import data.transport_data as tdata
import socket
import subprocess
import re
from communication.exec_output_comm import ExecOutputComm

class PbsOutputComm( ExecOutputComm):
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
        process = subprocess.Popen(self.installation.get_args(python_file), 
            stdout=subprocess.PIPE)
        # wait for port number
        out = process.stdout.readline()
        port = re.match( 'PORT:--(\d+)--', str(out, 'utf-8'))
        if port is not None:
            logging.debug("Next communicator return socket port:" + port.group(1)) 
            self.port = int(port.group(1))
 
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
