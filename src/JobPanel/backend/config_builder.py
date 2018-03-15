import os
import json

from client_pipeline.mj_preparation import *


def build(data_app, mj_id):
    """Builds configuration for multijob running."""

    # multijob preset properties
    mj_preset = data_app.multijobs[mj_id].preset
    mj_name = mj_preset.name
    an_name = mj_preset.analysis
    res_preset = data_app.resource_presets[mj_preset.resource_preset]
    mj_log_level = mj_preset.log_level
    mj_number_of_processes = mj_preset.number_of_processes

    # resource preset
    mj_execution_type = res_preset.mj_execution_type
    mj_ssh_preset = data_app.ssh_presets.get(res_preset.mj_ssh_preset, None)
    mj_remote_execution_type = res_preset.mj_remote_execution_type
    mj_pbs_preset = data_app.pbs_presets.get(res_preset.mj_pbs_preset, None)
    if mj_ssh_preset is None:
        mj_env = data_app.config.local_env
    else:
        mj_env = mj_ssh_preset.env
    mj_env = data_app.env_presets[mj_env]

    j_execution_type = res_preset.j_execution_type
    j_ssh_preset = data_app.ssh_presets.get(res_preset.j_ssh_preset, None)
    j_remote_execution_type = res_preset.j_remote_execution_type
    j_pbs_preset = data_app.pbs_presets.get(res_preset.j_pbs_preset, None)
    if j_ssh_preset is None:
        j_env = mj_env
    else:
        j_env = j_ssh_preset.env
        j_env = data_app.env_presets[j_env]




    # prepare mj
    workspace = data_app.workspaces.workspace
    analysis = an_name
    mj = mj_name
    err, input_files = MjPreparation.prepare(workspace=workspace, analysis=analysis, mj=mj)
    if len(err) > 0:
        for e in err:
            print(e)
        #os.exit()

    # mj_config_dir
    mj_config_dir = os.path.join(workspace, analysis, "mj", mj, "mj_config")

    # todo: docasne, zatim neni kde brat
    rem_geomop_root = "/storage/brno2/home/radeksrb/work/GeoMop/src"
    rem_geomop_analysis_workspace = "/storage/brno2/home/radeksrb/work/workspace"
    loc_geomop_root = "/home/radek/work/GeoMop/src"
    loc_geomop_analysis_workspace = os.path.abspath(workspace)

    # multi_job_service executable
    multi_job_service = {"__class__": "Executable",
                         "name": "multi_job_service",
                         "path": "JobPanel/services/multi_job_service.py",
                         "script": True}

    # job_service executable
    job_service = {"__class__": "Executable",
                   "name": "job_service",
                   "path": "JobPanel/services/job_service.py",
                   "script": True}

    # flow123d executable
    flow123d = {"__class__": "Executable",
                "name": "flow123d",
                "path": j_env.flow_path}

    # mj environment
    env_mj = {"__class__": "Environment",
           "geomop_root": loc_geomop_root if mj_ssh_preset is None else rem_geomop_root,
           "geomop_analysis_workspace": loc_geomop_analysis_workspace if mj_ssh_preset is None else rem_geomop_analysis_workspace,
           "executables": [],
           "python": mj_env.python_exec}

    # job environment
    env_j = {"__class__": "Environment",
           "geomop_root": env_mj["geomop_root"] if j_ssh_preset is None else rem_geomop_root,
           "geomop_analysis_workspace": env_mj["geomop_analysis_workspace"] if j_ssh_preset is None else rem_geomop_analysis_workspace,
           "executables": [job_service, flow123d],
           "python": j_env.python_exec}

    # mj connection
    if mj_ssh_preset is None:
        mj_con = {"__class__": "ConnectionLocal",
              "address": "localhost",
              "environment": env_mj,
              "name": "localhost"}
    else:
        # ToDo: jmena, hesla
        u, p = get_passwords()["metacentrum"]
        mj_con = {"__class__": "ConnectionSSH",
              "address": mj_ssh_preset.host,
              "uid": mj_ssh_preset.uid,
              "password": p,
              "environment": env_mj,
              "name": mj_ssh_preset.name}

    # j connection
    if j_ssh_preset is None:
        j_con = {"__class__": "ConnectionLocal",
              "address": "localhost",
              "environment": env_j,
              "name": "localhost"}
    else:
        u, p = get_passwords()["metacentrum"]
        j_con = {"__class__": "ConnectionSSH",
              "address": j_ssh_preset.host,
              "uid": j_ssh_preset.uid,
              # ToDo: nechci, aby se heslo ulozilo, nebude fungovat pripadne prihlasovani
              "password": "",
              "environment": env_j,
              "name": j_ssh_preset.name}

    # multi job data
    if mj_pbs_preset is None:
        pe = {"__class__": "ProcessExec",
              "executable": multi_job_service}
    else:
        pe = {"__class__": "ProcessPBS",
              "executable": multi_job_service,
              "exec_args": {"__class__": "ExecArgs",
                            "pbs_args": _get_pbs_conf(mj_pbs_preset, mj_env.pbs_params)}}

    if j_pbs_preset is None:
        job_pe = {"__class__": "ProcessExec"}
    else:
        job_pe = {"__class__": "ProcessPBS",
                  "exec_args": {"__class__": "ExecArgs",
                                "pbs_args": _get_pbs_conf(j_pbs_preset, j_env.pbs_params)}}

    job_service_data = {"service_host_connection": j_con,
                        "process": job_pe}
    service_data = {"service_host_connection": mj_con,
                    "process": pe,
                    "workspace": analysis + "/mj/" + mj + "/mj_config",
                    "config_file_name": "mj_service.conf",
                    "pipeline": {"python_script": "analysis.py",
                                 "pipeline_name": "pipeline"},
                    "job_service_data": job_service_data,
                    "input_files": input_files}

    #print(json.dumps(service_data, indent=4, sort_keys=True))
    return service_data




    #########################
    # testovaci konfigurace #
    #########################


    # docker
    ########

    # # job_service executable
    # job_service = {"__class__": "Executable",
    #                "name": "job_service",
    #                "path": "JobPanel/services/_job_service.py",
    #                "script": True}
    #
    # # flow123d executable
    # flow123d = {"__class__": "Executable",
    #             "name": "flow123d",
    #             #"path": "/home/radek/work/Flow123d-2.1.0-linux-install/bin/flow123d.sh"}
    #             "path": "/opt/flow123d/bin/flow123d"}
    #             #"path": "/storage/praha1/home/jan_brezina/local/flow123d_2.2.0/"}
    #
    # # environment
    # env = {"__class__": "Environment",
    #        "geomop_root": "/home/radek/work/GeoMop/src",
    #        "geomop_analysis_workspace": os.path.abspath(workspace),
    #        "executables": [job_service, flow123d],
    #        "python": "python3"}
    #
    # # local connection
    # cl = {"__class__": "ConnectionLocal",
    #       "address": "localhost",
    #       "environment": env,
    #       "name": "localhost"}
    #
    # # multi job data
    # pe = {"__class__": "ProcessExec",
    #       "executable": {"__class__": "Executable",
    #                      "path": "JobPanel/services/multi_job_service.py",
    #                      "script": True}}
    # job_pe = {"__class__": "ProcessExec"}
    # job_service_data = {"service_host_connection": cl,
    #                     "process": job_pe}
    # service_data = {"service_host_connection": cl,
    #                 "process": pe,
    #                 # ToDo: musi byt vzdy s "/"
    #                 "workspace": os.path.join(analysis, "mj", mj, "mj_config"),
    #                 "config_file_name": "mj_service.conf",
    #                 "pipeline": {"python_script": python_script,
    #                              "pipeline_name": pipeline_name},
    #                 "job_service_data": job_service_data}
    # return service_data


    # mj docker, job charon frontend
    ################################

    # # job_service executable
    # job_service = {"__class__": "Executable",
    #                "name": "job_service",
    #                "path": "JobPanel/services/_job_service.py",
    #                "script": True}
    #
    # # flow123d executable
    # flow123d = {"__class__": "Executable",
    #             "name": "flow123d",
    #             #"path": "/home/radek/work/Flow123d-2.1.0-linux-install/bin/flow123d.sh"}
    #             "path": "/storage/brno2/home/radeksrb/flow123d.sh"}
    #             #"path": "/storage/praha1/home/jan_brezina/local/flow123d_2.2.0/"}
    #
    # # environment
    # env = {"__class__": "Environment",
    #        "geomop_root": "/home/radek/work/GeoMop/src",
    #        "geomop_analysis_workspace": os.path.abspath(workspace),
    #        "executables": [job_service, flow123d],
    #        "python": "python3"}
    #
    # env_charon = {"__class__": "Environment",
    #        "geomop_root": "/storage/brno2/home/radeksrb/work/GeoMop/src",
    #        "geomop_analysis_workspace": "/storage/brno2/home/radeksrb/work/workspace",
    #        "executables": [job_service, flow123d],
    #        "python": "/storage/brno2/home/radeksrb/geomop_python.sh"}
    #
    # # local connection
    # cl = {"__class__": "ConnectionLocal",
    #       "address": "localhost",
    #       "environment": env,
    #       "name": "localhost"}
    #
    # cl_charon = {"__class__": "ConnectionLocal",
    #       "address": "localhost",
    #       "environment": env_charon,
    #       "name": "localhost"}
    #
    # u, p = get_passwords()["metacentrum"]
    # cr_charon = {"__class__": "ConnectionSSH",
    #       "address": "charon-ft.nti.tul.cz",
    #       "uid": u,
    #       "password": p,
    #       "environment": env_charon,
    #       "name": "charon"}
    #
    # # multi job data
    # pe = {"__class__": "ProcessExec",
    #       "executable": {"__class__": "Executable",
    #                      "path": "JobPanel/services/multi_job_service.py",
    #                      "script": True}}
    # job_pe = {"__class__": "ProcessExec"}
    # job_service_data = {"service_host_connection": cr_charon,
    #                     "process": job_pe}
    # service_data = {"service_host_connection": cl,
    #                 "process": pe,
    #                 # ToDo: musi byt vzdy s "/"
    #                 "workspace": os.path.join(analysis, "mj", mj, "mj_config"),
    #                 "config_file_name": "mj_service.conf",
    #                 "pipeline": {"python_script": "analysis.py",
    #                              "pipeline_name": "pipeline"},
    #                 "job_service_data": job_service_data,
    #                 "input_files": ["s.py", "V7_jb_par.sprt", "V7_jb_par.yaml", "V7.msh"]}
    #
    # return service_data


    # charon frontend
    #################

    # # job_service executable
    # job_service = {"__class__": "Executable",
    #                "name": "job_service",
    #                "path": "JobPanel/services/_job_service.py",
    #                "script": True}
    #
    # # flow123d executable
    # flow123d = {"__class__": "Executable",
    #             "name": "flow123d",
    #             #"path": "/home/radek/work/Flow123d-2.1.0-linux-install/bin/flow123d.sh"}
    #             #"path": "/opt/flow123d/bin/flow123d"}
    #             #"path": "/storage/praha1/home/jan_brezina/local/flow123d_2.2.0/flow123d"}
    #             #"path": "/storage/praha1/home/jan-hybs/projects/Flow123dDocker/flow123d/bin/flow123d"}
    #             "path": "/storage/brno2/home/radeksrb/flow123d.sh"}
    #
    # # environment
    # env = {"__class__": "Environment",
    #        "geomop_root": "/home/radek/work/GeoMop/src",
    #        "geomop_analysis_workspace": os.path.abspath(workspace),
    #        "executables": [job_service, flow123d],
    #        "python": "python3"}
    #
    # env_charon = {"__class__": "Environment",
    #        "geomop_root": "/storage/brno2/home/radeksrb/work/GeoMop/src",
    #        "geomop_analysis_workspace": "/storage/brno2/home/radeksrb/work/workspace",
    #        "executables": [job_service, flow123d],
    #        "python": "/storage/brno2/home/radeksrb/geomop_python.sh"}
    #
    # # local connection
    # cl = {"__class__": "ConnectionLocal",
    #       "address": "localhost",
    #       "environment": env,
    #       "name": "localhost"}
    #
    # cl_charon = {"__class__": "ConnectionLocal",
    #       "address": "localhost",
    #       "environment": env_charon,
    #       "name": "localhost"}
    #
    # u, p = get_passwords()["metacentrum"]
    # cr_charon = {"__class__": "ConnectionSSH",
    #       "address": "charon-ft.nti.tul.cz",
    #       "uid": u,
    #       "password": p,
    #       "environment": env_charon,
    #       "name": "charon"}
    #
    # # multi job data
    # pe = {"__class__": "ProcessExec",
    #       "executable": {"__class__": "Executable",
    #                      "path": "JobPanel/services/multi_job_service.py",
    #                      "script": True}}
    # job_pe = {"__class__": "ProcessExec"}
    # job_service_data = {"service_host_connection": cl_charon,
    #                     "process": job_pe}
    # service_data = {"service_host_connection": cr_charon,
    #                 "process": pe,
    #                 # ToDo: musi byt vzdy s "/"
    #                 "workspace": os.path.join(analysis, "mj", mj, "mj_config"),
    #                 "config_file_name": "mj_service.conf",
    #                 "pipeline": {"python_script": "analysis.py",
    #                              "pipeline_name": "pipeline"},
    #                 "job_service_data": job_service_data,
    #                 "input_files": ["analysis.py", "V7_jb_par.sprt", "V7_jb_par.yaml", "V7.msh"]}
    #
    # return service_data


    # charon PBS
    ############

    # # job_service executable
    # job_service = {"__class__": "Executable",
    #                "name": "job_service",
    #                "path": "JobPanel/services/_job_service.py",
    #                "script": True}
    #
    # # flow123d executable
    # flow123d = {"__class__": "Executable",
    #             "name": "flow123d",
    #             #"path": "/home/radek/work/Flow123d-2.1.0-linux-install/bin/flow123d.sh"}
    #             #"path": "/opt/flow123d/bin/flow123d"}
    #             #"path": "/storage/praha1/home/jan_brezina/local/flow123d_2.2.0/flow123d"}
    #             #"path": "/storage/praha1/home/jan-hybs/projects/Flow123dDocker/flow123d/bin/flow123d"}
    #             "path": "/storage/brno2/home/radeksrb/flow123d.sh"}
    #
    # # environment
    # env = {"__class__": "Environment",
    #        "geomop_root": "/home/radek/work/GeoMop/src",
    #        "geomop_analysis_workspace": os.path.abspath(workspace),
    #        "executables": [job_service, flow123d],
    #        "python": "python3"}
    #
    # env_charon = {"__class__": "Environment",
    #        "geomop_root": "/storage/brno2/home/radeksrb/work/GeoMop/src",
    #        "geomop_analysis_workspace": "/storage/brno2/home/radeksrb/work/workspace",
    #        "executables": [job_service, flow123d],
    #        "python": "/storage/brno2/home/radeksrb/geomop_python.sh"}
    #
    # # local connection
    # cl = {"__class__": "ConnectionLocal",
    #       "address": "localhost",
    #       "environment": env,
    #       "name": "localhost"}
    #
    # cl_charon = {"__class__": "ConnectionLocal",
    #       "address": "localhost",
    #       "environment": env_charon,
    #       "name": "localhost"}
    #
    # u, p = get_passwords()["metacentrum"]
    # cr_charon = {"__class__": "ConnectionSSH",
    #       "address": "charon-ft.nti.tul.cz",
    #       "uid": u,
    #       "password": p,
    #       "environment": env_charon,
    #       "name": "charon"}
    #
    # # multi job data
    # pe = {"__class__": "ProcessPBS",
    #       "executable": {"__class__": "Executable",
    #                      "path": "JobPanel/services/multi_job_service.py",
    #                      "script": True},
    #       "exec_args": {"__class__": "ExecArgs", "pbs_args": {"__class__": "PbsConfig", "dialect": {"__class__": "PbsDialectPBSPro"}, "queue": "charon"}}}
    # job_pe = {"__class__": "ProcessExec"}
    # job_service_data = {"service_host_connection": cl_charon,
    #                     "process": job_pe}
    # service_data = {"service_host_connection": cr_charon,
    #                 "process": pe,
    #                 # ToDo: musi byt vzdy s "/"
    #                 "workspace": os.path.join(analysis, "mj", mj, "mj_config"),
    #                 "config_file_name": "mj_service.conf",
    #                 "pipeline": {"python_script": "analysis.py",
    #                              "pipeline_name": "pipeline"},
    #                 "job_service_data": job_service_data,
    #                 "input_files": ["analysis.py", "V7_jb_par.sprt", "V7_jb_par.yaml", "V7.msh"]}
    #
    # return service_data


    # charon frontend job PBS
    #########################

    # # job_service executable
    # job_service = {"__class__": "Executable",
    #                "name": "job_service",
    #                "path": "JobPanel/services/_job_service.py",
    #                "script": True}
    #
    # # flow123d executable
    # flow123d = {"__class__": "Executable",
    #             "name": "flow123d",
    #             #"path": "/home/radek/work/Flow123d-2.1.0-linux-install/bin/flow123d.sh"}
    #             #"path": "/opt/flow123d/bin/flow123d"}
    #             #"path": "/storage/praha1/home/jan_brezina/local/flow123d_2.2.0/flow123d"}
    #             #"path": "/storage/praha1/home/jan-hybs/projects/Flow123dDocker/flow123d/bin/flow123d"}
    #             "path": "/storage/brno2/home/radeksrb/flow123d.sh"}
    #
    # # environment
    # env = {"__class__": "Environment",
    #        "geomop_root": "/home/radek/work/GeoMop/src",
    #        "geomop_analysis_workspace": os.path.abspath(workspace),
    #        "executables": [job_service, flow123d],
    #        "python": "python3"}
    #
    # env_charon = {"__class__": "Environment",
    #        "geomop_root": "/storage/brno2/home/radeksrb/work/GeoMop/src",
    #        "geomop_analysis_workspace": "/storage/brno2/home/radeksrb/work/workspace",
    #        "executables": [job_service, flow123d],
    #        "python": "/storage/brno2/home/radeksrb/geomop_python.sh"}
    #
    # # local connection
    # cl = {"__class__": "ConnectionLocal",
    #       "address": "localhost",
    #       "environment": env,
    #       "name": "localhost"}
    #
    # cl_charon = {"__class__": "ConnectionLocal",
    #       "address": "localhost",
    #       "environment": env_charon,
    #       "name": "localhost"}
    #
    # u, p = get_passwords()["metacentrum"]
    # cr_charon = {"__class__": "ConnectionSSH",
    #       "address": "charon-ft.nti.tul.cz",
    #       "uid": u,
    #       "password": p,
    #       "environment": env_charon,
    #       "name": "charon"}
    #
    # # multi job data
    # pe = {"__class__": "ProcessExec",
    #       "executable": {"__class__": "Executable",
    #                      "path": "JobPanel/services/multi_job_service.py",
    #                      "script": True}}
    # job_pe = {"__class__": "ProcessPBS",
    #           "exec_args": {"__class__": "ExecArgs", "pbs_args": {"__class__": "PbsConfig", "dialect": {"__class__": "PbsDialectPBSPro"}, "queue": "charon"}}}
    # job_service_data = {"service_host_connection": cl_charon,
    #                     "process": job_pe}
    # service_data = {"service_host_connection": cr_charon,
    #                 "process": pe,
    #                 # ToDo: musi byt vzdy s "/"
    #                 "workspace": os.path.join(analysis, "mj", mj, "mj_config"),
    #                 "config_file_name": "mj_service.conf",
    #                 "pipeline": {"python_script": python_script,
    #                              "pipeline_name": pipeline_name},
    #                 "job_service_data": job_service_data,
    #                 "input_files": ["s.py", "V7_jb_par.sprt", "V7_jb_par.yaml", "V7.msh"]}
    #
    # return service_data


    # charon PBS job PBS
    ####################

    # # job_service executable
    # job_service = {"__class__": "Executable",
    #                "name": "job_service",
    #                "path": "JobPanel/services/_job_service.py",
    #                "script": True}
    #
    # # flow123d executable
    # flow123d = {"__class__": "Executable",
    #             "name": "flow123d",
    #             #"path": "/home/radek/work/Flow123d-2.1.0-linux-install/bin/flow123d.sh"}
    #             #"path": "/opt/flow123d/bin/flow123d"}
    #             #"path": "/storage/praha1/home/jan_brezina/local/flow123d_2.2.0/flow123d"}
    #             #"path": "/storage/praha1/home/jan-hybs/projects/Flow123dDocker/flow123d/bin/flow123d"}
    #             "path": "/storage/brno2/home/radeksrb/flow123d.sh"}
    #
    # # environment
    # env = {"__class__": "Environment",
    #        "geomop_root": "/home/radek/work/GeoMop/src",
    #        "geomop_analysis_workspace": os.path.abspath(workspace),
    #        "executables": [job_service, flow123d],
    #        "python": "python3"}
    #
    # env_charon = {"__class__": "Environment",
    #        "geomop_root": "/storage/brno2/home/radeksrb/work/GeoMop/src",
    #        "geomop_analysis_workspace": "/storage/brno2/home/radeksrb/work/workspace",
    #        "executables": [job_service, flow123d],
    #        "python": "/storage/brno2/home/radeksrb/geomop_python.sh"}
    #
    # # local connection
    # cl = {"__class__": "ConnectionLocal",
    #       "address": "localhost",
    #       "environment": env,
    #       "name": "localhost"}
    #
    # cl_charon = {"__class__": "ConnectionLocal",
    #       "address": "localhost",
    #       "environment": env_charon,
    #       "name": "localhost"}
    #
    # u, p = get_passwords()["metacentrum"]
    # cr_charon = {"__class__": "ConnectionSSH",
    #       "address": "charon-ft.nti.tul.cz",
    #       "uid": u,
    #       "password": p,
    #       "environment": env_charon,
    #       "name": "charon"}
    #
    # # multi job data
    # pe = {"__class__": "ProcessPBS",
    #       "executable": {"__class__": "Executable",
    #                      "path": "JobPanel/services/multi_job_service.py",
    #                      "script": True},
    #       "exec_args": {"__class__": "ExecArgs", "pbs_args": {"__class__": "PbsConfig", "dialect": {"__class__": "PbsDialectPBSPro"}, "queue": "charon"}}}
    # job_pe = {"__class__": "ProcessPBS",
    #           "exec_args": {"__class__": "ExecArgs",
    #                         "pbs_args": {"__class__": "PbsConfig", "dialect": {"__class__": "PbsDialectPBSPro"}, "queue": "charon"}}}
    # job_service_data = {"service_host_connection": cl_charon,
    #                     "process": job_pe}
    # service_data = {"service_host_connection": cr_charon,
    #                 "process": pe,
    #                 # ToDo: musi byt vzdy s "/"
    #                 "workspace": os.path.join(analysis, "mj", mj, "mj_config"),
    #                 "config_file_name": "mj_service.conf",
    #                 "pipeline": {"python_script": python_script,
    #                              "pipeline_name": pipeline_name},
    #                 "job_service_data": job_service_data,
    #                 "input_files": ["s.py", "V7_jb_par.sprt", "V7_jb_par.yaml", "V7.msh"]}
    #
    # return service_data




def _get_pbs_conf(preset, pbs_params=[]):
    """
    Converts preset data to PbsConfig.
    :param preset: Preset data object from UI.
    :return: PbsConfig
    """
    pbs = {"__class__": "PbsConfig"}

    pbs["name"] = preset.name
    pbs["dialect"] = {"__class__": preset.pbs_system}
    pbs["queue"] = preset.queue
    pbs["walltime"] = preset.walltime
    pbs["nodes"] = str(preset.nodes)
    pbs["ppn"] = str(preset.ppn)
    pbs["memory"] = preset.memory
    pbs["pbs_params"] = pbs_params

    return pbs


# todo: jen pro testovaci ucely
def get_passwords():
    """Return dict with passwords from secret file."""
    file = os.path.expanduser("~/.ssh/passwords")
    d = {}
    try:
        with open(file, 'r') as fd:
            for line in fd:
                line = line.split(sep="#", maxsplit=1)[0]
                line = line.strip()
                sp = line.split(sep=":")
                if len(sp) == 3:
                    d[sp[0]] = (sp[1], sp[2])
    except:
        pass
    return d
