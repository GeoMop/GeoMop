import os

class Pbs():
    """
    Class for configuration qsub command
    """
    def __init__(self, config):
        """init"""
        self.config = config
        """pbs configuration (:class:`data.communicator_conf.PbsConfig`) """
        
    def prepare_file(self, command, interpreter=None, args=[]):
        """Open and construct shell file for pbs starting"""
        if not os.path.isdir(self.config.name):
            os.makedirs(self.config.name)
        
        f = open(self.config.name  + "/com.qsub", 'w')
        f.write ('#!/bin/bash\n')
        f.write ('#\n')
        f.write ('#$ -cwd')
        f.write ('#$ -j y\n')
        f.write ('#$ -S /bin/bash\n')
        f.write ('#$ -terse\n')
        f.write ('#$ -o ' + self.config.name + '/pbs_output\n')
        f.write ('#$ -e ' + self.config.name + '/pbs_error\n')
        f.write ('#\n')
        f.write ('\n')
        line = ""
        if interpreter is not None:
            line = interpreter + ' ' + command
        else:
            line = command
        for arg in args:
            line += " "+arg
        line += '\n'        
        f.write (line + '\n')
        f.close()
        
    def get_qsub_args(self):
        return ["qsub", "-pe", "orte", "1", self.config.name + "/com.qsub"]
        
    def get_outpup(self):
        if  os.path.isfile(self.config.name + "/pbs_output"):
            f = open(self.config.name + "/pbs_output", 'r')
            lines = f.read().splitlines(False)
            f.close()
            return lines
        return None
    
    def get_errors(self):
        if  os.path.isfile(self.config.name + "/pbs_error"):
            f = open(self.config.name + "/pbs_error", 'r')
            error = f.read()
            f.close()
            return error
        return None        
