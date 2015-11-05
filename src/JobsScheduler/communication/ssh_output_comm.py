import logging
import sys
import data.transport_data as tdata
import re
from communication.communication import OutputComm

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
            
        def connect(self):
            """connect session"""
            self.ssh.connect()
            
        def disconnect(self):
            """disconnect session"""
            self.conn.close()
            
        def install(self):
            """make installation"""
            self.installation.prepare_python_env(self.ssh)
            try:
                self.installation.create_install_dir(self.ssh)
            except Exception as err:
                logging.warning("Installation error: " + str(err))
             
        def exec_(self, python_file, mj_name, mj_id):
            """run set python file in ssh"""
            
            mess = self.ssh.cd(self.installation.copy_path)
            if mess != "":
                logging.warning("Exec python file: " + mess) 
            mess = self.ssh.exec_(self.installation.get_command(python_file, mj_name, mj_id))
            if mess != "":
                logging.warning("Run python file: " + mess)  

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
                logging.warning("Receive message (" + txt + ") error: " + str(err))
            return None    
     
        def download_result(self):
            """download result files from installation folder"""
            try:
                self.installation.get_results(self.ssh)
            except Exception as err:
                logging.warning("Download file error: " + str(err))
                return False
            return True
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
            
        def connect(self):
            """connect session"""
            self.ssh = pxssh.pxssh()
            self.ssh.login(self.host, self.name, self.password)
            self.last_mess = None

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
                        logging.warning("Cd before logout fail: " + mess)
                try:
                    self.ssh.logout()
                except pexpect.TIMEOUT:
                    # sometimes first logout fails
                    self.ssh.sendline("pwd")
                    try:
                        self.ssh.logout()
                    except Exception as err:
                        logging.warning("Ssh logout error: " +   str(err))
            except Exception as err:
                logging.warning("Ssh error before logout: " +   str(err))
            
        def install(self):
            """make installation"""
            self.installation.prepare_python_env(self.ssh)                               
            try:        
                sftp = self._get_sftp()
                self.installation.create_install_dir(sftp)
                sftp.close()
            except Exception as err:
                logging.warning("Installation error: " + str(err))
                
        def exec_(self, python_file, mj_name, mj_id):
            """run set python file in ssh"""
            self.ssh.sendline("cd " + self.installation.copy_path)
            if self.ssh.prompt():
                mess = str(self.ssh.before, 'utf-8').strip()
                if mess != ("cd " + self.installation.copy_path):
                    logging.warning("Exec python file: " + mess) 
            self.ssh.sendline(self.installation.get_command(python_file, mj_name, mj_id))
            self.ssh.expect( self.installation.python_exec + ".*\r\n")
            
            lines = str(self.ssh.after, 'utf-8').splitlines(False)            
            del lines[0]
            error_lines = []
            for line in lines:
                line = self.strip_pexpect_echo( line.strip())
                if len(line)>0:
                    error_lines.append(line)
            if len(error_lines)>0:
                logging.warning("Run python file: " + "\n".join( error_lines)) 

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
                if not ready and lines[i][-1:] == "=": 
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
                logging.warning("Ballast in message:" + "\n".join( error_lines))
            
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
                logging.warning("Receive message (" + txt + ") error: " + str(err))
            return None
     
        def download_result(self):
            """download result files from installation folder"""
            try:
                sftp = self._get_sftp()
                self.installation.get_results(sftp)
                sftp.close()
            except Exception as err:
                logging.warning("Download file error: " + str(err))
                return False
            return True
            
        def _get_sftp(self):
            """return sftp connection"""
            sftp = pexpect.spawn('sftp ' + self.name + "@" + self.host)
            sftp.expect('.*assword:')
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
