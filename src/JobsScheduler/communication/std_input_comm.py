import logging
import data.transport_data as tdata
from communication.communication import InputComm
import sys

logger = logging.getLogger("Remote")

class StdInputComm(InputComm):
    """Input communication over stdout and in"""
    
    def __init__(self, input, output):
        super( StdInputComm, self).__init__()
        self.input = input
        """Input Stream"""
        self.output = output
        """Output Stream"""
        self._connected = False
        """Std is connected"""

    def connect(self):
        """connect session"""
        self._connected = True
    
    def isconnected(self):
        """Connection is opened"""
        return self._connected

    def send(self, msg):
        """send message to output stream"""
        self.output.write(msg.pack()+"\n")
        self.output.flush()
    
    def receive(self,  wait=60):
        """
        Receive message from input stream
        
        Function wait for answer for set time in seconds
        """
        mess = None
        if sys.platform == "win32":
            import fdpexpect
            import pexpect
            try:
                fd = fdpexpect.fdspawn(self.input)
                txt = fd.read_nonblocking(size=10000, timeout=wait)
            except pexpect.TIMEOUT:
                return None
            try:
                mess = tdata.Message(str(txt, 'utf-8').strip())
            except(tdata.MessageError) as err:
                txt = str(txt, 'utf-8').strip()
                logger.warning("Error(" + str(err) + ") during parsing input message: " + txt)
        else:
            logger.error("Reseve message over ssh is not implemented for windows platform")
        return mess
    
    def disconnect(self):
        """disconnect session"""
        self._connected = False
        
    def save_state(self, state):
        """save state to variable"""
        pass
        
    def load_state(self, state):
        """load state from variable"""
        pass
