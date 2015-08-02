"""class represent instalation"""
import os
import re
import pexpect
import logging

__install_dir__ = os.path.split(
    os.path.dirname(os.path.realpath(__file__)))[0]
__ins_files__ = {}
__ins_files__['delegator'] = "delegator.py"
__ins_dir__ = []
__ins_dir__.append("communication")
__ins_dir__.append("data")
__ins_dir__.append('twoparty')
__root_dir__ = "jobs"
__python_exec__ = "python3"

class Installation:
    """Files with installation (python files and configuration files) is selected 
        and send to set folder"""
    def __init__(self):
        self.copy_path = None
        """installation file path"""

    def create_install_dir(self, pexpect_conn):
        """Copy installation files"""
        pexpect_conn.sendline('pwd')
        pexpect_conn.expect(".*pwd\r\n")
        ret = str(pexpect_conn.readline(), 'utf-8').strip()
        searchObj = re.search( '^(.*):\s(/.*)$',ret)
        # use / instead join because destination os is linux and is not 
        # same with current os
        self.copy_path = searchObj.group(2) + '/' + __root_dir__
        
        pexpect_conn.sendline('mkdir ' + __root_dir__)
        pexpect_conn.expect(".*mkdir " + __root_dir__ + "\r\n")
        pexpect_conn.expect("sftp> ")
        if len(pexpect_conn.before)>0:
            logging.warning("Sftp message (mkdir root): " + str(pexpect_conn.before, 'utf-8').strip())      
        pexpect_conn.sendline('cd ' + __root_dir__)
        pexpect_conn.expect('.*cd ' + __root_dir__ + "\r\n")
        pexpect_conn.expect("sftp> ")
        if len(pexpect_conn.before)>0:
            logging.warning("Sftp message (cd root): " + str(pexpect_conn.before, 'utf-8').strip()) 
        pexpect_conn.sendline('mkdir res')
        pexpect_conn.expect(".*mkdir res\r\n")
        pexpect_conn.expect("sftp> ")
        if len(pexpect_conn.before)>0:
            logging.warning("Sftp message(mkdir res): " + str(pexpect_conn.before, 'utf-8').strip()) 
        pexpect_conn.sendline('lcd ' + __install_dir__)
        pexpect_conn.expect('.*lcd ' + __install_dir__ + "\r\n")
        for name in __ins_files__:
            pexpect_conn.sendline('put ' +  __ins_files__[name])
            pexpect_conn.expect('sftp> put ' + __ins_files__[name] + "\r\n")
            pexpect_conn.expect("sftp> ")
            if len(pexpect_conn.before)>0:
                logging.debug(str(pexpect_conn.before, 'utf-8').strip()) 
        for dir in __ins_dir__:
            pexpect_conn.sendline('mkdir ' + dir)
            pexpect_conn.expect('.*mkdir ' + dir + "\r\n")
            pexpect_conn.expect("sftp> ")
            if len(pexpect_conn.before)>0:
                logging.warning("Sftp message(mkdir " + dir + "): " + str(pexpect_conn.before, 'utf-8').strip())
            pexpect_conn.sendline('put -r ' +  dir)
            pexpect_conn.expect('.*put -r ' + dir + "\r\n")
            end=0
            while end==0:
                #wait 2s after last message
                end = pexpect_conn.expect(["\r\n", pexpect.TIMEOUT], timeout=2)
                if end == 0 and len(pexpect_conn.before)>0:
                    logging.debug("Sftp message(mkdir " + dir + "): " + str(pexpect_conn.before, 'utf-8').strip())
 
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
        
