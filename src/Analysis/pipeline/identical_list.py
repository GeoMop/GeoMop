import logging
import json
import os

logger = logging.getLogger("Analysis")

class IdenticalList():
    """Class for save status information between sessions"""
    def __init__(self, instance_dict={}):
        self._instance_dict = instance_dict
        """
        Instance names dictionary 
        next processing =>  previous processing
        """
        
    def get_old_iname(self, new_iname):
        """return old instance name from IdenticalList or None"""
        if new_iname in self._instance_dict:
            return self._instance_dict[new_iname]
        return None
    
    def load(self, file):
        """Try load IdenticalList from file"""
        self._instance_dict = {}
        if not os.path.isfile(file):
            return False
        try:
            fd = open(file, 'r') 
            self._instance_dict = json.load(fd)
            fd.close()
        except Exception as err:
            error = "Identical list loading error: {0}".format(err.str)
            logger.warning(error)
            fd.close()
            raise Exception(error)
        return True
        
    def save(self, file):
        """save Identical list"""
        try:
            fd = open(file, 'w')            
            json.dump(self._instance_dict, fd, indent=4, sort_keys=True)
            fd.close()
        except Exception as err:
            error = "Identical list saving error: {0}".format(err.str)
            logger.warning(error)
            fd.close()
            raise Exception(error)
