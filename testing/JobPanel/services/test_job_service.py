from backend.service_base import ServiceBase, ServiceStatus
#from ..backend.test_connection import get_test_password

import threading
import os
import shutil
import time
import logging


logging.basicConfig(filename='test_job_service.log', filemode='w', level=logging.INFO)


TEST_FILES = "test_files"
REMOTE_WORKSPACE = "/home/test/workspace"


def xxx_test_correct_run(request):
    def clear_test_files():
        #shutil.rmtree(TEST_FILES, ignore_errors=True)
        pass
    request.addfinalizer(clear_test_files)

    # create analysis and job workspaces
    os.makedirs(os.path.join(TEST_FILES, "workspace/job"), exist_ok=True)

    # local service
    env = {"__class__": "Environment",
           "geomop_root": os.path.abspath("../src"),
           "geomop_analysis_workspace": os.path.abspath(os.path.join(TEST_FILES, "workspace")),
           "python": "python3"}
    cl = {"__class__": "ConnectionLocal",
          "address": "localhost",
          "environment": env}
    local_service = ServiceBase({"service_host_connection": cl})
    threading.Thread(target=local_service.run, daemon=True).start()

    # job data
    pe = {"__class__": "ProcessExec",
          "executable": {"__class__": "Executable",
                         "path": "JobPanel/services",
                         "name": "_job_service.py",
                         "script": True},
          "environment": env}
    je = {"__class__": "Executable",
          "path": "../testing/JobPanel/services",
          "name": "job_1.py",
          "script": True}
    service_data = {"service_host_connection": cl,
                    "process": pe,
                    "job_executable": je,
                    "workspace": "job",
                    "config_file_name": "job_service.conf",
                    "wait_before_run": 10.0}

    # start job
    local_service.request_start_child(service_data)
    job = local_service._child_services[1]

    # wait for job queued
    for i in range(4):
        time.sleep(1)
        job.get_status()
    time.sleep(1)
    assert job.get_status() == ServiceStatus.queued

    # wait for job running
    for i in range(9):
        time.sleep(1)
        job.get_status()
    time.sleep(1)
    assert job.get_status() == ServiceStatus.running

    # wait for job done
    for i in range(9):
        time.sleep(1)
        job.get_status()
    time.sleep(1)
    assert job.get_status() == ServiceStatus.done

    # stopping, closing
    local_service._closing = True


def test_correct_run_connection_fail(request):
    def clear_test_files():
        #shutil.rmtree(TEST_FILES, ignore_errors=True)
        pass
    request.addfinalizer(clear_test_files)

    # create analysis and job workspaces
    os.makedirs(os.path.join(TEST_FILES, "workspace/job"), exist_ok=True)

    # local service
    env = {"__class__": "Environment",
           "geomop_root": os.path.abspath("../src"),
           "geomop_analysis_workspace": os.path.abspath(os.path.join(TEST_FILES, "workspace")),
           "python": "python3"}
    cl = {"__class__": "ConnectionLocal",
          "address": "localhost",
          "environment": env}
    local_service = ServiceBase({"service_host_connection": cl})
    threading.Thread(target=local_service.run, daemon=True).start()

    # job data
    env_rem = {"__class__": "Environment",
               "geomop_root": os.path.abspath("../src"),
               "geomop_analysis_workspace": REMOTE_WORKSPACE,
               "python": "python3"}
    #u, p = get_test_password()
    u, p = "test", ""
    cr = {"__class__": "ConnectionSSH",
          "address": "localhost",
          "uid": u,
          "password": p,
          "environment": env_rem}
    pe = {"__class__": "ProcessExec",
          "executable": {"__class__": "Executable",
                         "path": "JobPanel/services",
                         "name": "_job_service.py",
                         "script": True},
          "environment": env_rem}
    je = {"__class__": "Executable",
          "path": "../testing/JobPanel/services",
          "name": "job_1.py",
          "script": True}
    service_data = {"service_host_connection": cr,
                    "process": pe,
                    "job_executable": je,
                    "workspace": "job",
                    "config_file_name": "job_service.conf",
                    "wait_before_run": 10.0}

    # start job
    local_service.request_start_child(service_data)
    #print(local_service._child_services.keys())
    job = local_service._child_services[2]

    time.sleep(20)
    assert False

    # wait for job queued
    for i in range(4):
        time.sleep(1)
        job.get_status()
    time.sleep(1)
    assert job.get_status() == ServiceStatus.queued

    # wait for job running
    for i in range(9):
        time.sleep(1)
        job.get_status()
    time.sleep(1)
    assert job.get_status() == ServiceStatus.running

    # wait for job done
    for i in range(9):
        time.sleep(1)
        job.get_status()
    time.sleep(1)
    assert job.get_status() == ServiceStatus.done

    # stopping, closing
    local_service._closing = True
