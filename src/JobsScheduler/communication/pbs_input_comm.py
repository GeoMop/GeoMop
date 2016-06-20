from communication.socket_input_comm import SocketInputComm
import sys
import os
import logging

logger = logging.getLogger("Remote")

__MAX_OPEN_PORTS__=200

class PbsInputComm(SocketInputComm):
    """Socket server connection"""
    
    def __init__(self, port):
        super(PbsInputComm, self).__init__(port)
        
    def connect(self):
        """connect session and send port number over stdout"""
        host = None
        host = os.environ.get('HOSTNAME')
        if host is None:
            host = ""
        self._write_output("HOST:--" + str(host) + "--") 
        logger.debug("Server host is:" + host) 
        super(PbsInputComm, self).connect()
        
    def _write_output(self, line):
        """write information about connection to relevant output"""
        sys.stdout.write(line + "\n")
        sys.stdout.flush()
        dir = os.environ.get('PBS_O_INITDIR')
        if dir is not None:
            # write to alternate file for torque too
            file = dir + '/pbs_output_alt'
            with open(file, 'a') as f:
                f.write(line + "\n")
            
        

