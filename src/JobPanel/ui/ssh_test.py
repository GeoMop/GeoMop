import threading
from ui.helpers.ssh.tests import Tests
class SshTester(threading.Thread):   
    """
    Class created own thread for for testing.
    """
    def __init__(self, preset, data):            
        super().__init__(name="ssh_test")
        self._preset = preset
        """new ssh preset"""
        self._data = data
        """Data container with others presets"""
        self.__massage_lock = threading.Lock()
        """lock for erros and logs"""
        self.__logs = []
        """testing log messages"""
        self.__errors = []
        """testing error messages"""
        self.__finished = False
        """testing is ended""" 
        self.__tests_lib = Tests(preset)
        """Test library"""
        self.__stop = False
        """Test library"""
        self.__remove_dirs = False
        """try remove dir during finishing"""
    
    def start(self):
        """start testing"""
        super(SshTester, self).start() 

    def stop(self):
        """stop testing"""
        self.__stop = True
    
    def get_next_error(self):
        """return next error message"""
        self.__massage_lock.acquire()
        if len(self.__errors)==0:
            error = None
        else:
            error = self.__errors.pop(0)
        self.__massage_lock.release()
        return error
        
    def get_next_log(self):
        """return next log message"""
        self.__massage_lock.acquire()
        if len(self.__logs)==0:
            log = None
        else:
            log = self.__logs.pop(0)
        self.__massage_lock.release()
        return log

    def finished(self):
        """return if main thread is finished"""
        self.__massage_lock.acquire()
        finished = self.__finished
        self.__massage_lock.release()
        return finished
        
    def run(self):
        """testing"""
        env = self._preset.env
        if env is None or env not in self._data.env_presets:
            self.__massage_lock.acquire()
            self.__errors.append("Incorect environment name {0} in ssh settings", env)
            self.__finished = True
            self.__massage_lock.release()
            return
        else:
            env = self._data.env_presets[env]
            
        if self.__stop or not self._test(self.__tests_lib.open_connection):
            return self._finish() 
        self.__remove_dirs = True
        if self.__stop or not self._test(self.__tests_lib.create_dir_struc):
            return self._finish()        
        if self.__stop or not self._test(self.__tests_lib.open_sftp):
            return self._finish()
        if self.__stop or not self._test(self.__tests_lib.upload_file):
            return self._finish()
        if self.__stop or not self._test(self.__tests_lib.upload_dir):
            return self._finish()
        self._test(self.__tests_lib.test_python, env)
        self._test(self.__tests_lib.run_python, env)
        self._test(self.__tests_lib.download_file)
        self._test(self.__tests_lib.download_dir)
        self._test(self.__tests_lib.test_flow123d, env)
        if self._preset.pbs_system is not None and len(self._preset.pbs_system)>0:
            self._test(self.__tests_lib.test_pbs)
        self._finish()
        
    def _finish(self):
        if self.__remove_dirs:
            self._test(self.__tests_lib.remove_dir)
        if self.__tests_lib.conn is not None and self.__tests_lib.conn.conn is not None:
            self._test(self.__tests_lib.close_connection)
        if self.__tests_lib.conn is not None and self.__tests_lib.conn.sftp is not None:
            self._test(self.__tests_lib.close_sftp)
        self.__massage_lock.acquire()
        self.__logs.append("SSH conection test is finished ...")
        self.__finished = True
        self.__massage_lock.release()
        
    def _test(self, func, *args):
        """Call set test"""
        mess = func(True, *args)
        self.__massage_lock.acquire()
        self.__logs.append(mess)
        self.__massage_lock.release()
        try:
            (logs, errs) = func(False, *args)
        except Exception as err:
            logs = ["Something is wrong !!!"]
            errs = [str(err)]
        res = len(errs) == 0
        self.__massage_lock.acquire()
        self.__logs.extend(logs)
        self.__errors.extend(errs)
        self.__massage_lock.release()
        return res
        
        
