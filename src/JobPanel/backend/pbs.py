from .json_data import JsonData, ClassFactory

import os


class PbsConfig(JsonData):
    """
    Class for configuration qsub command
    """

    def __init__(self, config={}):
        """init"""
        self.name = ""
        """name as unique job identifier for files"""
        self.dialect = ClassFactory([PbsDialectMetacentrum, PbsDialectPBSPro])
        self.queue = ""
        self.walltime = ""
        self.nodes = "1"
        self.ppn = "1"
        self.memory = ""
        self.scratch = ""
        #self.with_socket = False
        """
        Initialize communication over socket, True in case of MultiJob
        otherwise False.
        """
        self.pbs_params = []

        JsonData.__init__(self, config)


class Pbs():
    """
    Class for configuration qsub command
    """

    def __init__(self, mj_path, config):
        """init"""
        self.config = config
        """pbs configuration (:class:`data.communicator_conf.PbsConfig`) """
        self.mj_path = mj_path
        """folder name for multijob data"""

    def prepare_file(self, command, interpreter=None, load_commands=[], args=[], limit_args=[]):
        """Open and construct shell file for pbs starting"""
        if not os.path.isdir(self.mj_path):
            os.makedirs(self.mj_path)
        f = open(os.path.join(self.mj_path, "com.qsub"), 'w')

        f.write('#!/bin/bash\n')
        f.write('#\n')

        dirs = self.config.dialect.get_pbs_directives(self.mj_path, self.config)
        for dl in dirs:
            f.write(dl + '\n')
        f.write('#\n')
        f.write('\n')

        for line in self.config.pbs_params:
            f.write(line + '\n')
        if len(self.config.pbs_params) > 0:
            f.write('\n')
        for com in load_commands:
            f.write(com + '\n')
        if len(load_commands) > 0:
            f.write('\n')

        # work dir
        f.write('cd "{}"\n\n'.format(self.mj_path))

        line = ""
        for arg in limit_args:
            line += arg + " "
        if interpreter is not None:
            line += interpreter + ' ' + command
        else:
            line += command
        for arg in args:
            line += " " + arg
        line += '\n'
        f.write(line + '\n')
        f.close()

    def get_qsub_args(self):
        """Get arguments for qsub function"""
        args = self.config.dialect.get_qsub_args()
        args.insert(0, "qsub")
        args.append(os.path.join(self.mj_path, "com.qsub"))
        return args

    # def get_outpup(self):
    #     """Get pbs output file contens"""
    #     if self.config.dialect:
    #         imp = DialectImporter.get_dialect_by_name(self.config.dialect)
    #         file = imp.PbsDialect.get_outpup_file(self.mj_path + "/" + self.config.name)
    #     if file is None:
    #         file = self.mj_path + "/" + self.config.name + "/pbs_output"
    #     if os.path.isfile(file):
    #         f = open(file, 'r')
    #         lines = f.read().splitlines(False)
    #         f.close()
    #         if len(lines) == 0 or (len(lines) == 1 and \
    #                                        lines[0].isspace() or len(lines[0]) == 0):
    #             return None
    #         return lines
    #     return None
    #
    # def get_errors(self):
    #     """Get pbs error file contens"""
    #     if os.path.isfile(self.mj_path + "/" + self.config.name + "/pbs_error"):
    #         f = open(self.mj_path + "/" + self.config.name + "/pbs_error", 'r')
    #         error = f.read()
    #         f.close()
    #         if error.isspace() or len(error) == 0:
    #             return None
    #         return error
    #     return None


class PbsDialect(JsonData):
    def __init__(self, config={}):
        super().__init__(config)


class PbsDialectMetacentrum(PbsDialect):
    @staticmethod
    def get_pbs_directives(work_dir, pbs_config):
        """
        Generates file directives for specific PBS system.
        :param work_dir: Path to MJ, specifies output file.
        :param pbs_config: PbsConf object with data.
        :return: List of PBS directives.
        """
        directives = list()
        # ToDo fix cwd work around
        # http://www.uibk.ac.at/zid/systeme/hpc-systeme/common/tutorials/pbs-howto.html
        # directives.append("#PBS -cwd")
        directives.append("#PBS -S /bin/bash")
        # ToDo fix terse
        # There seems to be no option for that
        # http://docs.adaptivecomputing.com/torque/4-0-2/Content/topics/commands/qsub.htm#-t
        # directives.append("#PBS -terse")
        directives.append("#PBS -o " + os.path.join(work_dir, "pbs_output"))
        directives.append("#PBS -e " + os.path.join(work_dir, "pbs_error"))
        directives.append("#PBS -d " + work_dir)

        # PBS -N name
        if pbs_config.name != "":
            directives.append("#PBS -N %s" % pbs_config.name)

        # PBS -l nodes=1:ppn=1
        if pbs_config.nodes != "" and int(pbs_config.nodes) > 1 and pbs_config.ppn != "" \
                and int(pbs_config.ppn) > 1:
            directives.append("#PBS -l nodes=%s:ppn=%s" % (pbs_config.nodes,
                                                           pbs_config.ppn))

        # PBS -l mem=500mb
        if pbs_config.memory != "":
            directives.append("#PBS -l mem=%s" % pbs_config.memory)

        # PBS -l scratch=1gb
        if pbs_config.scratch != "":
            directives.append("#PBS -l scratch=%s" % pbs_config.scratch)

        # PBS -q queue
        if pbs_config.queue != "":
            directives.append("#PBS -q %s" % pbs_config.queue)

        return directives

    @staticmethod
    def get_qsub_args():
        """Return qsub arguments in list"""
        return []

class PbsDialectPBSPro(PbsDialect):
    @staticmethod
    def get_pbs_directives(work_dir, pbs_config):
        """
        Generates file directives for specific PBS system.
        :param work_dir: Path to MJ, specifies output file.
        :param pbs_config: PbsConf object with data.
        :return: List of PBS directives.
        """
        directives = []
        directives.append("#PBS -S /bin/bash")
        # ToDo fix terse
        # There seems to be no option for that
        # http://docs.adaptivecomputing.com/torque/4-0-2/Content/topics/commands/qsub.htm#-t
        # directives.append("#PBS -terse")
        directives.append('#PBS -o "{}"'.format(os.path.join(work_dir, "pbs_output")))
        directives.append('#PBS -e "{}"'.format(os.path.join(work_dir, "pbs_error")))
        #directives.append("#PBS -d " + work_dir)

        # PBS -N name
        if pbs_config.name != "":
            directives.append("#PBS -N %s" % pbs_config.name)

        # PBS -l select=1:ncpus=1
        chunks = "1"
        if pbs_config.nodes != "":
            chunks = pbs_config.nodes

        ncpus = "1"
        if pbs_config.ppn != "":
            ncpus = pbs_config.ppn

        select = "#PBS -l select=%s:ncpus=%s" % (chunks, ncpus)

        # :mem=500mb
        if pbs_config.memory != "":
            select += ":mem=%s" % pbs_config.memory

        # :scratch_local=1gb
        if pbs_config.scratch != "":
            select += ":scratch_local=%s" % pbs_config.scratch

        directives.append(select)

        # PBS -l walltime=1:00:00
        walltime = "1:00:00"
        if pbs_config.walltime != "":
            walltime = pbs_config.walltime
        directives.append("#PBS -l walltime=%s" % walltime)

        # PBS -q queue
        if pbs_config.queue != "":
            directives.append("#PBS -q %s" % pbs_config.queue)

        return directives

    @staticmethod
    def get_qsub_args():
        """Return qsub arguments in list"""
        return []
