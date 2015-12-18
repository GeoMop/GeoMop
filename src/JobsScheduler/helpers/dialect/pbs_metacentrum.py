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
    def get_pbs_directives(mj_path, config):
        """
        Generates file directives for specific PBS system.
        :param mj_path: Path to MJ, specifies output file.
        :param config: PbsConf object with data.
        :return: List of PBS directives.
        """
        directives = list()
        directives.append("#$ -cwd")
        directives.append("#$ -S /bin/bash")
        directives.append("#$ -terse")
        directives.append("#$ -o " + mj_path + "/" +
                          config.name + "/pbs_output")
        directives.append("#$ -e " + mj_path + "/" +
                          config.name + "/pbs_error")

        # specify queue, i.e. all.q
        if config.queue:
            directives.append("#$ -q %s" % config.queue)

        # request a parallel environment, i.e. 'openmpi' using n slots (CPUs)
        if config.nodes and int(config.nodes) > 1:
            directives.append("#$ -pe %s %s" % ("openmpi", config.nodes))

        # -l resource=value, ...
        # ToDo opravit, nejasny syntax a pouzitelne direktivy
        resources = list()
        res_dir = "#$ -l "
        if config.walltime:
            pass
        if config.memory:
            resources.append("mem=" + config.memory[:-2])
        if config.scratch:
            resources.append("scratch=" + config.scratch[:-2])
        for res in resources:
            res_dir = res_dir + ", " + res

        directives.append(res_dir)
        return directives
