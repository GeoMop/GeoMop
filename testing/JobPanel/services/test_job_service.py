from JobPanel.backend.service_base import ServiceBase, ServiceStatus
from testing.JobPanel.mock.passwords import get_test_password
from .port_forwarder import PortForwarder

import threading
import os
import shutil
import time
import logging
import pytest

logging.basicConfig(filename='test_job_service.log', filemode='w', level=logging.INFO)


TEST_FILES = "test_files"
REMOTE_WORKSPACE = "/home/test/workspace"

@pytest.mark.slow
def test_correct_run(request):
    def clear_test_files():
        shutil.rmtree(TEST_FILES, ignore_errors=True)
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
          "environment": env,
          "name": "local"}
    local_service = ServiceBase({"service_host_connection": cl})
    threading.Thread(target=local_service.run, daemon=True).start()

    # job data
    pe = {"__class__": "ProcessExec",
          "executable": {"__class__": "Executable",
                         "path": "JobPanel/services/_job_service.py",
                         "script": True}}
    je = {"__class__": "Executable",
          "path": "../testing/JobPanel/services/job_1.py",
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

    # check correct job state transition
    time.sleep(5)
    assert job._status == ServiceStatus.queued
    time.sleep(15)
    assert job._status == ServiceStatus.running
    time.sleep(15)
    assert job._status == ServiceStatus.done

    # stopping, closing
    local_service._closing = True


def test_correct_run_connection_fail(request):
    def clear_test_files():
        shutil.rmtree(TEST_FILES, ignore_errors=True)
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
          "environment": env,
          "name": "local"}
    local_service = ServiceBase({"service_host_connection": cl})
    threading.Thread(target=local_service.run, daemon=True).start()

    # port forwarder
    port_forwarder = PortForwarder()
    forwarded_port = port_forwarder.forward_port(22)

    # job data
    env_rem = {"__class__": "Environment",
               "geomop_root": os.path.abspath("../src"),
               "geomop_analysis_workspace": REMOTE_WORKSPACE,
               "python": "python3"}
    u, p = get_test_password()
    cr = {"__class__": "ConnectionSSH",
          "address": "localhost",
          "port": forwarded_port,
          "uid": u,
          "password": p,
          "environment": env_rem,
          "name": "remote"}
    pe = {"__class__": "ProcessExec",
          "executable": {"__class__": "Executable",
                         "path": "JobPanel/services/_job_service.py",
                         "script": True}}
    je = {"__class__": "Executable",
          "path": "../testing/JobPanel/services/job_1.py",
          "script": True}
    service_data = {"service_host_connection": cr,
                    "process": pe,
                    "job_executable": je,
                    "workspace": "job",
                    "config_file_name": "job_service.conf",
                    "wait_before_run": 15.0}

    # start job
    local_service.request_start_child(service_data)
    #print(local_service._child_services.keys())
    job = local_service._child_services[2]

    # check correct job state transition
    time.sleep(5)
    port_forwarder.discard_data = True
    time.sleep(5)
    port_forwarder.discard_data = False
    time.sleep(10)
    assert job._status == ServiceStatus.running
    time.sleep(5)
    port_forwarder.discard_data = True
    time.sleep(5)
    port_forwarder.discard_data = False
    time.sleep(5)
    assert job._status == ServiceStatus.running
    assert job._online
    time.sleep(10)
    assert job._status == ServiceStatus.done

    # stopping, closing
    port_forwarder.close_all_forwarded_ports()
    local_service._closing = True
