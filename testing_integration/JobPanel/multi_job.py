import os
import shutil
import threading
import time

from client_pipeline.mj_preparation import *
from pipeline.pipeline_processor import *
from backend.service_base import ServiceBase, ServiceStatus


# setting testing directory
test_dir = "/home/radek/work/test/multi_job"


# remove old files
workspace = os.path.join(test_dir, "workspace")
shutil.rmtree(workspace, ignore_errors=True)

# copy files to testing directory
shutil.copytree("multi_job_res/workspace", workspace)

# prepare mj
analysis="an1"
mj="mj1"
python_script="s.py"
pipeline_name="Pipeline_5"
err = MjPreparation.prepare(workspace=workspace, analysis=analysis, mj=mj,
                            python_script=python_script, pipeline_name=pipeline_name)
if len(err) > 0:
    for e in err:
        print(e)
    os.exit()

# mj_config_dir
mj_config_dir = os.path.join(workspace, analysis, "mj", mj, "mj_config")


# job_service executable
job_service = {"__class__": "Executable",
               "name": "job_service",
               "path": "JobPanel/services/job_service.py",
               "script": True}

# flow123d executable
flow123d = {"__class__": "Executable",
            "name": "flow123d",
            "path": "/home/radek/work/Flow123d-2.1.0-linux-install/bin/flow123d.sh"}

# environment
env = {"__class__": "Environment",
       "geomop_root": os.path.abspath("../../src"),
       "geomop_analysis_workspace": os.path.abspath(workspace),
       "executables": [job_service, flow123d],
       "python": "python3"}

# local connection
cl = {"__class__": "ConnectionLocal",
      "address": "localhost",
      "environment": env,
      "name": "localhost"}

# local service
local_service = ServiceBase({"service_host_connection": cl})
threading.Thread(target=local_service.run, daemon=True).start()

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
                "workspace": "an1/mj/mj1/mj_config",
                "config_file_name": "mj_service.conf",
                "pipeline": {"python_script": python_script,
                             "pipeline_name": pipeline_name},
                "job_service_data": job_service_data}

# start multi job
child_id = local_service.request_start_child(service_data)
multi_job = local_service._child_services[child_id]

# wait for multi job done
while multi_job._status != ServiceStatus.done:
    time.sleep(1)

# stopping, closing
local_service._closing = True
