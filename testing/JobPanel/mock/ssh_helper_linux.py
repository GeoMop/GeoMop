import pxssh
import pexpect
import config
import os

from data import Users

def clear_ssh_installation(data, mj_name):
    dir = '/home/test/js_services'
    conn = _Conn(data, mj_name)
    conn.connect()
    conn.remove_dir(dir)
    conn.disconnect()
    
def check_ssh_installation(data, mj_name):
    INS_FILES1 = ["delegator.py", "job.py", "remote.py",  "mj_service.py", "remove_pyc.py", 
        "locks.py", "communication", "helpers", "data", "twoparty"]
    INS_FILES2 = ["communication.py","communicator.py", "exec_output_comm.py", "__init__.py", 
        "installation.py", "jobs_communicator.py", "pbs_input_comm.py", "pbs_output_comm.py",
        "socket_input_comm.py", "ssh_output_comm.py", "std_input_comm.py"]
    dir = '/home/test/js_services'
    conn = _Conn(data, mj_name)
    conn.connect()
    contents = conn.ls_dir(dir)
    i=0
    for file in contents:
        if file in INS_FILES1:
            i += 1
    assert len(INS_FILES1)==i
    contents = conn.ls_dir(dir + "/communication")
    i=0
    for file in contents:
        if file in INS_FILES2:
            i += 1
    assert len(INS_FILES2)==i
    conn.disconnect()
   
def check_pexpect(data, mj_name):
    conn = _Conn(data, mj_name)
    conn.connect()
    conn.conn.sendline("pwd")
    conn.conn.expect(".*pwd\r\n")
    ret = str(conn.conn.readline(), 'utf-8').strip()
    conn.disconnect()
    assert ret == '/home/tester'

class _Conn():
    def __init__(self,data, mj_name):
        ssh_presets = data.ssh_presets
        resource_presets = data.resource_presets
        mj_preset = data.multijobs[mj_name].preset
        res_preset = resource_presets[mj_preset.resource_preset]
        self.ssh = ssh_presets.get(res_preset.mj_ssh_preset, None)
        self.conn = None
        
    def remove_dir(self,dir):
        command = "rm -rf "+dir
        self.conn.sendline(command)
        ok = self.conn.expect([".*" + command + "\r\n", pexpect.TIMEOUT])        
        if ok != 0:
           assert False, str(self.conn.before, 'utf-8').strip() 
           
    def ls_dir(self,dir):
        command = "ls -m --color='never' "+dir
        self.conn.sendline(command)
        ok = self.conn.expect([".*" + command + "\r\n", pexpect.TIMEOUT])        
        if ok != 0:
           assert False, str(self.conn.before, 'utf-8').strip() 
        ret = str(self.conn.readline(), 'utf-8').strip()
        arr = ret.split(", ")
        return arr
           
    def connect(self):
        cfg_dir = config.__config_dir__
        reg = os.path.join(cfg_dir, "JobPanel", ".reg")
        assert os.path.isfile(reg)         
        u = Users(self.ssh.name, dir, os.path.join(cfg_dir, "JobPanel"), self.ssh.to_pc,  self.ssh.to_remote)
        pwd = u.get_login(self.ssh.pwd, self.ssh.key, "LONG")
        assert pwd == self.ssh.pwd
        assert pwd is not None
        self.conn = pxssh.pxssh()
        try:
            self.conn.login(self.ssh.host, self.ssh.uid,pwd, check_local_ip=False)            
            self.conn.setwinsize(128,512)                    
        except Exception as err:
            assert False, "Connect error:" + str(err)
            self.conn = None
            
    def disconnect(self):
        try:
            self.conn.logout()
        except Exception as err:
            assert False, "Disconnect error:" + str(err)
        self.conn = None

