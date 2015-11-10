import logging
import json
import os

class CommunicatorStatus():
    """Class for save status information between sessions"""
    def __init__(self, path, name):
        self.path = path
        """Communicator status saving path"""
        self.name = name
        """Communicator name"""
        self.next_installed = False
        """if is next communicator installed"""
        self.interupted = False
        """if is communicator interupted"""
        self.next_started = False
        """if is next communicator starteded"""
    
    def load(self):
        """Try load status, and return if is found status file (communicator was initialized)"""
        if self.path is None:
            return False
        if not os.path.isdir(self.path):
            return False
        file =  os.path.join(self.path, self.name + ".json" )
        if not os.path.isfile(file):
            return False
        try:
            fd = open(file, 'r') 
            data = json.load(fd)
            fd.close()
        except Exception as err:
            logging.warning("Status loading error: %s", err.str)
            fd.close()
            return False
            
        self.__dict__ = data
        logging.debug("Status loaded from %s", file)        
        return True
        
    def save(self):
        """save comminicator data"""
        if self.path is None:
            return False
        if not os.path.isdir(self.path):
            return False
        file =  os.path.join(self.path, self.name + ".json" )
        data = dict(self.__dict__)
        try:
            fd = open(file, 'w')            
            json.dump(data, fd, indent=4, sort_keys=True)
            fd.close()
        except Exception as err:
            logging.warning("Status saveing error: %s", err.str)
            fd.close()
            return False
        logging.debug("Status saved to  %s", file)
        return True
