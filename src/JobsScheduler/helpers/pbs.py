import os
import copy

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
        f.write ('#$ -cwd\n')
        f.write ('#$ -S /bin/bash\n')
        f.write ('#$ -terse\n')
        f.write ('#$ -o ' + self.mj_path + "/" + self.config.name + '/pbs_output\n')
        f.write ('#$ -e ' + self.mj_path + "/" + self.config.name + '/pbs_error\n')
        f.write ('#\n')
        f.write ('\n')
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

    def _get_pbs_directives(self):
        """
        Generates file directives for specific PBS system.
        :return: List of PBS directives.
        """
        directives = list()
        directives.append("#$ -cwd")
        directives.append("#$ -S /bin/bash")
        directives.append("#$ -terse")
        directives.append("#$ -o " + self.mj_path + "/" +
                          self.config.name + "/pbs_output")
        directives.append("#$ -e " + self.mj_path + "/" +
                          self.config.name + "/pbs_error")

        # specify queue, i.e. all.q
        if self.config.queue:
            directives.append("#$ -q %s" % self.config.queue)

        # request a parallel environment, i.e. 'openmpi' using n slots (CPUs)
        if self.config.nodes and int(self.config.nodes) > 1:
            directives.append("#$ -pe %s %s" % ("openmpi", self.config.nodes))

        # -l resource=value, ...
        # ToDo opravit, nejasny syntax a pouzitelne direktivy
        resources = list()
        res_dir = "#$ -l "
        if self.config.walltime:
            pass
        if self.config.memory:
            resources.append("mem=" + self.config.memory[:-2])
        if self.config.scratch:
            resources.append("scratch=" + self.config.scratch[:-2])
        for res in resources:
            res_dir = res_dir + ", " + res

        directives.append(res_dir)
        return directives

    def get_qsub_args(self):
        return ["qsub", "-pe", "orte", "1", self.mj_path + "/" + self.config.name + "/com.qsub"]
        
    def get_outpup(self):
        if  os.path.isfile(self.mj_path + "/" + self.config.name + "/pbs_output"):
            f = open(self.mj_path + "/" + self.config.name + "/pbs_output", 'r')
            lines = f.read().splitlines(False)
            f.close()
            if len(lines) == 0 or (len(lines) == 1 and \
                lines[0].isspace() or len(lines[0]) == 0):
                return None
            return lines
        return None
    
    def get_errors(self):
        if  os.path.isfile(self.mj_path + "/" + self.config.name + "/pbs_error"):
            f = open(self.mj_path + "/" + self.config.name + "/pbs_error", 'r')
            error = f.read()
            f.close()
            if error.isspace() or len(error) == 0:
                return None
            return error
        return None        
