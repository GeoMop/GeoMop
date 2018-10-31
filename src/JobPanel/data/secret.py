import os
import pyDes
import uuid
import stat
import binascii
import hashlib

from gm_base import config


class Secret:
    """
    Class for mangling and demangling secret data.
    """
    def __init__(self, key=None):
        self._key = ""
        if key is not None:
            self._key = key
        else:
            file = os.path.join(config.__config_dir__, ".secret")
            if os.path.isfile(file):
                with open(file, "r") as f:
                    self._key = f.readline().strip()
            else:
                self._key = str(uuid.uuid4())
                os.makedirs(config.__config_dir__, exist_ok=True)
                with open(file, "w") as f:
                    f.write(self._key)
                    f.write("\n")
                os.chmod(file, stat.S_IRUSR | stat.S_IWUSR)

    def get_key(self):
        return self._key

    def mangle(self, text):
        """
        Mangles secret data.
        :return:
        """
        if text == "":
            return ""

        m = hashlib.md5()
        m.update(self._key.encode())
        code = m.digest()
        k = pyDes.triple_des(code)
        bin = k.encrypt(text.encode(), padmode=pyDes.PAD_PKCS5)
        return str(binascii.b2a_base64(bin), "us-ascii").strip()

    def demangle(self, text):
        """
        Demangles secret data.
        :return:
        """
        if text == "":
            return ""

        m = hashlib.md5()
        m.update(self._key.encode())
        code = m.digest()
        k = pyDes.triple_des(code)
        bin = k.decrypt(binascii.a2b_base64(text), padmode=pyDes.PAD_PKCS5)
        return str(bin, "utf-8")
