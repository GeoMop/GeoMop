"""class represent instalation"""
import sys
import os
import re
import logging
import copy
import subprocess
import uuid
import time

from locks import Lock, LockFileError

logger = logging.getLogger("Remote")

__install_dir__ = os.path.split(
    os.path.dirname(os.path.realpath(__file__)))[0]
__lock_file__ = "locks.py"
__ins_files__ = {}
__ins_files__['delegator'] = "delegator.py"
__ins_files__['job'] = "job.py"
__ins_files__['remote'] = "remote.py"
__ins_files__['test_task'] = "test_task.py"
__ins_files__['mj_service'] = "mj_service.py"
__ins_files__['job_configurations'] = "job_configurations.json"
__ins_files__['remove_pyc'] = "remove_pyc.py"
__ins_dirs__ = []
__ins_dirs__.append("communication")
__ins_dirs__.append("helpers")
__ins_dirs__.append("data") 
__ins_dirs__.append("twoparty") 
__ins_libs_log__ = "install_job_libs.log"
__root_dir__ = "js_services"
__jobs_dir__ = "jobs"
__logs_dir__ = "log"
__conf_dir__ = "mj_conf"
__result_dir__ = "res"
__status_dir__ = "status"
__lib_dir__ = "ins-lib"

class Installation:
    """Files with installation (python files and configuration files) is selected 
        and send to set folder"""
    def __init__(self, mj_name):
        self.mj_name = mj_name
        """folder name for multijob data"""
        self.copy_path = None
        """installation file path"""
        self.ins_files = copy.deepcopy(__ins_files__)
        """files to install"""
        self.ins_dirs = copy.deepcopy(__ins_dirs__)
        """directories to install"""
        self.python_env = None
        """python running envirounment"""
        self.libs_env = None
        """libraries running envirounment"""
        self.app_version = None
        """
        Applicationj version. If version in remote installation is different
        new instalation is created
        """        
        self.data_version = None
        """
        Long id of configuration. If  in remote installation is different
        id new configuration is reloaded
        """
        self.instalation_fails_mess = None        
        """
        if installation fail, this variable contain instalation message,
        that is send.
        """
        
    def set_env_params(self, python_env,  libs_env):
        """Set install specific settings"""
        self.python_env = python_env
        self.libs_env = libs_env
        
    def set_version_params(self, app_version, data_version):
        """Set install specific settings"""
        self.app_version = app_version
        self.data_version = data_version

    def local_copy_path(self):
        """Set copy path for local installation"""
        self.copy_path = __install_dir__
        
    def _create_dir(self, conn, dir, log=True):
        result = None
        if sys.platform == "win32":
            res = conn.mkdir(dir)
            if len(res)>0:
                result = "Sftp message (mkdir " + dir + "): " + res
                if log:
                    logger.warning(result)
        else:
            conn.sendline('mkdir ' + dir)
            conn.expect(".*mkdir " + dir + "\r\n")
            conn.expect("sftp> ")
            if len(conn.before)>0:
                result = "Sftp message (mkdir " + dir + "): " + str(conn.before, 'utf-8').strip()
                if log:
                    logger.warning(result)
        return result

    def create_install_dir(self, conn, ssh):
        """Create installation directory, return if should installation continue"""
        if sys.platform == "win32":
            self.copy_path = conn.pwd() + '/' + __root_dir__
            if self.is_local_and_remote_same(ssh):
                logger.debug("Installation and local directory is same")                
                return False
            if self._is_install_lock(ssh):
                logger.debug("Other installation is running")
                return False
            self._create_dir(conn, __root_dir__, False)
            res = conn.cd(__root_dir__)
            if len(res)>0:
                logger.warning("Sftp message (cd root): " + res)            
            conn.set_sftp_paths( __install_dir__, self.copy_path)
            res = conn.put(__lock_file__) 
            if len(res)>0:
                logger.warning("Sftp message (put '" + __lock_file__ + "'): " + res)
        else:
            import pexpect 

            conn.sendline('pwd')
            conn.expect(".*pwd\r\n")
            ret = str(conn.readline(), 'utf-8').strip()
            searchObj = re.search( '^(.*):\s(/.*)$',ret)
            # use / instead join because destination os is linux and is not 
            # same with current os
            self.copy_path = searchObj.group(2) + '/' + __root_dir__
            if self.is_local_and_remote_same(ssh):
                logger.debug("Installation and local directory is same")                
                return False
            if self._is_install_lock(ssh):
                logger.debug("Other installation is running")
                return True
            self._create_dir(conn, __root_dir__, False)
            conn.sendline('cd ' + __root_dir__)
            conn.expect('.*cd ' + __root_dir__ + "\r\n")
            conn.expect("sftp> ")
            if len(conn.before)>0:
                logger.warning("Sftp message (cd root): " + str(conn.before, 'utf-8').strip()) 
            conn.sendline('lcd ' + __install_dir__)
            conn.expect('.*lcd ' + __install_dir__ + "\r\n")
            conn.sendline('put ' +  __lock_file__)
            conn.expect('sftp> put ' + __lock_file__ + "\r\n")
            end=0
            while end==0:
                #wait 3s after last message
                end = conn.expect(["\r\n", pexpect.TIMEOUT], timeout=3)
                if end == 0 and len(conn.before)>0:
                    logger.debug("Sftp message(put " + __lock_file__  + "): " + str(conn.before, 'utf-8').strip())
        return True

    def init_copy_path(self, conn):
        if sys.platform == "win32":
            self.copy_path = conn.pwd() + '/' + __root_dir__
        else:
            conn.sendline('pwd')
            conn.expect(".*pwd\r\n")
            self.copy_path = str(conn.readline(), 'utf-8').strip() + '/' + __root_dir__

    def lock_installation(self):
        """Set installation locks, return if should installation continue"""
        lock = Lock(self.mj_name, __install_dir__)
        try:
            if lock.lock_app(self.app_version, self.data_version, 
                self.get_result_dir(), __conf_dir__)<1:
                return False
        except LockFileError as err:
            logger.warning("Lock instalation error: " + str(err))
            return False
        return True
    
    def unlock_installation(self):
        """Unset installation locks"""
        lock = Lock(self.mj_name, __install_dir__)
        try:
            if not lock.unlock_install():
                return False
        except LockFileError as err:
            logger.warning("Unock instalation error: " + str(err))
            return False
        return True
    
    @staticmethod  
    def unlock_application(mj_name):
        """Unset application locks"""
        lock = Lock(mj_name, __install_dir__)
        try:
            if not lock.unlock_app():
                return False
        except LockFileError as err:
            logger.warning("Lock application error: " + str(err))
            return False
        return True        

    @classmethod
    def lock_lib(cls):
        """Set ilibrary lock"""
        path = os.path.join( __install_dir__, __lib_dir__)
        lock = Lock("", __install_dir__)
        try:
            if not lock.lock_lib(path):
                return False
        except LockFileError as err:
            logger.warning("Lock lib error: " + str(err))
            cls.unlock_lib()
            return False
        return True
     
    @staticmethod   
    def unlock_lib():
        """Set installation locks, return if should installation continue"""
        lock = Lock("", __install_dir__)
        try:
            if not lock.unlock_lib():
                return False
        except LockFileError as err:
            logger.warning("Unock lib error: " + str(err))
            return False
        return True

        
    def lock_installation_over_ssh(self, conn, ssh, lock):
        """
        Set installation locks, return if should installation continue
        
        Lock over ssh is specific, becose lock is processed during
        ssh connection. In start of application is lock repeated.
        
        :return: is app need install, is data need install
        """
        mj_dir = self.copy_path + "/" + __jobs_dir__ + "/" + self.mj_name
        res_dir = mj_dir + "/" + __result_dir__
        
        command = self.python_env.python_exec + " "
        command += '"' + self.copy_path + '/' + __lock_file__ + '" '
        command += self.mj_name + " "
        command += '"' + self.copy_path + '" '
        command += self.app_version + " "
        command += self.data_version + " "
        command += '"' + res_dir + '" '
        command += '"' + __conf_dir__ + '" '
        if lock:
            command += "Y"
        else:
            command += "N"
        
        if sys.platform == "win32":
            res, mess = conn.exec_ret(command, "--")
            if not res:
                logger.warning("Run python file: " + mess)  
            else:
                if res == "1":
                    return False, True
                if res == "2" or res == "3":
                    return True, True
        else:            
            import pexpect   
            
            command_test = self.python_env.python_exec + " "
            command_test += '"' + self.copy_path + '/' + __lock_file__ + '" '
            command_test += "test"
                        
            ssh.sendline(command_test)
            res = ssh.expect( ["ok", pexpect.TIMEOUT], timeout=5)
            if res>0:
                logger.error("Lock error:" + str(ssh.before,'utf-8').strip())
                ssh.prompt()
                self.instalation_fails_mess = "Can't run lock file in python environment"
                return False, False                
            
            logger.debug("Command:" + command)
            ssh.sendline(command)
            res = ssh.expect( ["--0--", "--1--", "--2--", "--3--", "---1--", pexpect.TIMEOUT], timeout=360)
            logger.debug("Lock function result:" + str(res))
            if res == 1:
                return False, True
            if res == 2 or res == 3:
                return True, True
            if res>3:                
                logger.warning("Lock error:" + str(ssh.before,'utf-8').strip())
                ssh.prompt()
        return False, False

    def copy_data_files(self, conn, ssh):
        """Copy installation files"""
        if sys.platform == "win32":
            # copy mj configuration directory
            res = conn.cd(self.copy_path)
            if len(res)>0:
                logger.warning("Sftp message (cd root): " + res)
            mjs_dir = __jobs_dir__  + '/' + self.mj_name
            self._create_dir(conn, mjs_dir, False)
            self._create_dir(conn, mjs_dir + '/' + __conf_dir__, False)  
            conf_path = os.path.join(__install_dir__, mjs_dir)
            #conf_path = os.path.join(os.path.join(__install_dir__, mjs_dir), __conf_dir__)
            if os.path.isdir(conf_path):
                conn.set_sftp_paths( conf_path , self.copy_path + '/' +  mjs_dir)
                res = conn.put_r(__conf_dir__) 
                if len(res)>0:
                    logger.warning("Sftp message (put -r '" + __conf_dir__ + "'): " + res)
        else:
            import pexpect            
            # copy mj configuration directory
            logger.debug("Copy data to: " + self.copy_path)                               
            conn.sendline('cd ' + self.copy_path)
            conn.expect('.*cd ' + self.copy_path + "\r\n")
            conn.expect("sftp> ")
            if len(conn.before) > 0:
                logger.warning("Sftp message (cd root): " + str(conn.before,
                                                                 'utf-8').strip()) 
                                                                
            mjs_dir = __jobs_dir__  + '/' + self.mj_name
            self._create_dir(conn, mjs_dir, False)
            self._create_dir(conn, mjs_dir + '/' + __conf_dir__, False)  
            conf_path = os.path.join(os.path.join(__install_dir__, mjs_dir), __conf_dir__)
            if os.path.isdir(conf_path):
                mj_path = os.path.join(__install_dir__, mjs_dir)
                conn.sendline('cd ' + mjs_dir)
                conn.expect('.*cd ' + mjs_dir + "\r\n")
                conn.expect("sftp> ")
                if len(conn.before) > 0:
                    logger.warning("Sftp message (cd " + mjs_dir + "): " +
                                    str(conn.before, 'utf-8').strip())
                conn.sendline('lcd ' + mj_path)
                conn.expect('.*lcd ' + mj_path)
                conn.sendline('put -r ' + __conf_dir__)
                conn.expect('.*put -r ' + __conf_dir__ + "\r\n")
                end=0
                while end==0:
                    #wait 3s after last message
                    end = conn.expect(["\r\n", pexpect.TIMEOUT], timeout=3)
                    if end == 0 and len(conn.before)>0:
                        logger.debug(
                            "Sftp message(put -r " + __conf_dir__ + "): " +
                            str(conn.before, 'utf-8').strip())

    def copy_install_files(self, conn, ssh):
        """Copy installation files"""
        if sys.platform == "win32":
            self._create_dir(conn, __jobs_dir__)
            mjs_dir = __jobs_dir__  + '/' + self.mj_name
            self._create_dir(conn, mjs_dir)
            self._create_dir(conn, mjs_dir + '/' + __result_dir__)
            conn.set_sftp_paths( __install_dir__, self.copy_path)
            for name in self.ins_files:
                res = conn.put(__ins_files__[name]) 
                if len(res)>0:
                    logger.warning("Sftp message (put '" + __ins_files__[name] + "'): " + res)
            for dir in self.ins_dirs:
                res = conn.put_r(dir) 
                if len(res)>0:
                    logger.warning("Sftp message (put -r '" + dir + "'): " + res)
        else:
            import pexpect            
            self._create_dir(conn, __jobs_dir__)
            mjs_dir = __jobs_dir__  + '/' + self.mj_name
            self._create_dir(conn, mjs_dir)            
            self._create_dir(conn, mjs_dir + '/' + __result_dir__)
            conn.sendline('cd ' + self.copy_path)
            conn.expect('.*cd ' + self.copy_path + "\r\n")
            conn.expect("sftp> ")
            if len(conn.before) > 0:
                logger.warning("Sftp message (cd root): " + str(conn.before,
                                                                 'utf-8').strip())
            conn.sendline('lcd ' + __install_dir__)
            conn.expect('.*lcd ' + __install_dir__ + "\r\n")
            for name in self.ins_files:
                conn.sendline('put ' +  __ins_files__[name])
                conn.expect('sftp> put ' + __ins_files__[name] + "\r\n")
                end=0
                while end==0:
                    #wait 3s after last message
                    end = conn.expect(["\r\n", pexpect.TIMEOUT], timeout=3)
                    if end == 0 and len(conn.before)>0:
                        logger.debug("Sftp message(put " + __ins_files__[name]  + "): " + str(conn.before, 'utf-8').strip())
            for dir in self.ins_dirs:
                self._create_dir(conn, dir)
                conn.sendline('put -r ' +  dir)
                conn.expect('.*put -r ' + dir + "\r\n")
                end=0
                while end==0:
                    #wait 5s after last message
                    end = conn.expect(["\r\n", pexpect.TIMEOUT], timeout=5)
                    if end == 0 and len(conn.before)>0:
                        logger.debug("Sftp message(put -r " + dir + "): " + str(conn.before, 'utf-8').strip())
 
    def get_results(self, conn):
        """Copy installation files"""
        res_local = self.get_result_dir_static(self.mj_name)
        res_dir = self.copy_path  + '/' + __jobs_dir__  + '/' + self.mj_name + '/' + __result_dir__
        if sys.platform == "win32": 
            conn.set_sftp_paths(res_local, res_dir)
            res = conn.get_r("*") 
            if len(res)>0:
                logger.warning("Sftp message (get -r '" + res_dir + "\\*'): " + res)
        else:
            import pexpect 
            
            conn.sendline('cd ' + res_dir)
            conn.expect('.*cd ' + res_dir + "\r\n")
            conn.expect("sftp> ")
            conn.sendline('lcd ' + res_local)
            conn.expect('.*lcd ' + res_local + "\r\n")
            conn.sendline('get -r *')
            conn.expect(r'.*get -r \*\r\n')
            end=0
            while end==0:
                #wait 2s after last message
                end = conn.expect(["\r\n", pexpect.TIMEOUT], timeout=2)
                if end == 0 and len(conn.before)>0:
                    logger.debug("Sftp message(get -r *): " + str(conn.before, 'utf-8').strip())
     
    def is_local_and_remote_same(self, conn):
        """Test if local and remote directory is same (open file with uuid in local and try find it in remote)"""
        result = False
        local = os.path.join(self.get_result_dir_static(self.mj_name), 'test666iden')
        remote = self.copy_path  + '/' + __jobs_dir__  + '/' + self.mj_name + '/' + __result_dir__ +'/' + 'test666iden'
        uid = str(uuid.uuid4())
        f=open(local, 'w')
        f.write(uid)
        f.close()
        if sys.platform == "win32": 
            # ToDo
            result = False
        else:
            import pexpect 
            
            conn.sendline('ls ' + remote)
            conn.expect('.*ls ' + remote + "\r\n")
            res = conn.expect([remote + ".*", ".*ls.*", pexpect.TIMEOUT])
            if res == 0:
                conn.sendline('head ' + remote)
                conn.expect('.*head ' + remote + "\r\n")
                res = conn.expect( ['.*' + uid + '.*', pexpect.TIMEOUT ])
                if res == 0:
                    result = True            
        os.remove(local)
        return result
        
    def _is_install_lock(self, conn):
        """Test if install lock is set in lock directory"""
        import locks
        locks.__lock_dir__
        lock_file = self.copy_path  + '/' + locks.__lock_dir__  + '/install.lock'
        if sys.platform == "win32": 
            # ToDo
            return False
        else:
            import pexpect 
            
            conn.sendline('ls ' + lock_file)
            conn.expect('.*ls ' + lock_file + "\r\n")
            res = conn.expect([lock_file + ".*", ".*ls.*", pexpect.TIMEOUT])
            if res == 0:
                return True
        return False
        
    def get_command(self, name, mj_name, mj_id):
        """Find install file according to name and return command for running"""
        # use / instead join because destination os is linux and is not 
        # same with current os
        command = self.copy_path + '/' + __ins_files__[name] + " " + mj_name
        if mj_id is not None:
            command += " " + mj_id
        return self.python_env.python_exec + " " + command
    
    def get_args(self, name, mj_name, mj_id):
        # use / instead join because destination os is linux and is not 
        # same with current os
        dest_path = self.copy_path + '/' + __ins_files__[name]
        if sys.platform == "win32": 
            if mj_id is None:
                return [self.python_env.python_exec,dest_path, mj_name]
            return [self.python_env.python_exec,dest_path, mj_name, mj_id]
        if mj_id is None:
            return [self.python_env.python_exec,dest_path, mj_name, "&", "disown"]
        return [self.python_env.python_exec,dest_path, mj_name, mj_id, "&", "disown"]
        
    def get_interpreter(self):
        """return python interpreter with path"""
        return self.python_env.python_exec

    def get_command_only(self, name, mj_name, mj_id):
        """return command with path"""
        command = self.copy_path + '/' + __ins_files__[name] + " " + mj_name
        if mj_id is not None:
            command += " " + mj_id
        return command

    @staticmethod
    def get_central_log_dir_static():
        """Return dir for central log"""
        try:
            path = os.path.join(__install_dir__, "log")
            if not os.path.isdir(path):
                os.makedirs(path)
        except Exception as err:
            logger.warning("Get central log dir error: " + str(err))
            return "."
        return path

    @staticmethod
    def get_result_dir_static(mj_name):
        """Return dir for savings results"""
        try:
            path = os.path.join(__install_dir__, __jobs_dir__)
            if not os.path.isdir(path):
                os.makedirs(path)
            path = os.path.join( path,  mj_name)
            if not os.path.isdir(path):
                os.makedirs(path)
            path = os.path.join(path, __result_dir__)
            if not os.path.isdir(path):
                os.makedirs(path)
        except Exception as err:
            logger.warning("Get mj result dir error: " + str(err))
            return "."
        return path
        
    def get_result_dir(self):
        """Return dir for savings results"""
        return self.get_result_dir_static(self.mj_name) 
        
    @staticmethod
    def get_config_dir_static(mj_name):
        """Return dir for configuration"""
        try:
            path = os.path.join(__install_dir__, __jobs_dir__)
            if not os.path.isdir(path):
                os.makedirs(path)
            path = os.path.join( path,  mj_name)
            if not os.path.isdir(path):
                os.makedirs(path)
            path = os.path.join(path,__conf_dir__)
            if not os.path.isdir(path):
                os.makedirs(path)
        except Exception as err:
            logger.warning("Get mj configuration dir error: " + str(err))
            return "."
        return path

    def get_config_dir(self):
        """Return dir for configuration """
        return self.get_config_dir_static(self.mj_name)         

    @staticmethod
    def get_mj_data_dir_static(mj_name):
        """Return dir for savings results"""
        try:
            path = os.path.join(__install_dir__, __jobs_dir__)
            if not os.path.isdir(path):
                os.makedirs(path)
            path = os.path.join( path, mj_name)
            if not os.path.isdir(path):
                os.makedirs(path)
        except Exception as err:
            logger.warning("Get mj data dir error: " + str(err))
            return "."
        return path 

    def get_mj_data_dir(self):
        """
        Return dir for multijob data
        :return:
        """
        return self.get_mj_data_dir_static(self.mj_name)

    @staticmethod
    def get_mj_log_dir_static(mj_name):
        """Return dir for logging"""
        try:
            path = os.path.join(__install_dir__, __jobs_dir__)
            if not os.path.isdir(path):
                os.makedirs(path)
            path = os.path.join( path,  mj_name)
            if not os.path.isdir(path):
                os.makedirs(path)
            path = os.path.join(path, __result_dir__)
            if not os.path.isdir(path):
                os.makedirs(path)
            path = os.path.join(path, __logs_dir__)
            if not os.path.isdir(path):
                os.makedirs(path)
        except Exception as err:
            logger.warning("Get mj result dir error: " + str(err))
            return "."
        return path

    def get_mj_log_dir(self):
        """
        Return dir for multijob logs
        :return:
        """
        return self.get_mj_log_dir_static(self.mj_name)

    def get_status_dir(self):
        """Return dir for savings status"""
        return  self.get_staus_dir_static(self.mj_name)
    
    @staticmethod
    def get_staus_dir_static(mj_name):
        """Return dir for savings status"""
        try:
            path = os.path.join(__install_dir__, __jobs_dir__)
            if not os.path.isdir(path):
                os.makedirs(path)
            path = os.path.join( path,  mj_name)
            if not os.path.isdir(path):
                os.makedirs(path)
            path = os.path.join(path,__status_dir__ )
            if not os.path.isdir(path):
                os.makedirs(path)
        except Exception as err:
            logger.warning("Get mj status dir error: " + str(err))
            return None
        return path 

    def install_job_libs(self):
        """Return dir for savings status"""
        self.install_job_libs_static(self.mj_name, self.python_env, self.libs_env)

    def prepare_ssh_env(self, term):
        self.prepare_python_env_static(term, self.python_env)
        if self.libs_env.start_job_libs:
            self.prepare_mpi_env_static(term, self.libs_env)
    
    @staticmethod
    def prepare_python_env_static(term,  python_env):
        """Prepare python environment for installation"""
        if sys.platform == "win32":
            if python_env.scl_enable_exec is not None:
                mess = term.exec_("scl enable " +  python_env.scl_enable_exec + " bash")
                if mess != "":
                    logger.warning("Enable scl error: " + mess)
            if python_env.module_add is not None:
                mess = term.exec_("module add " +  python_env.module_add)
                if mess != "":
                    logger.warning("Add module error: " + mess)
        else:
            if python_env.scl_enable_exec is not None:
                term.sendline("scl enable " +  python_env.scl_enable_exec + " bash")
                term.expect(".*scl enable " +  python_env.scl_enable_exec + " bash\r\n")
                if len(term.before)>0:
                    logger.warning("Ssh message (scl enable): " + str(term.before, 'utf-8').strip()) 
            if python_env.module_add is not None:
                term.sendline("module add " +  python_env.module_add)
                term.expect(".*module add " +  python_env.module_add + "\r\n")
                if len(term.before)>0:
                    logger.warning("Ssh message (Add module): " + str(term.before, 'utf-8').strip()) 
    
    def prepare_popen_env(self):
        self.prepare_popen_env_static(self.python_env, self.libs_env)
    
    @staticmethod
    def prepare_popen_env_static(python_env, libs_env):
        """prepare envoronment for execution by popen"""
        if python_env.scl_enable_exec is not None:
            subprocess.call(["scl", "enable", python_env.scl_enable_exec,"bash"], shell=True, timeout=10)
        if python_env.module_add is not None:
            subprocess.call(["module", "add", python_env.module_add], shell=True, timeout=10)
        if libs_env.start_job_libs:
            if libs_env.mpi_scl_enable_exec is not None:
                subprocess.call(["scl", "enable", libs_env.mpi_scl_enable_exec,"bash"], shell=True, timeout=10)
            if libs_env.mpi_module_add is not None:
                subprocess.call(["module", "add", libs_env.mpi_module_add], shell=True, timeout=10) 

    @staticmethod
    def prepare_mpi_env_static(term, libs_env):
        """Prepare libs environment for installation"""
        if libs_env.mpi_scl_enable_exec is not None:
            term.sendline("scl enable " +  libs_env.mpi_scl_enable_exec + " bash")
            term.expect(".*scl enable " + libs_env.mpi_scl_enable_exec + " bash\r\n")
            if len(term.before)>0:
                logger.warning("Ssh message (scl enable): " + str(term.before, 'utf-8').strip()) 
        if libs_env.mpi_module_add is not None:
            term.sendline("module add " +  libs_env.mpi_module_add)
            term.expect(".*module add " + libs_env.mpi_module_add + "\r\n")
            if len(term.before)>0:
                logger.warning("Ssh message (Add module): " + str(term.before, 'utf-8').strip()) 

    def get_prepare_pbs_env(self):
        """Get array of commads for loading environment for pbs"""
        res=[]
        if self.python_env.scl_enable_exec is not None:
            res.append("scl enable " + self.python_env.scl_enable_exec + " bash")
        if self.python_env.module_add is not None:
            res.append("module add " + self.python_env.module_add)
        if self.libs_env.start_job_libs:
            if self.libs_env.mpi_scl_enable_exec is not None:
                res.append("scl enable" + self.libs_env.mpi_scl_enable_exec +" bash")
            if self.libs_env.mpi_module_add is not None:
                res.append("module add " + self.libs_env.mpi_module_add)  
        return res        

    @classmethod
    def install_job_libs_static(cls, mj_name, python_env, libs_env):
        """Return dir for savings status"""
        if not cls.lock_lib():
            logger.debug("Libraries is allready installed")
            return
            
        if sys.platform == "win32":
            #ToDo if is needed
            pass
        else:
            import pexpect
            
            term = pexpect.spawn('bash')
            cls.prepare_python_env_static(term, python_env)
            cls.prepare_mpi_env_static(term, libs_env)
            term.sendline('cd twoparty/install')
            time.sleep(1)            
            term.expect('.*cd twoparty/install.*')
            log_file= os.path.join(cls.get_result_dir_static(mj_name), "log")
            log_file= os.path.join(log_file, __ins_libs_log__)
            if libs_env.libs_mpicc is None:
                command = "./install_mpi4.sh " + python_env.python_exec + " &>> " + log_file
            else:
                command = "./install_mpi4.sh " + python_env.python_exec  + " " + libs_env.mpicc +  \
                                 " &>> " + log_file 
            logger.debug("Installation libraries started")
            term.sendline(command)
            time.sleep(1)
            logger.debug("Command: " + command)
            try:
                term.expect('.*'+__ins_libs_log__, timeout=10) 
                logger.debug("1: before:" +  str(term.before, 'utf-8') + ",after:" +  str(term.after, 'utf-8'))
                term.expect('.*install.*', timeout=600)
                logger.debug("2: before:" +  str(term.before, 'utf-8') + ",after:" +  str(term.after, 'utf-8'))
            except pexpect.TIMEOUT:
                msg = str(term.before, 'utf-8').strip()
                if len(msg)<1:
                    msg = "timeout"
                logger.warning("Installation libraries failed ( " +
                                          msg + " )") 
            logger.debug("Installation libraries ended")
            term = term.sendline('exit')
        cls.unlock_lib()
 
 
