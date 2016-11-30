import sys
import os
import re
import shutil

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
        if mess:
            return "Downlding file over SFTP ..."
        errors=[]
        logs=[]
        file = "testout.txt"
        file_text = "This is test"
        res_dir =  os.path.join(os.path.dirname(os.path.realpath(__file__)), "tmp_tests")
        os.mkdir(res_dir)
        try:            
            self.conn.download_file(file, res_dir)
            logs.append("File {0} is downloaded".format(file))
            res_file = os.path.join(res_dir, file)
            if not os.path.isfile(res_file):
                logs.append("Can't find downloaded file !!!")
                errors.append("Can't find downloaded file")
            else:
                with open(res_file, 'r') as f:
                    lines = f.readlines()
                    if len(lines) != 1 or lines[0] != file_text:
                        logs.append("Downloaded file is corrupted !!!")
                        errors.append("Downloaded file is corrupted")
        except conn.SshError as err:
            logs.append("Can't download file over SFTP !!!")
            errors.append(err.message)
        
        shutil.rmtree(res_dir, ignore_errors=True)
        
        return logs, errors

    def download_dir(self, mess=False):
        """Dowload file over sftp"""
        if mess:
            return "Downlding folder over SFTP ..."
        errors=[]
        logs=[]
        dir = "remote_tests"
        source_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "remote_tests")
        res_dir =  os.path.join(os.path.dirname(os.path.realpath(__file__)), "tmp_tests")
        os.mkdir(res_dir)
        try:            
            self.conn.download_dir(dir, res_dir)
            logs.append("Folder {0} is downloaded".format(dir))
            names = os.listdir( source_dir)
            is_error = False
            for name in names:                        
                path = os.path.join(res_dir)
                if not os.path.isfile(path) and not os.path.isdir(path):
                    errors.append("Can't find downloaded file: {0}".format(path))
                    is_error = True
            if is_error:                    
                logs.append("Can't find one or more downloaded files !!!")
            else:
                logs.append("All downloaded files is checked")
        except conn.SshError as err:
            logs.append("Can't download directory over SFTP !!!")
            errors.append(err.message)
        
        shutil.rmtree(res_dir, ignore_errors=True)
        
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
            if re.search("command not found", version) :                
                logs.append("Can't find out python version !!!")
                errors.append("Command '{0}' is not valid perl interpreter.".format(
                    python_env.python_exec))
            v = re.search(r'^Python\s+(\d+)\.(\d+)\.(\d+)\s*$', version)
            if not v:                
                logs.append("Can't find out python version !!!")
                errors.append("Python command return: {0}".format(
                    version))
                return logs, errors   
            v1 = v.group(1)
            v2 = v.group(2)
            v3 = v.group(3)
            logs.append("Python version is: {0}.{1}.{2}".format(v1, v2, v3))
            if int(v1)<3 or (int(v1)==3 and int(v2)<2):
                errors.append("Python version is too low. Vewsion 3.1 or higher is required.")
        except conn.SshError as err:
            logs.append("Can't find out python version !!!")
            errors.append(err.message)        
        return logs, errors
        
    def test_flow123d(self, mess,  env):
        """Test flow123d properties"""
        if mess:
            return "Testing flow123d installation ..."
        errors=[]
        logs=[]
        try:  
            # prepare python env
            python_env, libs_env = ConfFactory.get_env_conf(env)
            Installation.prepare_python_env_static(self.conn.conn, python_env, False)            
            flow_help, err, wrns = self.conn.get_flow123_help(env.flow_path,  env.cli_params)
            if len(wrns)>0:
                for wrn in wrns:
                    logs.append("{0} !!!".format(wrn))
            if len(err)>0:
                logs.append("Can't process Flow123d !!!")
                errors.append("Flow123d processing error: " + err)        
            elif len(flow_help)==0:
                logs.append("Flow123d help is empty !!!")
                errors.append("Flow123d help is empty")
            else:
                if flow_help[0]!="Allowed options:":
                    logs.append("Incorrect Flow123d help file !!!")
                    errors.append("Incorrect Flow123d help file:\n" + "\n".join(flow_help))                    
        except conn.SshError as err:
            logs.append("Can't obtain flow123d help !!!")
            errors.append(err.message)         
        return logs, errors
        
    def run_python(self, mess, env):
        """Run python script on Remote"""
        if mess:
            return "Python script running test ..."
        errors=[]
        logs=[]
        file = "testout.txt"
        file_text = "This is test"
        try:  
            # prepare python env
            python_env, libs_env = ConfFactory.get_env_conf(env)
            Installation.prepare_python_env_static(self.conn.conn, python_env, False)
            self.conn.test_python_script(python_env.python_exec,
                "remote_tests/test_env.py",  file, file_text)
            logs.append("Python script is finished succesfuly")
        except conn.SshError as err:
            logs.append("Errors occured during running python script!!!")
            errors.append(err.message) 
        try:
            ok = False  
            files = self.conn.ls_dir("./")
            for f in files:
                if f=='testout.txt':
                    ok = True                    
            if ok:
                logs.append("Python script create test file")
            else:
                logs.append("Can't find created output file !!!")
                errors.append("Can't find created output file")
        except conn.SshError as err:
            logs.append("Can't check script output file!!!")
            errors.append(err.message) 
        return logs, errors
        
    def test_pbs(self, mess=False):
        """Test pbs version and list of queues"""
        if mess:
            return "Testing pbs system ..."
        errors=[]
        logs=[]
        try:  
            version, queues = self.conn.get_pbs_info()
            if len(version)==0:
                logs.append("Can't obtain pbs version !!!")
            elif not version[0].startswith('version'):
                logs.append("Pbs system checking error !!!")
                errors.append("Qstat return: {0}".format("\n".join(version)))
                return logs, errors
            else:
                logs.append("Pbs version is {0}".format(version))
            if len(queues)==0:
                logs.append("Can't obtain pbs list of pbs queues !!!")
            else:
                logs.append("Pbs queues:\n{0}".format(self._format_pbs_ques(queues)))
        except conn.SshError as err:
            logs.append("Pbs system checking error !!!")
            errors.append(err.message)         
        return logs, errors
        
    def _format_pbs_ques(self, queues):
        """Return list of queues as string."""
        res = ""
        for queue in queues:
            name = re.search(r'^(\S+)\s+', queue)
            if name:                
                res += name.group(1) + ", "
        res = res.strip(", ")
        return res
            
