import os
import copy

from helpers.importer import DialectImporter


class Pbs():
    """
    Class for configuration qsub command
    """
    def __init__(self, mj_path, config):
        """init"""
        self.config = copy.deepcopy(config)
        """pbs configuration (:class:`data.communicator_conf.PbsConfig`) """
        self. mj_path = mj_path
        """folder name for multijob data"""
        
    def prepare_file(self, command, interpreter=None, load_commands=[], args=[]):
        """Open and construct shell file for pbs starting"""
        if not os.path.isdir(self.mj_path):
            os.makedirs(self.mj_path)
        if not os.path.isdir(self.mj_path + "/" + self.config.name):
            os.makedirs(self.mj_path + "/" + self.config.name)
        f = open(self.mj_path + "/" + self.config.name  + "/com.qsub", 'w')
        
        f.write ('#!/bin/bash\n')
        f.write ('#\n')
        
        if self.config.dialect:
            imp = DialectImporter.get_dialect_by_name(self.config.dialect)
            dirs = imp.PbsDialect.get_pbs_directives(self.mj_path, self.config)
            for dl in dirs:
                f.write(dl + '\n')
        else:
            f.write ('#$ -cwd\n')
            f.write ('#$ -S /bin/bash\n')
            f.write ('#$ -terse\n')
            f.write ('#$ -o ' + self.mj_path + "/" + self.config.name + '/pbs_output\n')
            f.write ('#$ -e ' + self.mj_path + "/" + self.config.name + '/pbs_error\n')
        f.write ('#\n')
        f.write ('\n')
        for line in self.config.pbs_params:
            f.write(line + '\n')
        for com in  load_commands:
            f.write(com + '\n')
        if len(load_commands)>0:
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
        """Get arguments for qsub function"""
        if self.config.dialect:
            imp = DialectImporter.get_dialect_by_name(self.config.dialect)
            args = imp.PbsDialect.get_qsub_args()
            args.insert(0, "qsub")
            args.append(self.mj_path + "/" + self.config.name + "/com.qsub")
            return args
        return ["qsub", "-pe", "orte", "1", self.mj_path + "/" + self.config.name + "/com.qsub"]
        
    def get_outpup(self):
        """Get pbs output file contens"""
        if self.config.dialect:
            imp = DialectImporter.get_dialect_by_name(self.config.dialect)
            file = imp.PbsDialect.get_outpup_file()
        if file is None:
            file = self.mj_path + "/" + self.config.name + "/pbs_output"
        if  os.path.isfile(file):
            f = open(file, 'r')
            lines = f.read().splitlines(False)
            f.close()
            if len(lines) == 0 or (len(lines) == 1 and \
                lines[0].isspace() or len(lines[0]) == 0):
                return None
            return lines
        return None
    
    def get_errors(self):
        """Get pbs error file contens"""
        if  os.path.isfile(self.mj_path + "/" + self.config.name + "/pbs_error"):
            f = open(self.mj_path + "/" + self.config.name + "/pbs_error", 'r')
            error = f.read()
            f.close()
            if error.isspace() or len(error) == 0:
                return None
            return error
        return None        
