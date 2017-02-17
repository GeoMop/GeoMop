import logging
import pexpect
import time
logger = logging.getLogger("Remote")
from communication.exec_output_comm import ExecOutputComm
from communication.ssh_output_comm import SshOutputComm

class SshOutputTunnelComm(SshOutputComm):
    """Ancestor of communication classes"""

    def __init__(self, host, tunnel_port, mj_name, an_name,  name,  password=''):
        super( SshOutputTunnelComm, self).__init__(host, mj_name, an_name, name,  password)
        self.socket = None
        """socket connection over ssh tunnel"""
        self.tunnel = None
        """ssh tunnel"""
        self.mj_name = mj_name
        self.an_name = an_name
        
    def _get_tunnel(self, tunnel_command):
        """return sftp connection"""
        tunnel = pexpect.spawn(tunnel_command, timeout=60)
        try:
            res = tunnel.expect(['.*assword:', pexpect.EOF])
        except pexpect.TIMEOUT:
            tunnel.kill(0)
            return None
        if res == 0:
            # password requaried
            tunnel.sendline(self.password)
            tunnel.expect(pexpect.EOF)
            mess = str(tunnel.before, 'utf-8').strip()
            if mess is not None and mess != (""):
                logger.error("Can't create ssh tunnel " +  mess)
                return None
            return tunnel
        
    def _close_tunnel(self):
        """return sftp connection"""
        path = self.an_name + '-' + self.mj_name
        tunnel_command = 'ssh -S {0} -O exit {1}@localhost'.format(path, self.host)            
        tunnel = pexpect.spawn(tunnel_command, timeout=60)
        try:
            res = tunnel.expect(['.*assword:', pexpect.EOF])
        except pexpect.TIMEOUT:
            tunnel.kill(0)
            return None
        if res == 0:
            # password requaried
            tunnel.sendline(self.password)
            tunnel.expect(pexpect.EOF)
            mess = str(tunnel.before, 'utf-8').strip()
            if mess is not None and mess != (""):
                logger.error("Can't close ssh tunnel " +  mess)
                return None
            
    def create_tunnel(self, port, host):
        """create socket connection over ssh tunnel"""
        local_port=5000
        path = self.an_name + '-' + self.mj_name
        tunnel_command = 'ssh -C -N -f -S {0} -L {1}:{2}:{3} {4}@localhost'.format(
            path, local_port, host, port, self.name, self.host)
        logger.debug("Tunnel command: " + tunnel_command)
        if self._get_tunnel(tunnel_command) is None:
            return  
        super( SshOutputTunnelComm, self).disconnect()
        self.socket =  ExecOutputComm(self.mj_name, self.an_name, local_port)
        # try connect 60s
        i=0
        while True:
            try:
                self.socket.connect()                    
                break
            except ConnectionRefusedError as err:
                    i += 1
                    time.sleep(1)
                    if i >= 60:
                        logger.error("Connect tunnel timeout error (" + str(err) + ')')
                    else:
                        continue
            except err:
                logger.error("Connect tunnel error (" + str(err) + ')')
            self.socket = None    
            break    
    
    def disconnect(self):
        if self.socket is None:
            super( SshOutputTunnelComm, self).disconnect()
        else:
            self._close_tunnel()
            
    def send(self,  mess):
        """send json message"""
        if self.socket is None:
            super( SshOutputTunnelComm, self).send(mess)
        else:
            self.socket.send(mess)

    def receive(self, timeout=60):
        """receive json message"""
        if self.socket is None:
            return super( SshOutputTunnelComm, self).receive(timeout)
        else:
            return self.socket.receive(timeout)
        
    def save_state(self, state):
        """save state to variable"""
        if self.socket is not None:
            self.socket.save_state(state)
    
    def load_state(self, state):
        """load state from variable"""
        if self.socket is not None:
            self.socket.load_state(state)
