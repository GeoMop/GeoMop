import sys
import os

if sys.platform == "win32":
    import ui.helpers.ssh.win_conn as conn
else:
    import ui.helpers.ssh.linux_conn as conn
from ui.data.config_builder import ConfFactory
from  communication.installation import Installation

class Tests():
    def __init__(self,ssh):
        self.ssh = ssh
        self.conn = None
        self.remote_dir = None
    
    def open_connection(self, mess=False):
        """Inicoalize ssh connection"""
        if mess:
            return "Opening SSH connection ..."
        errors=[]
        logs=[]
        try:
            self.conn=conn.Conn(self.ssh)
            self.conn.connect()
            logs.append("SSH connection is opened")
            try:
                self.remote_dir = self.conn.pwd()
                logs.append("Remote directory is: "  + self.remote_dir )
            except Exception as err:
                logs.append("Can't recognise user directory !!!")
                errors.append(str(err))
                self.conn.disconnect()
        except conn.SshError as err:
            logs.append("Can't open SSH Connection !!!")
            errors.append(err.message)            
        return logs, errors
        
    def close_connection(self, mess=False):
        """Close ssh connection"""
        if mess:
            return "Closing SSH connection ..."
        errors=[]
        logs=[]
        try:            
            self.conn.disconnect()
            logs.append("SSH connection is closed")
        except conn.SshError as err:
            logs.append("Can't close SSH Connection !!!")
            errors.append(err.message)        
        return logs, errors
        
    def create_dir_struc(self, mess=False):
        """Create directory on remote"""
        if mess:
            return "Testing directory operations in user directory ..."
        errors=[]
        logs=[]
        try: 
            self.conn.create_dir("JobPanelTestDirectory")
            logs.append("Job panel test directory is created")
            self.conn.cd("JobPanelTestDirectory")
            logs.append("Current directory is changed to new directory")
            self.conn.create_dir("remote_tests")
            logs.append("Test directory is created")
            dirs = self.conn.ls_dir("./")
            if len(dirs)==1 and dirs[0]=="remote_tests":
                logs.append("Test directory is checked")
            else:
                logs.append("Can't find created directory on remote !!!")
                errors.append("Can't find created directory on remote") 
        except conn.SshError as err:
            logs.append("Error occurred during directory operation !!!")
            errors.append(err.message)        
        
        return logs, errors
        
    def open_sftp(self, mess=False):
        """Inicoalize sftp connection"""
        if mess:
            return "Opening SFTP connection ..."
        errors=[]
        logs=[]
        try:
            local = os.path.dirname(os.path.realpath(__file__))
            self.conn.connect_sftp(local, "JobPanelTestDirectory")
            logs.append("SFTP connection is opened")
        except conn.SshError as err:
            logs.append("Can't open SFTP Connection !!!")
            errors.append(err.message)            
        return logs, errors
        
    def close_sftp(self, mess=False):
        """Close sftp connection"""
        if mess:
            return "Closing SFTP connection ..."
        errors=[]
        logs=[]
        try:            
            self.conn.disconnect_sftp()
            logs.append("SFTP connection is closed")
        except conn.SshError as err:
            logs.append("Can't close SFTP Connection !!!")
            errors.append(err.message)        
        return logs, errors
        
    def upload_file(self, mess=False):
        """Upload file over sftp"""
        if mess:
            return "Uploading file over SFTP ..."
        errors=[]
        logs=[]
        file = "test_libs.py"
        try:            
            self.conn.upload_file(file)
            logs.append("File {0} is uploaded".format('test_libs.py'))
            ok = False
            files = self.conn.ls_dir("./")
            for f in files:
                if f=='test_libs.py':
                    ok = True                    
            if not ok:
                logs.append("Can't find uploaded file on remote !!!")
                errors.append("Can't find uploaded file on remote")        
        except conn.SshError as err:
            logs.append("Can't upload file over SFTP !!!")
            errors.append(err.message)        
        return logs, errors
        
    def upload_dir(self, mess=False):
        """Upload dir over sftp"""
        if mess:
            return "Uploading directory over SFTP ..."
        errors=[]
        logs=[]
        dir = "remote_tests"
        try:            
            self.conn.upload_dir(dir)
            logs.append("Directory {0} is uploaded".format('remote_tests'))
            ok = False
            files = self.conn.ls_dir("./remote_tests")
            for f in files:
                if f=='test_env.py':
                    ok = True                    
            if not ok:
                logs.append("Can't find uploaded files on remote !!!")
                errors.append("Can't find uploaded files on remote")        
        except conn.SshError as err:
            logs.append("Can't upload directory over SFTP !!!")
            errors.append(err.message)        
        return logs, errors
        
    def download_file(self, mess=False):
        """Dowload file over sftp"""
        errors=[]
        logs=[]
        
        return logs, errors

    def download_dir(self, mess=False):
        """Dowload file over sftp"""
        errors=[]
        logs=[]
        
        return logs, errors
        
    def remove_dir(self, mess=False):
        """Remove directory directory remote"""
        if mess:
            return "Removing user directory ..."
        errors=[]
        logs=[]
        try:
            self.conn.cd(self.remote_dir)
            logs.append("Current directory is changed to user directory")
            self.conn.remove_dir("JobPanelTestDirectory")
            logs.append("Test directory is removed")
        except conn.SshError as err:
            logs.append("Can't open SSH Connection !!!")
            errors.append(err.message)            
        return logs, errors
        
        
        return logs, errors
        
    def test_python(self, mess, env):
        """Test python properties"""
        if mess:
            return "Testing remote python version ..."
        errors=[]
        logs=[]
        try:  
            # prepare python env
            python_env, libs_env = ConfFactory.get_env_conf(env)
            Installation.prepare_python_env_static(self.conn.conn, python_env, False)            
            version = self.conn.get_python_version(python_env.python_exec)
            logs.append("Python version is: {0}".format(version))
        except conn.SshError as err:
            logs.append("Can't find out python version !!!")
            errors.append(err.message)        
        return logs, errors
        
    def test_flow123d(self, mess=False):
        """Test flow123d properties"""
        errors=[]
        logs=[]
        
        return logs, errors
        
    def run_python(self, mess=False):
        """Run python script on Remote"""
        errors=[]
        logs=[]
        
        return logs, errors
        
    def test_pbs(self, mess=False):
        """Test pbs properties"""
        errors=[]
        logs=[]    
        
        return logs, errors
