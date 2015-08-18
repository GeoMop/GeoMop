"""class represent instalation"""
import sys
import os
import re
import logging
import copy

__install_dir__ = os.path.split(
    os.path.dirname(os.path.realpath(__file__)))[0]
__ins_files__ = {}
__ins_files__['delegator'] = "delegator.py"
__ins_dirs__ = []
__ins_dirs__.append("communication")
__ins_dirs__.append("data") 
__ins_dirs__.append("twoparty") 
__root_dir__ = "jobs"
__python_exec__ = "python3"

class Installation:
    """Files with installation (python files and configuration files) is selected 
        and send to set folder"""
    def __init__(self):
        self.copy_path = None
        """installation file path"""
        self.ins_files = copy.deepcopy(__ins_files__)
        """files to install"""
        self.ins_dirs = copy.deepcopy(__ins_dirs__)
        """directories to install"""

    def create_install_dir(self, conn):
        """Copy installation files"""
        if sys.platform == "win32":
            self.copy_path = "/home/test/jobs"
        else:
            import pexpect
            
            conn.sendline('pwd')
            conn.expect(".*pwd\r\n")
            ret = str(conn.readline(), 'utf-8').strip()
            searchObj = re.search( '^(.*):\s(/.*)$',ret)
            # use / instead join because destination os is linux and is not 
            # same with current os
            self.copy_path = searchObj.group(2) + '/' + __root_dir__
            
            conn.sendline('mkdir ' + __root_dir__)
            conn.expect(".*mkdir " + __root_dir__ + "\r\n")
            conn.expect("sftp> ")
            if len(conn.before)>0:
                logging.warning("Sftp message (mkdir root): " + str(conn.before, 'utf-8').strip())      
            conn.sendline('cd ' + __root_dir__)
            conn.expect('.*cd ' + __root_dir__ + "\r\n")
            conn.expect("sftp> ")
            if len(conn.before)>0:
                logging.warning("Sftp message (cd root): " + str(conn.before, 'utf-8').strip()) 
            conn.sendline('mkdir res')
            conn.expect(".*mkdir res\r\n")
            conn.expect("sftp> ")
            if len(conn.before)>0:
                logging.warning("Sftp message(mkdir res): " + str(conn.before, 'utf-8').strip()) 
            conn.sendline('lcd ' + __install_dir__)
            conn.expect('.*lcd ' + __install_dir__ + "\r\n")
            for name in self.ins_files:
                conn.sendline('put ' +  __ins_files__[name])
                conn.expect('sftp> put ' + __ins_files__[name] + "\r\n")
                conn.expect("sftp> ")
                if len(conn.before)>0:
                    logging.debug(str(conn.before, 'utf-8').strip()) 
            for dir in self.ins_dirs:
                conn.sendline('mkdir ' + dir)
                conn.expect('.*mkdir ' + dir + "\r\n")
                conn.expect("sftp> ")
                if len(conn.before)>0:
                    logging.warning("Sftp message(mkdir " + dir + "): " + str(conn.before, 'utf-8').strip())
                conn.sendline('put -r ' +  dir)
                conn.expect('.*put -r ' + dir + "\r\n")
                end=0
                while end==0:
                    #wait 2s after last message
                    end = conn.expect(["\r\n", pexpect.TIMEOUT], timeout=2)
                    if end == 0 and len(conn.before)>0:
                        logging.debug("Sftp message(mkdir " + dir + "): " + str(conn.before, 'utf-8').strip())
 
    def get_command(self, name):
        """Find install file according to name and return command for running"""
        # use / instead join because destination os is linux and is not 
        # same with current os
        dest_path = self.copy_path + '/' + __ins_files__[name]
        return __python_exec__ + " " + dest_path
    
    @staticmethod
    def get_result_dir():
        """Return dir for savings results"""
        try:
            path = os.path.join(__install_dir__, __root_dir__)
            if not os.path.isdir(path):
                os.makedirs(path)
            path = os.path.join(__install_dir__, "res")
            if not os.path.isdir(path):
                os.makedirs(path)
        except:
            return "."
        return path
        
