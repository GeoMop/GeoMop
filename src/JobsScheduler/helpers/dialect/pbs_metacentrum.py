# -*- coding: utf-8 -*-
"""
Dialect for specific Metacentrum PBS environment.
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

__dialect_name__ = "Metacentrum"
__dialect_class__ = "PbsDialect"
__queue_file__ = "meta_queues.txt"


class PbsDialect:
    @staticmethod
    def get_pbs_directives(mj_path, pbs_config):
        """
        Generates file directives for specific PBS system.
        :param mj_path: Path to MJ, specifies output file.
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
        directives.append("#PBS -o " + mj_path + "/" +
                          pbs_config.name + "/pbs_output")
        directives.append("#PBS -e " + mj_path + "/" +
                          pbs_config.name + "/pbs_error")
        directives.append("#PBS -d " + mj_path + "/" +
                          pbs_config.name)

        # PBS -N name
        if pbs_config.name:
            directives.append("#PBS -N %s" % pbs_config.name)

        # PBS -l nodes=1:ppn=1
        if pbs_config.nodes and int(pbs_config.nodes) > 1 and pbs_config.ppn \
                and int(pbs_config.ppn) > 1:
            directives.append("#PBS -l nodes=%s:ppn=%s" % (pbs_config.nodes,
                                                           pbs_config.ppn))

        # PBS -l mem=500mb
        if pbs_config.memory:
            directives.append("#PBS -l mem=%s" % pbs_config.memory)

        # PBS -l scratch=1gb
        if pbs_config.scratch:
            directives.append("#PBS -l scratch=%s" % pbs_config.scratch)

        # PBS -q queue
        if pbs_config.queue:
            directives.append("#PBS -q %s" % pbs_config.queue)

        return directives
    
    @staticmethod
    def get_qsub_args():
        """Return qsub arguments in list"""
        return []
        
    @staticmethod
    def get_outpup_file():
        """
        return output file if is specific, None for standart output file from
        -o parameter
        
        Torque return output file after pbs job clossing - set alternative file
        """
        return None

