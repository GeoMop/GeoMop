import logging
import sys
import data.transport_data as tdata
import socket
import time
import threading
import struct

from communication.communication import InputComm

logger = logging.getLogger("Remote")
__MAX_OPEN_PORTS__=200

class SocketInputComm(InputComm):
    """Socket server connection"""
    
    def __init__(self, port):
        super( SocketInputComm, self).__init__()
        self.port = port
        """port for server communacion"""
        self.conn = None
        """Socket connection"""
        self._conn_interupted = False
        """Connection was unintendently interupted"""
        self._conn_interupted_count = 0
        """time of connection interuption"""
        self._connected = False
        """Socket Connection is connected"""
        self._connected_lock = threading.Lock()
        """Lock for connected"""
        self._established = False
        """Port and host for Socket Connection was recognised"""

    def isconnected(self):
        """Connection is opened"""
        self._connected_lock.acquire()
        con = self._connected
        self._connected_lock.release()       
        return con

    def connect(self):
        """connect session in separate thread"""
        t = threading.Thread(target=self._connect)
        t.daemon = True
        t.start()

    def _connect(self):
        """connect session and send port number over stdout"""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', 1, 0))
        ok = False
        i = 0
        while not ok:
            try:
                s.bind(("", self.port + i))
                ok = True
                if not self._established:
                    self._write_output("PORT:--" + str(self.port + i) + "--")
                    self._established = True
            except OSError as err:
                if (err.errno == 98 or err.errno == 1048) and not self._established:
                    i += 1
                    if __MAX_OPEN_PORTS__< i:
                        raise Exception("Max open ports number is exceed")
                else:
                    logger.error("Cant listen on port " + str(self.port) + ": " + str(err))
                    return
        self.port += i
        logger.debug("Server try listen on port " + str(self.port)) 
        s.listen(1)
        self.conn, addr = s.accept()
        self._connected_lock.acquire()
        self._connected = True 
        self._connected_lock.release()        
        logger.debug("Server is listened on port " + str(self.port) +" by " + str(addr)) 
        
    def _write_output(self, line):
        """write information about connection to relevant output"""
        sys.stdout.write(line + "\n")
        sys.stdout.flush()
  
    def send(self, msg):
        """send message to output stream"""
        if not self.isconnected():
            logger.debug("Can't send message, connection is not established.") 
            return
        b = bytes(msg.pack(), "us-ascii")
        self.conn.sendall(b)
        
    def receive(self,  wait=60):
        """
        Receive message from socket
        
        Function wait for answer for set time in seconds
        """
        if not self.isconnected():
            time.sleep(1)
            return 
        self.conn.settimeout(wait)
        try:
            data = self.conn.recv(1024*1024)
        except socket.timeout:
            return None
        if len(data) == 0:
            if self._conn_interupted_count > 600:
                self.disconnect
                self.connect()
                return 
            time.sleep(1)
            if not self._conn_interupted:
                self._conn_interupted = True
                logger.warning("Connection was probably closed.")
            else:
                self._conn_interupted_count +=1
            return None
        txt =str(data, "us-ascii")
        try:
            mess = tdata.Message(txt)
        except(tdata.MessageError) as err:
            logger.warning("Error(" + str(err) + ") during parsing input message: " + txt)
            return None
        self._conn_interupted = False
        self._conn_interupted_count = 0
        return mess
        
    def disconnect(self):
        """disconnect session"""
        self._connected_lock.acquire()
        self._connected = False
        self._connected_lock.release()
        self.conn.shutdown(socket.SHUT_RDWR)        
        self.conn.close() 
        logger.debug("Server close connection on port " + str(self.port))        
        
    def save_state(self, state):
        """save state to variable"""
        state.input_port = self.port 
        
    def load_state(self, state):
        """load state from variable"""
        self.port = state.input_port

