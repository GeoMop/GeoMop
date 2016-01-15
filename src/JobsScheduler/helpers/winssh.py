"""
Ssh wrapper for windows abova libssh c library and pyssh-types
"""
import time
import pyssh
import pyssh.exceptions as exc
import re

class Wssh():
    """Ssh wrapper for windows"""
    
    def __init__(self, host,  name,  password=''):
        self.host=host
        """ip or dns of host for communication"""
        self.name = name
        """login name for ssh connection"""
        self.password = password
        """password name for ssh connection"""
        self.ssh = None
        """Ssh subprocessed instance"""
        self.sftp = None
        """Sftp subprocessed instance"""
        self.sftp_local_path = ""
        """Sftp local path"""
        self.sftp_remote_path = ""
        """Sftp remote path"""
        self._buffer = ""
        self._prefix = ""
        self._prompt = False       
    
    def close(self):
        """Close ssh and sftp connection"""
        # add close action to pyssh-types library instead __exit__ method
        self.ssh = None
        self.sftp = None
        
    def connect(self):
        """connect session"""
        s = pyssh.new_session(hostname=self.host, username=self.name, password=self.password)
        self.ssh = s.create_shell()
        self.sftp = s.create_sftp()
        self._prefix = ""
        self._read_prefix()
        i=0        
        while len(self._prefix) == 0 and i < 10:
            self._read_prefix()
            i += 1
        self._clear()
        
    def set_sftp_paths(self, local, remote):
        self.sftp_local_path = local
        self.sftp_remote_path = remote

    def cd(self, dir):
        """ssh cd"""
        self.ssh.write("cd " + dir + "\n")
        self._read_prefix()
        if len(self._prefix) == 0:
            time.sleep(2)
            self._read_prefix()
        return self._read_filter("cd " + dir)
        
    def ls(self, path):
        """return list of files, directories"""
        f=[]
        d=[]
        self.ssh.write("ls -p -1 --color=never " + path + "\n")
        files = self._read_filter("ls -p -1 --color=never " + path)
        lines = files.splitlines(False)
        for line in lines:
            poz = line.find("/")
            if poz>-1:
                if poz>0:
                    d.append(line[:poz])
            else:
                f.append(line)
        return f, d
    
    def pwd(self):
        """ssh pwd"""
        self.ssh.write("pwd\n")        
        return self._read_filter("pwd")
        
    def rmdir(self, dir):
        """ssh rm"""
        self.ssh.write("rm -rf " + dir + "\n")        
        return self._read_filter("rm -rf " + dir)
    
    def mkdir(self, dir):
        """ssh cd"""
        self.ssh.write("mkdir " + dir + "\n")        
        return self._read_filter("mkdir " + dir)

    def put(self, file):
        """sftp put"""
        import os
        remote = self.sftp_remote_path + '/' + file
        local =  os.path.join(self.sftp_local_path, file)
        try:
            self.sftp.put(local, remote)
        except (RuntimeError, exc.ConnectionError) as err:
            return str(err)
        return ""

    def put_r(self, dir):
        """sftp put -r"""
        import os
        err = []
        res = self.mkdir(self.sftp_remote_path + '/' + dir) 
        if len(res) > 0:
            err.append(res)            
        for root, dirs, files in os.walk(os.path.join(self.sftp_local_path,  dir)):
            cdir = root
            resdir = None
            ndir = ""
            # prepare resource linux dir name
            while ndir != dir: 
                [cdir, ndir] = os.path.split(cdir)
                if resdir is None:
                    resdir = ndir
                else:
                    resdir = ndir + '/' + resdir
            resdir = self.sftp_remote_path + '/' + resdir
            # create dirs
            for name in dirs:
                linux_dir = resdir + '/' + name
                res = self.mkdir(linux_dir) 
                if len(res) > 0:
                    err.append(res)
            # copy files
            for name in files:
                remote =resdir + '/' +  name
                local = os.path.join(root, name)
                try:
                    self.sftp.put(local, remote)
                except (RuntimeError, exc.ConnectionError) as error:
                    err.append(str(error))
        if len(err) == 0:
            return ""
        return "\n".join(err)

    def get(self, remote, local):
        """
        sftp get
        
        :param str remote: relative remote file path
        :param str local: relative local file path
        """
        import os
        remote = self.sftp_remote_path + '/' + remote
        local =  os.path.join(self.sftp_local_path, local)
        try:
            self.sftp.get(remote, local)
        except (RuntimeError, exc.ConnectionError) as err:
            return str(err)
        return ""
        
    def _get_files(self, mask,  remote, local):
        """"
        Get all files in set directory
        
        :return: array of errors
        """
        import os
        errs = []
        if mask == "*":
            mask = ""
        if len(remote)>0:
            remote += '/'
        files,  dirs = self.ls(self.sftp_remote_path + '/' + remote + mask)       
        for file in files:
            err = self.get(remote + file, os.path.join(local, file))
            if err != '':
                errs.append(err)
        for dir in dirs:
            if len(local)>0:
                new_local =  os.path.join(local, dir)
            else:
                new_local = dir
            abs_new_local = os.path.join(self.sftp_local_path, new_local)
            if not os.path.isdir(abs_new_local):
                os.makedirs(abs_new_local)
            errs.extend(self._get_files('*', remote + dir, new_local))
        return errs
            

    def get_r(self, mask="*", remote_path="", local_path=""):
        """ 
        sftp get file recursivly
        
        :param str mask: mask for file or dir in remote_path folder
        :param str remote_path: relative remote file path
        :param str local_path: relative local file path
        """
        err = self._get_files(mask, remote_path, local_path)
        return "\n".join(err)         

    def exec_(self, command):
        """run async command"""
        self.ssh.write(command + "\n")        
        text = self._read_filter(command)
        self._clear()
        return text
        
    def exec_ret(self, command, quotes=""):
        """
        run async command, wait to finishing
        
        :return: result, err text
        """
        self.ssh.write(command + "\n")        
        text = self._read_filter(command)
        err = ""
        ret = ""
        while True:
            if  text != "":                
                if len(quotes)==0:
                    if self._prompt:
                        ret = text
                    else:    
                        if err != "":
                            err += '\n'
                        err += text
                else:
                    prefix = re.search( quotes+'(.*)'+quotes, text)
                    if prefix is not None:
                        ret = prefix.group(1)
                    if prefix is None or text != ret.strip():
                        # not quates or more than expected
                        if err != "":
                            err += '\n'
                        err += text                    
            if self._prompt:
                break
        self._clear()
        return ret, err

    def write(self, text):
        """write text to stdin"""
        self.ssh.write(text + "\n")

    def read(self, timeout, echo=None):
        """read text from stdout"""
        len_buffer = len(self._buffer)
        sec = time.time() + timeout
        text = self._read()
        while len_buffer == len(text) and sec < time.time():
            text += self._read()
        if echo is not None:
            dis = self._get_prefix_distance(echo, text)    
            if dis > 0:
                text = text[dis:]    
        return self._trim_message(text)

    def _clear(self):
        """read std in and drop it"""
        byte = b"p"
        while len(byte) > 0:
            byte = self.ssh.read(100)
        self._buffer = ""
        self._prompt = False

    def _read_filter(self, echo=None):
        """read text without echo and ssh terminal prefix from std in"""
        text = self._read()
        res = []
        # delete echo
        if echo is not None:
            dis = self._get_prefix_distance(echo, text)            
            if dis > 0:
                text = text[dis:]
                
        while len(text) > 0:
            prefix = True
            # delete empty chars and prefix
            while prefix is not None:
                prefix = re.match( '\s*(' + self._prefix + '\$\s*)', text)
                if prefix is None:
                    prefix = re.match( '\s*(' + self._prefix + '\x07\s*)', text)
                if prefix is not None:
                    text = text[len(prefix.group(1)):]
                    self._prompt = True
            # parse message
            line = re.match('(.*?)(\r\n\x1b]0;)', text)
            line2 = re.match( '(.*?)(\r\n)', text)
            if line is None or len(line.group(1))>len(line2.group(1)):
                line = line2
            if line is None:
                if len(text.strip()) > 0:
                    res.append(text.strip())
                text = ""
            else:
                if len(line.group(1)) > 0:
                    res.append(line.group(1))
                text = text[len(line.group(1))+len(line.group(2)):]
        if len(res) == 0:
            return ""
        return "\n".join(res)
        
    def _trim_message(self, text):
        """Remove spaces from the end of text"""
        line = re.match('(.*?)(\r\n\x1b]0;)$', text)
        if line is None:
            line = re.match( '(.*?)(\r\n)', text)
        if line is None:
            return text.strip()
        return line.group(1).strip()

    def _get_prefix_distance(self, prefix, text):
        """
        Try find the prefix in begin of the text
        
        :return: distance from begin of text or 0 if no prefix in the text
        """
        if len(prefix)>len(text):
            return 0
        dis=0
        for ch in prefix:
            if dis >= len(text):
                return 0
            if ch == text[dis]:
                dis += 1 
                continue
            dist_e = self._get_emptychars_distance(text[dis:])
            if dist_e > 0 and ch == text[dis+dist_e]:
                dis += 1 + dist_e  
                continue
            return 0            
        dis += self._get_emptychars_distance(text[dis:])
        return dis
        
    def _get_emptychars_distance(self, text):
        """
        Try find the empty chars sequence in begin of the text
        
        :return: distance from begin of text or 0 if no empty chars in text
        """
        dis=0
        while dis<len(text):
            if text[dis]  == '\r' and len(text) > (dis+5) and \
                '\n\x1b]0;' == text[dis+1:dis+6]:
                dis += 6
                continue
            if text[dis]  == '\r' and len(text) > (dis+1) and \
                '\n' == text[dis+1]:
                dis += 2
                continue
            if text[dis]  == ' ' and len(text) > (dis+1) and \
                '\r' == text[dis+1]:
                dis += 2
                continue
            if text[dis]  == '\x07': 
                continue
            break
        return dis

    def _read(self):
        """read std in"""
        text = self._buffer
        self._buffer = ""
        text_hlp = ""
        i = 0
        while i<3:
            text_hlp = self.ssh.read(100).decode("utf8")
            if(len(text_hlp)>0):
                text += text_hlp
                i = 0
            else:
                i += 1
                time.sleep(1)
        return text

    def _read_prefix(self):
        """filter std in"""
        text = self._read()
        self._buffer += text
        prefix = re.search( '(' + self.name + '@\S*:)\s*(~[^@:]*)\$', text)
        if prefix is not None:
            self._prefix = prefix.group(1) + '\s*' + prefix.group(2)
        else:
            self._prefix = ""
