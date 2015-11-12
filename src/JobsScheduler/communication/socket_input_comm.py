import logging
import sys
import data.transport_data as tdata
import socket
import time

from communication.communication import InputComm

__MAX_OPEN_PORTS__=200

class SocketInputComm(InputComm):
    """Socket server connection"""
    
    def __init__(self, port):
        super( SocketInputComm, self).__init__()
        self.port = port
        """port for server communacion"""
        self.conn = None
        """Socket connection"""
        self.conn_interupted = False

    def connect(self):
        """connect session and send port number over stdout"""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ok = False
        i = 0
        while not ok:
            try:
                s.bind(("", self.port + i))
                ok = True
                sys.stdout.write("PORT:--" + str(self.port + i) + "--\n")
                sys.stdout.flush()
            except OSError as err:
                if err.errno == 98:
                    i += 1
                    if __MAX_OPEN_PORTS__< i:
                        raise Exception("Max open ports number is exceed")
                else:
                    raise err
        s.listen(1)
        self.port += i
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
        if len(data) == 0:
            time.sleep(10)
            if not self.conn_interupted:
                self.conn_interupted = True
                logging.warning("Connection was probably closed.")
            return None            
        txt =str(data, "us-ascii")
        try:
            mess = tdata.Message(txt)
        except(tdata.MessageError) as err:
            logging.warning("Error(" + str(err) + ") during parsing input message: " + txt)
            return None
        self.conn_interupted = False
        return mess
        
    def disconnect(self):
        """disconnect session"""
        self.conn.close()
        
    def save_state(self, state):
        """save state to variable"""
        state.input_port = self.port 
        
    def load_state(self, state):
        """load state from variable"""
        self.port = state.input_port

