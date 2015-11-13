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
        
        host = os.environ.get('HOSTNAME')
        sys.stdout.write("HOST:--" + str(host) + "--\n")
        sys.stdout.flush()
        logger.debug("Server host is:" + host) 
        super(PbsInputComm, self).connect()       
