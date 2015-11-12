"""class represent instalation"""
import sys
import os
import re
import logging
import copy
import time
import subprocess

__install_dir__ = os.path.split(
    os.path.dirname(os.path.realpath(__file__)))[0]
__ins_files__ = {}
__ins_files__['delegator'] = "delegator.py"
__ins_files__['job'] = "job.py"
__ins_files__['test_task'] = "test_task.py"
__ins_files__['mj_service'] = "mj_service.py"
__ins_dirs__ = []
__ins_dirs__.append("communication")
__ins_dirs__.append("helpers")
__ins_dirs__.append("data") 
__ins_dirs__.append("twoparty") 
__root_dir__ = "js_services"
__jobs_dir__ = "jobs"
__conf_dir__ = "mj_conf"
__result_dir__ = "res"
__status_dir__ = "status"

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
        
    def set_env_params(self, python_env,  libs_env):
        """Set install specific settings"""
        self.python_env = python_env
        self.libs_env = libs_env

    def local_copy_path(self):
        """Set copy path for local installation"""
        self.copy_path = __install_dir__
        
    def _create_dir(self, conn, dir):
        if sys.platform == "win32":
            res = conn.mkdir(dir)
            if len(res)>0:
                logging.warning("Sftp message (mkdir " + dir + "): " + res)
        else:
            conn.sendline('mkdir ' + dir)
            conn.expect(".*mkdir " + dir + "\r\n")
            conn.expect("sftp> ")
            if len(conn.before)>0:
                logging.warning("Sftp message (mkdir " + dir + "): " + str(conn.before, 'utf-8').strip())

    def create_install_dir(self, conn):
        """Copy installation files"""
        if sys.platform == "win32":
            self.copy_path = conn.pwd() + '/' + __root_dir__
            self._create_dir(conn, __root_dir__)
            res = conn.cd(__root_dir__)
            if len(res)>0:
                logging.warning("Sftp message (cd root): " + res)
            res = conn.rmdir(self.mj_name)
            if len(res)>0:
                logging.warning("Sftp message (rm " + self.mj_name + "): " + res)
            self._create_dir(conn, __jobs_dir__)
            mjs_dir = __jobs_dir__  + '/' + self.mj_name
            self._create_dir(conn, mjs_dir)
            self._create_dir(conn, mjs_dir + '/' + __conf_dir__)  
            self._create_dir(conn, mjs_dir + '/' + __result_dir__)
            # copy mj configuration directory
            conf_path = os.path.join(os.path.join(__install_dir__, mjs_dir), __conf_dir__)
            if os.path.isdir(conf_path):
                conn.set_sftp_paths( conf_path , self.copy_path + '/' + self.mj_name)
                res = conn.put_r(__conf_dir__) 
                if len(res)>0:
                    logging.warning("Sftp message (put -r '" + __conf_dir__ + "'): " + res)
            conn.set_sftp_paths( __install_dir__, self.copy_path)
            for name in self.ins_files:
                res = conn.put(__ins_files__[name]) 
                if len(res)>0:
                    logging.warning("Sftp message (put '" + __ins_files__[name] + "'): " + res)
            for dir in self.ins_dirs:
                res = conn.put_r(dir) 
                if len(res)>0:
                    logging.warning("Sftp message (put -r '" + dir + "'): " + res)
        else:
            import pexpect            
           
            conn.sendline('pwd')
            conn.expect(".*pwd\r\n")
            ret = str(conn.readline(), 'utf-8').strip()
            searchObj = re.search( '^(.*):\s(/.*)$',ret)
            # use / instead join because destination os is linux and is not 
            # same with current os
            self.copy_path = searchObj.group(2) + '/' + __root_dir__
            self._create_dir(conn, __root_dir__)
            conn.sendline('cd ' + __root_dir__)
            conn.expect('.*cd ' + __root_dir__ + "\r\n")
            conn.expect("sftp> ")
            if len(conn.before)>0:
                logging.warning("Sftp message (cd root): " + str(conn.before, 'utf-8').strip()) 
            conn.sendline('rm -r ' + self.mj_name)
            conn.expect(".*rm -r " + self.mj_name + "\r\n")
            ret = str(conn.readline(), 'utf-8').strip()
            conn.expect("sftp> ")
            if len(conn.before)>0:
                logging.warning("Sftp message(rm -rf " + self.mj_name + "): " 
                                          + str(conn.before, 'utf-8').strip()) 
                                          
            self._create_dir(conn, __jobs_dir__)
            mjs_dir = __jobs_dir__  + '/' + self.mj_name
            self._create_dir(conn, mjs_dir)
            self._create_dir(conn, mjs_dir + '/' + __conf_dir__)  
            self._create_dir(conn, mjs_dir + '/' + __result_dir__)
            
            # copy mj configuration directory
            conf_path = os.path.join(os.path.join(__install_dir__, mjs_dir), __conf_dir__)
            if os.path.isdir(conf_path):
                mj_path = os.path.join(__install_dir__, mjs_dir)
                conn.sendline('cd ' + mjs_dir)
                conn.expect('.*cd ' + mjs_dir + "\r\n")
                conn.expect("sftp> ")
                if len(conn.before) > 0:
                    logging.warning("Sftp message (cd " + mjs_dir + "): " +
                                    str(conn.before, 'utf-8').strip())
                conn.sendline('lcd ' + mj_path)
                conn.expect('.*lcd ' + mj_path)
                conn.sendline('put -r ' + __conf_dir__)
                conn.expect('.*put -r ' + __conf_dir__ + "\r\n")
                end=0
                while end==0:
                    #wait 2s after last message
                    end = conn.expect(["\r\n", pexpect.TIMEOUT], timeout=2)
                    if end == 0 and len(conn.before)>0:
                        logging.debug(
                            "Sftp message(put -r " + __conf_dir__ + "): " +
                            str(conn.before, 'utf-8').strip())
            conn.sendline('cd ' + self.copy_path)
            conn.expect('.*cd ' + self.copy_path + "\r\n")
            conn.expect("sftp> ")
            if len(conn.before) > 0:
                logging.warning("Sftp message (cd root): " + str(conn.before,
                                                                 'utf-8').strip())
            conn.sendline('lcd ' + __install_dir__)
            conn.expect('.*lcd ' + __install_dir__ + "\r\n")
            for name in self.ins_files:
                conn.sendline('put ' +  __ins_files__[name])
                conn.expect('sftp> put ' + __ins_files__[name] + "\r\n")
                end=0
                while end==0:
                    #wait 2s after last message
                    end = conn.expect(["\r\n", pexpect.TIMEOUT], timeout=2)
                    if end == 0 and len(conn.before)>0:
                        logging.debug("Sftp message(put " + __ins_files__[name]  + "): " + str(conn.before, 'utf-8').strip())
            for dir in self.ins_dirs:
                self._create_dir(conn, dir)
                conn.sendline('put -r ' +  dir)
                conn.expect('.*put -r ' + dir + "\r\n")
                end=0
                while end==0:
                    #wait 2s after last message
                    end = conn.expect(["\r\n", pexpect.TIMEOUT], timeout=2)
                    if end == 0 and len(conn.before)>0:
                        logging.debug("Sftp message(put -r " + dir + "): " + str(conn.before, 'utf-8').strip())
 
    def get_results(self, conn):
        """Copy installation files"""
        res_local = self.get_result_dir_static(self.mj_name)
        res_dir = self.copy_path  + '/' + __jobs_dir__  + '/' + self.mj_name + '/' + __result_dir__
        if sys.platform == "win32": 
            conn.set_sftp_paths(res_local, res_dir)
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
                    logging.debug("Sftp message(get -r *): " + str(conn.before, 'utf-8').strip())
            
 
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
        return  command

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
            logging.warning("Get mj result dir error: " + str(err))
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
            logging.warning("Get mj configuration dir error: " + str(err))
            return "."
        return path

    def get_config_dir(self):
        """Return dir for configuration """
        return self.get_config_dir_static(self.mj_name)         
        
    def get_mj_data_dir(self):
        """Return dir for savings results"""
        try:
            path = os.path.join(__install_dir__, __jobs_dir__)
            if not os.path.isdir(path):
                os.makedirs(path)
            path = os.path.join( path,  self.mj_name)
            if not os.path.isdir(path):
                os.makedirs(path)
        except Exception as err:
            logging.warning("Get mj data dir error: " + str(err))
            return "."
        return path 
       
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
            logging.warning("Get mj status dir error: " + str(err))
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
                    logging.warning("Enable scl error: " + mess)
            if python_env.module_add is not None:
                mess = term.exec_("module add " +  python_env.module_add)
                if mess != "":
                    logging.warning("Add module error: " + mess)
        else:
            if python_env.scl_enable_exec is not None:
                term.sendline("scl enable " +  python_env.scl_enable_exec + " bash")
                term.expect(".*scl enable " +  python_env.scl_enable_exec + " bash\r\n")
                if len(term.before)>0:
                    logging.warning("Ssh message (scl enable): " + str(term.before, 'utf-8').strip()) 
            if python_env.module_add is not None:
                term.sendline("module add " +  python_env.module_add)
                term.expect(".*module add " +  python_env.module_add + "\r\n")
                if len(term.before)>0:
                    logging.warning("Ssh message (Add module): " + str(term.before, 'utf-8').strip()) 
    
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
                logging.warning("Ssh message (scl enable): " + str(term.before, 'utf-8').strip()) 
        if libs_env.mpi_module_add is not None:
            term.sendline("module add " +  libs_env.mpi_module_add)
            term.expect(".*module add " + libs_env.mpi_module_add + "\r\n")
            if len(term.before)>0:
                logging.warning("Ssh message (Add module): " + str(term.before, 'utf-8').strip()) 

    def get_prepare_pbs_env(self):
        """Get array of commads for loading environment for pbs"""
        res=[]
        if self.python_env.scl_enable_exec is not None:
            res.append("scl enable " + self.python_env.scl_enable_exec + " bash")
        if self.python_env.module_add is not None:
            res.append("module add" + self.python_env.module_add)
        if self.libs_env.start_job_libs:
            if self.libs_env.mpi_scl_enable_exec is not None:
                res.append("scl enable" + self.libs_env.mpi_scl_enable_exec +" bash")
            if self.libs_env.mpi_module_add is not None:
                res.append("module add" + self.libs_env.mpi_module_add)  
        return res        

    @classmethod
    def install_job_libs_static(cls, mj_name, python_env, libs_env):
        """Return dir for savings status"""
        if sys.platform == "win32":
            #ToDo if is needed
            pass
        else:
            import pexpect
            
            term = pexpect.spawn('bash')
            cls.prepare_python_env_static(term, python_env)
            cls.prepare_mpi_env_static(term, libs_env)
            term.sendline('cd twoparty/install')            
            term.expect('.*cd twoparty/install.*')
            log_file= os.path.join(cls.get_result_dir_static(mj_name), "log")
            log_file= os.path.join(log_file, "install_job_libs.log")
            if libs_env.libs_mpicc is None:
                command = "./install_mpi4.sh " + python_env.python_exec + " &>> " + log_file
            else:
                command = "./install_mpi4.sh " + python_env.python_exec  + " " + libs_env.mpicc +  \
                                 " &>> " + log_file 
            logging.debug("Installation libraries started")
            term.sendline(command)
            time.sleep(1)
            try:
                term.expect('.*install.*') 
                term.expect('.*install.*', timeout=600)
            except pexpect.TIMEOUT:
                logging.warning("Installation libraries failed ( " +
                                          str(term.before, 'utf-8').strip()) 
            logging.debug("Installation libraries ended")
            term = term.sendline('exit')
 
 
