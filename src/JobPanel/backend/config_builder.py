import os

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
    workspace = "/home/radek/work/workspace"#data_app.workspace
    analysis = an_name
    mj = mj_name
    python_script = "s.py"
    pipeline_name = "Pipeline_5"
    err = MjPreparation.prepare(workspace=workspace, analysis=analysis, mj=mj,
                                python_script=python_script, pipeline_name=pipeline_name)
    if len(err) > 0:
        for e in err:
            print(e)
        #os.exit()

    # mj_config_dir
    mj_config_dir = os.path.join(workspace, analysis, "mj", mj, "mj_config")

    # job_service executable
    job_service = {"__class__": "Executable",
                   "name": "job_service",
                   "path": "JobPanel/services/_job_service.py",
                   "script": True}

    # flow123d executable
    flow123d = {"__class__": "Executable",
                "name": "flow123d",
                #"path": "/home/radek/work/Flow123d-2.1.0-linux-install/bin/flow123d.sh"}
                "path": "/opt/flow123d/bin/flow123d"}

    # environment
    env = {"__class__": "Environment",
           "geomop_root": "/home/radek/work/GeoMop/src",
           "geomop_analysis_workspace": os.path.abspath(workspace),
           "executables": [job_service, flow123d],
           "python": "python3"}

    # local connection
    cl = {"__class__": "ConnectionLocal",
          "address": "localhost",
          "environment": env,
          "name": "localhost"}

    # multi job data
    pe = {"__class__": "ProcessExec",
          "executable": {"__class__": "Executable",
                         "path": "JobPanel/services/multi_job_service.py",
                         "script": True}}
    job_pe = {"__class__": "ProcessExec"}
    job_service_data = {"service_host_connection": cl,
                        "process": job_pe}
    service_data = {"service_host_connection": cl,
                    "process": pe,
                    # ToDo: musi byt vzdy s "/"
                    "workspace": os.path.join(analysis, "mj", mj, "mj_config"),
                    "config_file_name": "mj_service.conf",
                    "pipeline": {"python_script": python_script,
                                 "pipeline_name": pipeline_name},
                    "job_service_data": job_service_data}

    return service_data
