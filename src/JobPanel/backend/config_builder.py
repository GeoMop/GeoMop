import os
import json
import logging

from Analysis.client_pipeline.mj_preparation import *
from JobPanel.ui.dialogs import SshPasswordDialog
from JobPanel.data.secret import Secret
from gm_base.geomop_analysis import Analysis, InvalidAnalysis
from .path_converter import if_win_win2lin_conv_path


def build(data_app, mj_id):
    """Builds configuration for multijob running."""
    err = []

    # multijob preset properties
    mj_preset = data_app.multijobs[mj_id].preset
    mj_name = mj_preset.name
    an_name = mj_preset.analysis
    mj_log_level = mj_preset.log_level
    if mj_preset.from_mj is not None:
        reuse_mj = data_app.multijobs[mj_preset.from_mj].preset.name
    else:
        reuse_mj = None

    # resource preset
    mj_ssh_preset = data_app.ssh_presets.get(mj_preset.mj_ssh_preset, None)
    mj_pbs_preset = data_app.pbs_presets.get(mj_preset.mj_pbs_preset, None)

    j_ssh_preset = data_app.ssh_presets.get(mj_preset.j_ssh_preset, None)
    j_pbs_preset = data_app.pbs_presets.get(mj_preset.j_pbs_preset, None)

    # prepare mj
    workspace = data_app.workspaces.workspace
    analysis = an_name
    mj = mj_name
    python_script = "analysis.py"
    try:
        an = Analysis.open(data_app.workspaces.get_path(), an_name)
        for file in an.script_files:
            if file.selected:
                python_script = file.file_path
                break
    except InvalidAnalysis:
        pass
    e, input_files = MjPreparation.prepare(workspace=workspace, analysis=analysis, mj=mj,
                                           python_script=python_script, reuse_mj=reuse_mj)
    if len(e) > 0:
        err.extend(e)
        return err, None

    # mj_config_dir
    mj_config_dir = os.path.join(workspace, analysis, "mj", mj)

    # ToDo: vyresit lepe
    loc_geomop_root = if_win_win2lin_conv_path(os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "..", ".."))
    loc_geomop_analysis_workspace = if_win_win2lin_conv_path(os.path.abspath(workspace))

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

    # docker flow123d executable
    # todo: v budoucnu bude brat z executables.json, ktery bude primo v dockeru
    docker_flow123d = {"__class__": "Executable",
                       "name": "flow123d",
                       "path": "/opt/flow123d/bin/flow123d"}

    # mj environment
    if mj_ssh_preset is not None:
        env_mj = {"__class__": "Environment",
                  "geomop_root": mj_ssh_preset.geomop_root,
                  "geomop_analysis_workspace": mj_ssh_preset.workspace,
                  "executables": [],
                  "python": mj_ssh_preset.geomop_root + "/" + "bin/python"}
    else:
        env_mj = {"__class__": "Environment",
                  "geomop_root": loc_geomop_root,
                  "geomop_analysis_workspace": loc_geomop_analysis_workspace,
                  "executables": [],
                  "python": "python3"}

    # job environment
    if j_ssh_preset is not None:
        env_j = {"__class__": "Environment",
                 "geomop_root": j_ssh_preset.geomop_root,
                 "geomop_analysis_workspace": j_ssh_preset.workspace,
                 "executables": [job_service],
                 "python": j_ssh_preset.geomop_root + "/" + "bin/python"}
    else:
        env_j = env_mj.copy()
        env_j["executables"] = [job_service, docker_flow123d] if (mj_ssh_preset is None) else [job_service]

    # mj connection
    if mj_ssh_preset is None:
        mj_con = {"__class__": "ConnectionLocal",
              "address": "localhost",
              "environment": env_mj,
              "name": "localhost"}
    else:
        if mj_ssh_preset.to_pc:
            s = Secret()
            pwd = s.demangle(mj_ssh_preset.pwd)
        else:
            dialog = SshPasswordDialog(None, mj_ssh_preset)
            if dialog.exec_():
                pwd = dialog.password
            else:
                err.append("PasswordDialog: Password not entered.")
                return err, None
        #u, pwd = get_passwords()["metacentrum"]
        mj_con = {"__class__": "ConnectionSSH",
              "address": mj_ssh_preset.host,
              "uid": mj_ssh_preset.uid,
              "password": pwd,
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
                            "pbs_args": _get_pbs_conf(mj_pbs_preset)}}

    if j_pbs_preset is None:
        job_pe = {"__class__": "ProcessExec"}
    else:
        job_pe = {"__class__": "ProcessPBS",
                  "exec_args": {"__class__": "ExecArgs",
                                "pbs_args": _get_pbs_conf(j_pbs_preset)}}

    log_all = mj_log_level == logging.INFO
    job_service_data = {"service_host_connection": j_con,
                        "process": job_pe,
                        "log_all": log_all}
    service_data = {"service_host_connection": mj_con,
                    "process": pe,
                    "workspace": analysis + "/mj/" + mj,
                    "config_file_name": "_mj_service.conf",
                    "pipeline": {"python_script": python_script,
                                 "pipeline_name": "pipeline"},
                    "job_service_data": job_service_data,
                    "input_files": input_files,
                    "log_all": log_all,
                    "reuse_mj": reuse_mj if (reuse_mj is not None) else ""}

    #print(json.dumps(service_data, indent=4, sort_keys=True))
    return err, service_data




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




def build_ssh_conf(ssh):
    """Builds configuration for ssh test."""
    # environment
    env = {"__class__": "Environment",
           "geomop_root": ssh.geomop_root,
           "geomop_analysis_workspace": ssh.workspace,
           "python": ssh.geomop_root + "/" + "bin/python"}

    # connection
    con = {"__class__": "ConnectionSSH",
           "address": ssh.host,
           "uid": ssh.uid,
           "password": ssh.pwd,
           "environment": env,
           "name": ssh.name}

    return con


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
