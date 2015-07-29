"""class represent instalation"""
import os
import re

__install_dir__ = os.path.split(os.path.split(
    os.path.dirname(os.path.realpath(__file__)))[0])[0]
__ins_files__ = {}
__ins_files__['delegator'] =os.path.join(__install_dir__, "delegator.py")
__ins_dir__ = []
__ins_dir__.append(os.path.join(__install_dir__, "communication"))
__ins_dir__.append(os.path.join(__install_dir__, "data"))
__ins_dir__.append(os.path.join(__install_dir__, "twoparty"))

class Installation:
    """Files with installation (python files and configuration files) is selected 
        and send to set folder"""
    def __init__(self):
        self.copy_path = None
        """installation file path"""

    def create_install_dir(self, dir, pexpect_conn):
        """Copy installation files"""
        pexpect_conn.sendline('pwd')
        pexpect_conn.expect(".*pwd\r\n")
        ret = str(pexpect_conn.readline())[:-5]
        searchObj = re.search( '^(.*):\s(/.*)$',ret)
        # use / instead join because destination os is linux and is not 
        # same with current os
        self.copy_path = searchObj.group(2) + '/' + dir
        
        pexpect_conn.sendline('mkdir ' + dir)
        pexpect_conn.expect('.*mkdir ' + dir + "\r\n")
        pexpect_conn.sendline('cd ' + dir)
        pexpect_conn.expect('.*cd ' + dir + "\r\n")
        for name in __ins_files__:
            pexpect_conn.sendline('put ' +  __ins_files__[name])
            pexpect_conn.expect('sftp> put .*')
        for dir in __ins_dir__:
            pexpect_conn.sendline('put -r ' +  dir)
            pexpect_conn.expect('sftp> put .*')

 
    def get_command(self, name):
        """Find install file according to name and return command for running"""
        orig_path =  __ins_files__[name]
        # use / instead join because destination os is linux and is not 
        # same with current os
        dest_path = self.copy_path + '/' + orig_path[len(__install_dir__):]
        return "python " + dest_path
        
