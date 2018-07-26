import sys
import os
import re
import shutil
import logging
import copy
import subprocess
import uuid
import time


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
__input_dir__ = "mj_input"
__an_subdir__ = "mj"
__result_dir__ = "res"
__status_dir__ = "status"
__lib_dir__ = "ins-lib"


class PathsConfig(object):
    """
    Class for configuration data, config, logs and locks paths

    self.app_dir variable is for renaming app directory created in remote.
    Other path is for communicators running on client pc. For communicators
    on remote pc (after first SSH connection) should be empty. First
    communicator before SSH should have self.copy_ex_libs set.
    """

    def __init__(self):
        """init"""
        self.app_dir = "js_services"
        """Name of application directory for remote"""
        self.home_dir = None
        """Absolut path to directory for central-log, locks and versions subdirectories.
        If variable is None, app directory is use"""
        self.work_dir = None
        """Absolut path to directory for result subdirectory.
        If variable is None, app directory/jobs/'JOB_NAME' path is use"""
        self.ex_lib_path = None
        """if absolute paths is set, is added to communicatin sys.path, if
        is None, path to lib directory is added"""
        self.copy_ex_libs = []
        """
        This variable contain relative directories with client system sepparators
        from self.ex_lib_path. (if self.ex_lib_path is None, variable is ignored) This
        directories is copy to lib directory on remote.
        """


