import logging
import sys
import data.transport_data as tdata
import re
from communication.communication import OutputComm

logger = logging.getLogger("Remote")

if sys.platform == "win32":
    import helpers.winssh as wssh
    class SshOutputComm(OutputComm):
        """Ancestor of communication classes"""
        
        def __init__(self, host, mj_name, name,  password=''):
            super( SshOutputComm, self).__init__(host, mj_name)
            self.name = name
            """login name for ssh connection"""
            self.password = password
            """password name for ssh connection"""
            self.ssh = wssh.Wssh(self.host, self.name, self.password)
            """Ssh subprocessed instance"""
            self._connected = False
            """SSH is connected"""
            self.installation.lock_installation()
            
        def connect(self):
            """connect session"""
            self.ssh.connect()
            self._connected = True
            self.installation.unlock_installation()
        
        def isconnected(self):
            """Connection is opened"""
            return self._connected
            
        def disconnect(self):
            """disconnect session"""
            self.conn.close()
            self.connected = False
            self.installation.unlock_application()
            
        def install(self):
            """make installation"""
            self.installation.prepare_ssh_env(self.ssh)
            try:
                self.installation.create_install_dir(self.ssh, self.ssh)
                self.installation.lock_installation_over_ssh(self.ssh, self.ssh, True)
                self.installation.copy_install_files(self.ssh, self.ssh)
            except Exception as err:
                logger.warning("Installation error: " + str(err))
            self.installation.lock_installation_over_ssh(self.ssh, self.ssh, False)    
             
        def exec_(self, python_file, mj_name, mj_id):
            """run set python file in ssh"""
            
            mess = self.ssh.cd(self.installation.copy_path)
            if mess != "":
                logger.warning("Exec python file: " + mess) 
            mess = self.ssh.exec_(self.installation.get_command(python_file, mj_name, mj_id))
            if mess != "":
                logger.warning("Run python file: " + mess)  

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
                logger.warning("Receive message (" + txt + ") error: " + str(err))
            return None    
     
        def download_result(self):
            """download result files from installation folder"""
            try:
                self.installation.get_results(self.ssh)
            except Exception as err:
                logger.warning("Download file error: " + str(err))
                return False
            return True
            
        def save_state(self, state):
            """save state to variable"""
            pass
        
        def load_state(self, state):
            """load state from variable"""
            pass
else:
    import pxssh
    import pexpect
    
    class SshOutputComm(OutputComm):
        """Ancestor of communication classes"""
        
        def __init__(self, host, mj_name,  name,  password=''):
            super( SshOutputComm, self).__init__(host, mj_name)
            self.name = name
            """login name for ssh connection"""
            self.password = password
            """password name for ssh connection"""
            self.ssh = None
            """Ssh subprocessed instance"""
            self._connected = False
            """SSH is connected"""
            
        def isconnected(self):
            """Connection is opened"""
            return self._connected
            
        def connect(self):
            """connect session"""
            self.ssh = pxssh.pxssh()
            self.ssh.login(self.host, self.name, self.password)
            self.last_mess = None
            self._connected = True

        def disconnect(self):
            """disconnect session"""
            try:
                try:
                    #prompt from exec
                    self.ssh.read_nonblocking(size=10000, timeout=10)
                except pexpect.TIMEOUT:
                    pass
                self.ssh.sendline("cd ..")
                if self.ssh.prompt():
                    mess = str(self.ssh.before, 'utf-8').strip()
                    if mess != ("cd .."):
                        logger.warning("Cd before logout fail: " + mess)
                try:
                    self.ssh.logout()
                except pexpect.TIMEOUT:
                    # sometimes first logout fails
                    self.ssh.sendline("pwd")
                    try:
                        self.ssh.logout()
                    except Exception as err:
                        logger.warning("Ssh logout error: " +   str(err))
            except Exception as err:
                logger.warning("Ssh error before logout: " +   str(err))
            self._connected = False
            
        def install(self):
            """make installation"""
            self.installation.prepare_ssh_env(self.ssh)           
           
            try:        
                sftp = self._get_sftp()
                self.installation.create_install_dir(sftp, self.ssh)
                sftp.close()
            except Exception as err:
                logger.warning("Installation error: " + str(err))
                
        def exec_(self, python_file, mj_name, mj_id):
            """run set python file in ssh"""
            self.ssh.sendline("cd " + self.installation.copy_path)
            if self.ssh.prompt():
                mess = str(self.ssh.before, 'utf-8').strip()
                if mess != ("cd " + self.installation.copy_path):
                    logger.warning("Exec python file: " + mess) 
                    
            logger.debug("Exec command over SSH: " + 
                self.installation.get_command(python_file, mj_name, mj_id))        
            self.ssh.sendline(self.installation.get_command(python_file, mj_name, mj_id))
            self.ssh.expect( self.installation.python_env.python_exec + ".*\r\n")
            
            lines = str(self.ssh.after, 'utf-8').splitlines(False)            
            del lines[0]
            error_lines = []
            for line in lines:
                line = self.strip_pexpect_echo( line.strip())
                if len(line)>0:
                    error_lines.append(line)
            if len(error_lines)>0:
                logger.warning("Run python file: " + "\n".join( error_lines)) 

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
            
            # parse message, delete echo
            error_lines = []
            ready = False
            for i in range(0, len(lines)):
                line = self.strip_pexpect_echo( lines[i].strip())
                if not ready and tdata.Message.check_mess(line): 
                    #base64 text
                    if self.last_mess is not None and line == self.last_mess:
                        #echo
                        last_mess_processed = True
                        self.last_mess = None
                    else:
                        # message
                        txt = line
                        ready = True
                else:
                    if len(line)>0:
                        error_lines.append(line)
   
            if len( error_lines) > 0:
                logger.warning("Ballast in message:" + "\n".join( error_lines))
            
            #only echo, tray again
            if last_mess_processed and txt is None:
                return self.receive(timeout)
             
            if txt is None:
                return None
                
            self.last_mess = None
            try:
                mess =tdata.Message(txt)
                return mess
            except(tdata.MessageError) as err:
                logger.warning("Receive message (" + txt + ") error: " + str(err))
            return None
     
        def download_result(self):
            """download result files from installation folder"""
            try:
                sftp = self._get_sftp()
                self.installation.get_results(sftp)
                sftp.close()
            except Exception as err:
                logger.warning("Download file error: " + str(err))
                return False
            return True
            
        def _get_sftp(self):
            """return sftp connection"""
            sftp = pexpect.spawn('sftp ' + self.name + "@" + self.host)
            res = sftp.expect(['.*assword:', 'sftp> '])
            if res == 0:
                # password requaried
                sftp.sendline(self.password)
                sftp.expect('.*')
                res = sftp.expect(['Permission denied','Connected to .*'])
                if res == 0:
                    sftp.kill(0)
                    raise Exception("Permission denied for user " + self.name)
            return sftp
        
        @staticmethod
        def strip_pexpect_echo(txt):
            """strip pexpect echo"""
            pex_echo = re.match( '(\[PEXPECT\]\$\s*)', txt)
            if pex_echo is not None:
                if  len(pex_echo.group(1)) == len(txt):
                        return ""
                txt = txt[len(pex_echo.group(1)):]
            return txt
            
        def save_state(self, state):
            """save state to variable"""
            pass
        
        def load_state(self, state):
            """load state from variable"""
            pass
