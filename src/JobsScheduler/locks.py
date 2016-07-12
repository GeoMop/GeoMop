import os
import shutil
import time

__lock_dir__ = "lock"
__version_dir__ = "versions"


class Lock():
    """
    Class for locking application.
    Implemment:
        - One global file lock for all installation directory, that make 
          possibility for save lock change during next actions processing.
          file: app.lock
        - Multi job application lock for running multiJob instance
          file: %lock_name%_app.lock
        - Installation lock for save installing set version of installation
          files: install.lock, __version_dir__/install.version
        - Data version for save copiing and deleting data accoding set
          version (jobs session). For opperation is used app.lock
          file: __version_dir__/%lock_name%_data.version
        - Library lock for save installing set library version
          files: lib.lock
    """
    __data__ = 1
    __app__ = 2
    __nothing__ = 0
    
    def __init__(self, lock_name, path, home_dir=None):
        """init"""
        self._lock_name = lock_name
        """Multijob name for unique jobs identification"""
        self._js_path = path
        if not os.path.isdir(path):
            os.makedirs(path)
        """Path to js directory"""        
        self._lock_dir = os.path.join(path, __lock_dir__)
        if home_dir is not None:
            self._lock_dir = os.path.join(home_dir, __lock_dir__)
        """Path to lock application directory"""
        if not os.path.isdir(self._lock_dir):
            os.makedirs(self._lock_dir)
        self._version_dir = os.path.join(path, __version_dir__) 
        if home_dir is not None:
            self._version_dir = os.path.join(home_dir, __version_dir__)
        """Path to version files"""
        
    def lock_app(self,  install_ver, data_ver, res_dir, conf_subdir):
        """
        Check if application with lock_name is not runnig
        and is installed right version of installation.
        
          - If other app with same name is running throw exception
          - If installation lock is set, wait for lock 300 second and if 
            another installation is not finished throw exception
          - If version of installation is different and other *_app.lock 
            is locked throw exception            
          - If version of installation is different and any *_app.lock 
            is not locked, install.lock is set and all js directory is 
            removed. Unlock install must be called after installation
          - If data version is diferent, remove multijob data dir
        return bite add of contant:
            - __data__ = 1
            - __app__ = 2
            - __nothing__ = 0
        """
        res = Lock.__nothing__
        if self._lock_file("app.lock"):
            if not self._lock_file(self._lock_name + "_app.lock", 0):
                self._unlock_file("app.lock")
                raise LockFileError("MuliJob application (" + self._lock_name + ") is running.")
            # first instance locked
            if not self._lock_file("install.lock", 0):
                self._unlock_file("app.lock")
                if not self._lock_file("install.lock", 300):
                    self._unlock_file(self._lock_name + "_app.lock")
                    raise LockFileError(" application (" + self._lock_name + ") is running.")                
                if not self._lock_file("app.lock"):
                    self._unlock_file(self._lock_name + "_app.lock")
                    self._unlock_file("install.lock")
                    raise LockFileError("Global lock can't be set.")
            installed_ver = self._read_version("install.version") 

            source = True
            if not os.path.isdir(os.path.join(self._js_path)):
                source = False
        
            if (installed_ver is None or installed_ver !=  install_ver) and \
                not source :
                if self._is_mj_lock_set(self._lock_name + "_app.lock"):                    
                    self._unlock_file(self._lock_name + "_app.lock")
                    self._unlock_file("install.lock")
                    self._unlock_file("app.lock")                    
                    raise LockFileError("New version can't be installed, old application is running.")
                #delete app dir
                names = os.listdir( self._js_path)
                for name in names:
                    path = os.path.join(self._js_path,name)
                    if os.path.isdir(path) and name != __lock_dir__:
                        shutil.rmtree(path, ignore_errors=True)
                    if os.path.isfile(path) and name != "locks.py":
                        os.remove(path)
                self._write_version("install.version", install_ver )
                res |= Lock.__app__
            else:
                self._write_version("install.version", install_ver, False)
                self._unlock_file("install.lock")
               
            # installation ready
            dataed_ver = self._read_version(self._lock_name + "_data.version")
            if dataed_ver is None or dataed_ver != data_ver:
                job_dir = os.path.split(res_dir)[0]
                if not source and os.path.isdir(job_dir):
                    names = os.listdir(job_dir)
                    for name in names:
                        path = os.path.join(job_dir,name)
                        if os.path.isdir(path):
                            if name != conf_subdir or not source:
                                shutil.rmtree(path, ignore_errors=True) 
                        if os.path.isfile(path) and name != "locks.py":
                            os.remove(path)
                self._write_version(self._lock_name + "_data.version", data_ver)   
                res |= Lock.__data__
            # data_ready            
        else:
            raise LockFileError("Global lock can't be set.")
        self._unlock_file("app.lock")
        return res
            
    def unlock_app(self):
        """Application with lock_name is stopping"""
        self._lock_file("app.lock")
        self._unlock_file(self._lock_name + "_app.lock")
        self._unlock_file("app.lock")                           
        
    def unlock_install(self):
        """Installation is finished"""
        self._lock_file("app.lock")
        self._unlock_file("install.lock")
        self._unlock_file("app.lock")                           
        
    def lock_lib(self, lib_dir):
        """
        Check if library lock is empty. If is, lib lock is set.
        
        return True if lib lock is set
        """
        res = True
        if self._lock_file("app.lock"):
            if self._lock_file("lib.lock", 300):
                if os.path.isdir(lib_dir):
                    names = os.listdir(lib_dir)
                    if len(names) > 0:
                        self._unlock_file("lib.lock")
                        res = False                
            else:                
                self._unlock_file("app.lock") 
                raise LockFileError("Library lock can't be set.")
        else:
            raise LockFileError("Global lock can't be set.")
        self._unlock_file("app.lock")
        return res 
        
    def unlock_lib(self):
        """Library is installed"""
        self._lock_file("app.lock")
        self._unlock_file("lib.lock")
        self._unlock_file("app.lock") 
 
    def _lock_file(self, file, timeout=120):
        """
        lock set file lock
        
        retun: True if lock is locked
        """
        sec = time.time() + timeout
        path = os.path.join(self._lock_dir, file)
        first = True
        while first or sec > time.time():
            first = False
            try:
                fd = os.open(path, os.O_CREAT|os.O_EXCL)
                os.close(fd)
                return True
            except OSError:
                if timeout > 0.1 :
                    if timeout <= 1:
                        time.sleep(timeout/2)
                    else:
                        time.sleep(1)
            except:
                return False
        return False
            
    def _unlock_file(self, file):
        """lock global lock"""
        path = os.path.join(self._lock_dir, file)
        try:
            os.remove(path)
        except:
            pass

    def _is_mj_lock_set(self, lock_name):
        """return True if any multijob lock difrent from actual is set"""
        names = os.listdir(self._lock_dir)
        for name in names:
            if len(name)>9 and name[-9:] == "_app.lock" and \
                name != lock_name:
                return True
        return False
        
    def _read_version(self, file):
        """Return version string or None if file is not exist"""
        path = os.path.join(self._version_dir, file)
        version = None
        try:
            with open(path, 'r') as f:
                version = f.readline()
        except:
            return None
        return version
        
    def _write_version(self, file,  version, rewrite=True):
        """Return version string or None if file is not exist"""
        path = os.path.join(self._version_dir, file)
        if not os.path.isdir(self._version_dir):
            os.makedirs(self._version_dir)
        else:
            if os.path.isfile(path) and not rewrite:
                return True
        try:
            with open(path, 'w') as f:
                f.write(version)
        except:
            return False
        return True
        