class Installation:
    """
    Class representing and manipulating with a GeoMop (backend) instalation.
    We assume this installation is on remote hosts, which are assumed to run linux.

    JB, TODO:
    - Overview of functionalities the class cares of.
    - Why all splitting for linux and win case? The work to be done on remote is same, so just make
      unified interface to whatever ssh library is in use.
    - Do we want to support Windows remote hosts in future? Then make system specific layer
      to perform necessary basic operations as change dir, mkdir, delete, run python script, ...
    """
    python_env = None
    """python running envirounment"""
    libs_env = None
    """libraries running envirounment"""
    paths_config = None
    """paths for running envirounment"""
    
    """Files with installation (python files and configuration files) is selected 
        and send to set folder"""

    @classmethod
    def set_init_paths(cls, home, workspace):
        """Set install specific settings, call it firs, before other installation function"""
        if cls.paths_config is None:
            cls.paths_config = PathsConfig()
        cls.paths_config.home_dir = home
        cls.paths_config.work_dir = workspace

    @classmethod
    def get_central_log_dir_static(cls):
        """Return dir for central log"""
        try:
            home = __install_dir__
            if cls.paths_config is not None and \
                cls.paths_config.home_dir is not None:
                home = os.path.join(cls.paths_config.home_dir)
            path = os.path.join(home,  "log")
            if not os.path.isdir(path):
                os.makedirs(path)
        except Exception as err:
            logger.warning("Get central log dir error: " + str(err))
            return "."
        return path

    @classmethod
    def get_result_dir_static(cls, mj_name, an_name):
        """Return dir for savings results"""
        try:
            if cls.paths_config is not None and \
                cls.paths_config.work_dir is not None:
                path = cls.paths_config.work_dir
            else:
                path = os.path.join(__install_dir__, __jobs_dir__)            
            if not os.path.isdir(path):
                os.makedirs(path)
            path = os.path.join( path, an_name)
            if not os.path.isdir(path):
                os.makedirs(path)
            path = os.path.join( path, __an_subdir__)            
            if not os.path.isdir(path):
                os.makedirs(path)                
            path = os.path.join( path, mj_name)
            if not os.path.isdir(path):
                os.makedirs(path)
            path = os.path.join(path, __result_dir__)
            if not os.path.isdir(path):
                os.makedirs(path)
        except Exception as err:
            logger.warning("Get mj result dir error: " + str(err))
            return "."
        return path
        
    @classmethod
    def get_config_dir_static(cls, mj_name, an_name):
        """Return dir for configuration"""
        try:
            if cls.paths_config is not None and \
                cls.paths_config.work_dir is not None:
                path = cls.paths_config.work_dir
            else:
                path = os.path.join(__install_dir__, __jobs_dir__)            
            if not os.path.isdir(path):
                os.makedirs(path)
            path = os.path.join( path, an_name)
            if not os.path.isdir(path):
                os.makedirs(path)
            path = os.path.join( path, __an_subdir__)            
            if not os.path.isdir(path):
                os.makedirs(path)                
            path = os.path.join( path, mj_name)
            if not os.path.isdir(path):
                os.makedirs(path)
            path = os.path.join(path,__conf_dir__)
            if not os.path.isdir(path):
                os.makedirs(path)
        except Exception as err:
            logger.warning("Get mj configuration dir error: " + str(err))
            return "."
        return path

    @classmethod
    def get_input_dir_static(cls, mj_name, an_name):
        """Return dir for inputuration"""
        try:
            if cls.paths_config is not None and \
                cls.paths_config.work_dir is not None:
                path = cls.paths_config.work_dir
            else:
                path = os.path.join(__install_dir__, __jobs_dir__)            
            if not os.path.isdir(path):
                os.makedirs(path)
            path = os.path.join( path, an_name)
            if not os.path.isdir(path):
                os.makedirs(path)
            path = os.path.join( path, __an_subdir__)            
            if not os.path.isdir(path):
                os.makedirs(path)                
            path = os.path.join( path, mj_name)
            if not os.path.isdir(path):
                os.makedirs(path)
            path = os.path.join(path,__input_dir__)
            if not os.path.isdir(path):
                os.makedirs(path)
        except Exception as err:
            logger.warning("Get mj input dir error: " + str(err))
            return "."
        return path

    @classmethod
    def get_mj_data_dir_static(cls, mj_name, an_name):
        """Return dir for savings results"""
        try:
            if cls.paths_config is not None and \
                cls.paths_config.work_dir is not None:
                path = cls.paths_config.work_dir
            else:
                path = os.path.join(__install_dir__, __jobs_dir__)            
            if not os.path.isdir(path):
                os.makedirs(path)
            path = os.path.join( path, an_name)
            if not os.path.isdir(path):
                os.makedirs(path)
            path = os.path.join( path, __an_subdir__)            
            if not os.path.isdir(path):
                os.makedirs(path)                
            path = os.path.join( path, mj_name)
            if not os.path.isdir(path):
                os.makedirs(path)
        except Exception as err:
            logger.warning("Get mj data dir error: " + str(err))
            return "."
        return path 

    @classmethod
    def get_mj_log_dir_static(cls, mj_name, an_name):
        """Return dir for logging"""
        try:
            if cls.paths_config is not None and \
                cls.paths_config.work_dir is not None:
                path = cls.paths_config.work_dir
            else:
                path = os.path.join(__install_dir__, __jobs_dir__)            
            if not os.path.isdir(path):
                os.makedirs(path)
            path = os.path.join( path, an_name)
            if not os.path.isdir(path):
                os.makedirs(path)
            path = os.path.join( path, __an_subdir__)            
            if not os.path.isdir(path):
                os.makedirs(path)
            path = os.path.join( path, mj_name)
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

    @classmethod
    def get_status_dir_static(cls, mj_name, an_name):
        """Return dir for savings status"""
        try:
            if cls.paths_config is not None and \
                cls.paths_config.work_dir is not None:
                path = cls.paths_config.work_dir
            else:
                path = os.path.join(__install_dir__, __jobs_dir__)            
            if not os.path.isdir(path):
                os.makedirs(path)
            path = os.path.join( path, an_name)
            if not os.path.isdir(path):
                os.makedirs(path)
            path = os.path.join( path, __an_subdir__)            
            if not os.path.isdir(path):
                os.makedirs(path)
            path = os.path.join( path, mj_name)
            if not os.path.isdir(path):
                os.makedirs(path)
            path = os.path.join(path,__status_dir__ )
            if not os.path.isdir(path):
                os.makedirs(path)
        except Exception as err:
            logger.warning("Get mj status dir error: " + str(err))
            return None
        return path 
