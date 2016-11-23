"""
ssh connection for testing

if error was occured throw exception
"""

import pxssh
import pexpect

class Conn():
    def __init__(self,ssh):
        self.ssh = ssh
        self.conn = None
        self.sftp = None
        
    def pwd(self):
        """return current folder"""
        command = "pwd"
        self.conn.sendline(command)
        ok = self.conn.expect([".*" + command + "\r\n", pexpect.TIMEOUT])        
        if ok != 0:
            err = str(self.conn.before, 'utf-8').strip() 
            raise  SshError("Error message during pwd: " + str(err))
        ret = str(self.conn.readline(), 'utf-8').strip()
        return ret
        
    def get_python_version(self,  interpreter): 
        """return python version"""
        command = "{0} --version".format(interpreter)
        self.conn.sendline(command)
        ok = self.conn.expect([".*" + command + "\r\n", pexpect.TIMEOUT])        
        if ok != 0:
            err = str(self.conn.before, 'utf-8').strip() 
            raise  SshError("Error message during calling python ({0}): {1}".format(
                interpreter, str(err)))
        ret = str(self.conn.readline(), 'utf-8').strip()
        return ret
        
    def test_python_script(self,  interpreter, script_file, file_name, file_text): 
        """
        Test script file.
        
        Test supposed that script expected three parameters. First is
        printed during script running. Second is file name, that is 
        created and third is text wrote to this file.
        If other text than is past as parameter is printed, text is evaluate
        as error message.
        """
        printed = """Script test"""
        command = '{0} {1} "{2}" "{3}" "{4}"'.format(
            interpreter, script_file, printed, file_name, file_text)
        self.conn.sendline(command)
        res = self.conn.expect( ["--" + printed + "--", pexpect.TIMEOUT], timeout=5)
        if res>0:
            raise  SshError("Run test python script error:" + str(self.conn.before,'utf-8').strip())
    
    def remove_dir(self,dir):
        """renove folder"""
        command = "rm -rf "+dir
        self.conn.sendline(command)
        ok = self.conn.expect([".*" + command + "\r\n", pexpect.TIMEOUT])        
        if ok != 0:
            err = str(self.conn.before, 'utf-8').strip() 
            raise  SshError("Error message during directory removing: " + str(err))
           
    def ls_dir(self,dir):       
        """return folders and files text names in array""" 
        command = "ls -m --color='never' "+dir
        self.conn.sendline(command)
        ok = self.conn.expect([".*" + command + "\r\n", pexpect.TIMEOUT])        
        if ok != 0:
           assert False, str(self.conn.before, 'utf-8').strip() 
        ret = str(self.conn.readline(), 'utf-8').strip()
        arr = ret.split(", ")
        return arr
        
    def create_dir(self,dir):
        """create folder"""
        command = "mkdir "+dir
        self.conn.sendline(command)
        ok = self.conn.expect([".*" + command + "\r\n", pexpect.TIMEOUT])        
        if ok != 0:
            err = str(self.conn.before, 'utf-8').strip() 
            raise  SshError("Error message during directory creation: " + str(err))
            
    def cd(self,dir):
        """change current folder"""
        command = "cd "+dir
        self.conn.sendline(command)
        ok = self.conn.expect([".*" + command + "\r\n", pexpect.TIMEOUT])        
        if ok != 0:
            err = str(self.conn.before, 'utf-8').strip() 
            raise  SshError("Error message during cd command: " + err)
           
    def connect(self):
        """Connect to ssh"""
        self.conn = pxssh.pxssh()
        try:
            self.conn.login(self.ssh.host, self.ssh.uid,self.ssh.pwd, check_local_ip=False)            
            self.conn.setwinsize(128,512)                    
        except Exception as err:
            self.conn = None
            try:
                self.conn = pxssh.pxssh()
                self.conn.login(self.ssh.host, self.ssh.uid,self.ssh.pwd, check_local_ip=False, quiet=False)            
            except Exception as err:  
                before_err = str(self.conn.before, 'utf-8').strip() 
                self.conn = None 
                if len(before_err)>3:
                    raise  SshError("SSH connection error:\nMessage: " + before_err + "\nError: " + str(err))
                else:
                    raise  SshError("SSH connection error: " + str(err))                               
            self.disconnect()
            self.conn = None
            raise  SshError("SSH connection non-quiet error: " + str(err))
            
    def connect_sftp(self, local, remote):        
        """return sftp connection"""
        self.sftp = pexpect.spawn('sftp ' + self.ssh.uid + "@" + self.ssh.host, timeout=15)
        try:
            res = self.sftp.expect(['.*assword:', 'sftp> '])
        except pexpect.TIMEOUT:
            self.sftp.kill(0)
            self.sftp = pexpect.spawn('sftp ' + self.name + "@" + self.host, timeout=30)
            res = self.sftp.expect(['.*assword:', 'sftp> '])
        if res == 0:
            # password requaried
            self.sftp.sendline(self.ssh.pwd)
            self.sftp.expect('.*')
            res = self.sftp.expect(['Permission denied','Connected to .*'])
            if res == 0:
                self.sftp.kill(0)
                self.sftp = None
                raise SshError("SFTP Error: Permission denied for user " + self.ssh.uid)
        self.sftp.sendline('lcd ' + local)
        self.sftp.expect('.*lcd ' + local + "\r\n")
        self.sftp.sendline('cd ' + remote)
        self.sftp.expect('.*cd ' + remote + "\r\n")
        self.sftp.expect("sftp> ")
        if len(self.sftp.before)>0:
            raise SshError("Cd SFTP Error: " + str(self.sftp.before, 'utf-8').strip())
                
    def upload_file(self, file):
        """upload file over sftp connection"""
        self.sftp.sendline('put ' + file)
        self.sftp.expect('.*put ' + file + "\r\n")
        self.sftp.expect("sftp> ")

    def upload_dir(self, dir):
        """upload dir over sftp connection"""
        self.sftp.sendline('put -r ' + dir)
        self.sftp.expect('.*put -r ' + dir + "\r\n")
        end=0
        while end==0:
            #wait 3s after last message
            end = self.sftp.expect(["\r\n", pexpect.TIMEOUT], timeout=3)
            
    def download_file(self, file, result_dir):
        """download file over sftp connection"""
        self.sftp.sendline('lcd ' + result_dir)
        self.sftp.expect('.*lcd ' + result_dir + "\r\n")
        self.sftp.sendline('get ' + file)
        self.sftp.expect("sftp> ")

    def download_dir(self, dir, result_dir):
        """download directory over sftp connection"""
        self.sftp.sendline('cd ' + dir)
        self.sftp.expect('.*cd ' + dir + "\r\n")
        self.sftp.expect("sftp> ")
        self.sftp.sendline('lcd ' + result_dir)
        self.sftp.expect('.*lcd ' + result_dir + "\r\n")
        self.sftp.sendline('get -r *')
        self.sftp.expect(r'.*get -r \*\r\n')
        end = 0
        while end==0:
            #wait 2s after last message
            end =  self.sftp.expect(["\r\n", pexpect.TIMEOUT], timeout=2)

    def disconnect_sftp(self):
        """Disonnect sftp"""
        try:
            self.sftp.close()
        except Exception as err:
            self.sftp = None
            raise  SshError("Disconnect SFTP error:" + str(err))
        self.sftp = None
            
    def disconnect(self):
        """disconnect ssh"""
        try:
            self.conn.logout()
        except Exception as err:
            self.conn = None
            raise  SshError("Disconnect error:" + str(err))
        self.conn = None
        
class SshError(Exception):
    """Exception raised for errors in ssh class."""

    def __init__(self, message):
        self.message = message
