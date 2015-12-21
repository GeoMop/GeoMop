# -*- coding: utf-8 -*-
"""
Dialect for specific Metacentrum PBS environment.
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

import re

__dialect_name__ = "Hydra"
__dialect_class__ = "PbsDialect"
__queue_file__ = "hydra_queues.txt"


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
        directives.append("#$ -cwd")
        directives.append("#$ -S /bin/bash")
        directives.append("#$ -terse")
        directives.append("#$ -o " + mj_path + "/" +
                          pbs_config.name + "/pbs_output")
        directives.append("#$ -e " + mj_path + "/" +
                          pbs_config.name + "/pbs_error")

        # specify queue, i.e. all.q
        if pbs_config.queue:
            directives.append("#$ -q %s" % pbs_config.queue)

        # request a parallel environment, i.e. 'openmpi' using n slots (CPUs)
        if pbs_config.nodes and int(pbs_config.nodes) > 1:
            directives.append("#$ -pe %s %s" % ("openmpi", pbs_config.nodes))

        # -l resource=value, ...
        resources = list()
        res_dir = "#$ -l "
        if pbs_config.walltime:
            pass
        if pbs_config.memory:
            resources.append("mem=" + re.findall(r'\d+', pbs_config.memory)[0])
        if pbs_config.scratch:
            resources.append("scratch=" + re.findall(r'\d+',
                                                     pbs_config.scratch)[0])
        for res in resources:
            res_dir = res_dir + ", " + res

        # only if there is some resource specification
        if resources:
            directives.append(res_dir)

        return directives