class LockFileError(Exception):
    """Represents an error in lock file class"""

    def __init__(self, msg):
        super(LockFileError, self).__init__(msg)
        
if __name__ == "__main__":
    """
    calling:
        locks.py lock_name path install_ver data_ver res_path conf_path locking
            - lock_name - multijob name
            - path - path to installation directory
            - install_ver - installation version 
            - data_ver - data version (id of started session) 
            - res_path - path to result directory
            - conf_path - path to confih directory
            - locking - Y/N do locking
    """
    import sys
    
    if len(sys.argv) == 2 and sys.argv[1] == "test":
        print("ok")
        sys.exit(0)
    
    if len(sys.argv) != 8:
        raise Exception('Lock application seven parameters require')
    lock_name = sys.argv[1]
    path = sys.argv[2]
    install_ver = sys.argv[3]
    data_ver = sys.argv[4]
    res_path = sys.argv[5]
    conf_path = sys.argv[6]
    locking = sys.argv[7]
        
    lock = Lock(lock_name, path)
    if locking == "N":
        lock.unlock_install()
        print("--0--")
        sys.exit(0)
    try:
        res = lock.lock_app(install_ver, data_ver, res_path, conf_path)
    except LockFileError as err:
        print("Lock instalation error: " + str(err))
        print("---1--")
        sys.exit(2)
    print("--" + str(res) + "--")
    sys.exit(0)
