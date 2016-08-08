import uuid
import hashlib
import getpass
import pickle
import os
from helpers.pyDes import triple_des as _trim, PAD_PKCS5

class Users():
    def __init__(self, name, dir, home_dir, to_pc, to_remote):
        self.name = name
        self.to_pc = to_pc
        self.to_remote = to_remote
        self.dir = dir
        self.home = home_dir
        
    def get_login(self, pwd, key1, key2, is_remote):
        if is_remote:
            if self.to_pc and self.to_remote:
                file = os.path.join(self.dir, ".reg")
                with open(file, 'rb') as f:
                    reg = pickle.load(f)
                os.remove(file)
                m = hashlib.md5()
                m.update(str.encode(key1))
                m.update(str.encode(reg))
                m.update(str.encode(key2))
                code = m.digest()
                tr = _trim(code)
                text = tr.decrypt(str.encode(pwd, 'utf-8'), padmode=PAD_PKCS5)         
                return str(text, 'utf-8')
        else:
            if not self.to_pc:
                name = key2
            else:
                name = self.name
            code = self.get_reg(name, key1, self.home)
            from ui.data.reg import Regs        
            regs = Regs(self.home)
            if not self.to_pc:
                regs.del_id(id)
            return code
        return None       

    def get_preset_pwd1(self, key, is_remote, long):
        if is_remote:
            if self.to_remote:
                from ui.data.reg import Regs
        
                regs = Regs(self.home)
                reg, text = regs. get_id(self.name)
                u = getpass.getuser()
                m = hashlib.md5()                
                m.update(str.encode(key))
                m.update(str.encode(reg))
                m.update(str.encode(u))
                code = m.digest()
                tr = _trim(code)
                code = tr.decrypt(text, padmode=PAD_PKCS5)
                file = os.path.join(self.dir, ".reg")
                with open(file, 'wb') as f:
                    pickle.dump(reg, f)
                key = str(uuid.uuid4())
                m = hashlib.md5()
                m.update(str.encode(key))
                m.update(str.encode(reg))
                m.update(str.encode(long))
                code = tr.encrypt(code, padmode=PAD_PKCS5) 
                return code, key
            else:
                return None, ""
        key = str(uuid.uuid4())
        code = key
        return key[:7], key[7:] 
        
    @classmethod    
    def get_preset_pwd2(cls, home, pwd, key, long):
        code = cls.save_reg(long, pwd, home, key)
        key = str(uuid.uuid4()) 
        return key[:7], code
     
    @staticmethod
    def save_reg(id, text, home, key=None):
        from ui.data.reg import Regs
        if key is None:
            key = str(uuid.uuid4())
        reg = str(uuid.uuid4())
        u = getpass.getuser()
        m = hashlib.md5()
        m.update(str.encode(key))
        m.update(str.encode(reg))
        m.update(str.encode(u))
        code = m.digest()
        regs = Regs(home)
        tr = _trim(code)
        code = tr.encrypt(str.encode(text, 'utf-8'), padmode=PAD_PKCS5) 
        regs.set_id(reg, id, code)
        return key
        
    @staticmethod    
    def get_reg(id, key, home):
        from ui.data.reg import Regs
        
        regs = Regs(home)
        reg, text = regs. get_id(id)        
        u = getpass.getuser()
        m = hashlib.md5()
        m.update(str.encode(key))
        m.update(str.encode(reg))
        m.update(str.encode(u))
        code = m.digest()
        tr = _trim(code)
        text = tr.decrypt(text, padmode=PAD_PKCS5)         
        return str(text, 'utf-8')
