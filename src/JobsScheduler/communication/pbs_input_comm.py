from communication.socket_input_comm import SocketInputComm
import sys
import os
import logging

__MAX_OPEN_PORTS__=200

class PbsInputComm(SocketInputComm):
    """Socket server connection"""
    
    def __init__(self, port):
        super(PbsInputComm, self).__init__(port)
        
    def connect(self):
        """connect session and send port number over stdout"""
        
        host = os.environ.get('SGE_O_HOST')
        sys.stdout.write("HOST:--" + str(host) + "--\n")
        sys.stdout.flush()
        logging.debug("Server host is:" + host) 
        super(PbsInputComm, self).connect()       
