from JobPanel.backend.service_base import ServiceBase, LongRequest, ServiceStatus
from JobPanel.backend.service_proxy import ServiceProxy
from JobPanel.backend.connection import *
from .t_service import TService

import time
import threading
import os
import logging
import shutil
import pytest


logging.basicConfig(filename='test_service_base.log', filemode='w', level=logging.INFO)


this_source_dir = os.path.dirname(os.path.realpath(__file__))
geomop_root_local = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(this_source_dir))), "src")

TEST_FILES = "test_files"


def test_request_local():
    test_service = TService({})

    # long request
    answer = []
    test_service.call("request_long", None, answer)
    time.sleep(1)
    assert len(answer) == 0
    time.sleep(2)
    assert "data" in answer[0]

    # error request
    answer = []
    test_service.call("request_error", None, answer)
    assert "error" in answer[0]


@pytest.mark.slow
def test_request_remote(request):
    local_service = None
    local_service_thread = None

    def finalizer():
        # stopping, closing
        if local_service_thread is not None:
            local_service._closing = True
            local_service_thread.join(timeout=5)
            assert not local_service_thread.is_alive()

        shutil.rmtree(TEST_FILES, ignore_errors=True)
    request.addfinalizer(finalizer)

    # create analysis workspace
    os.makedirs(os.path.join(TEST_FILES, "workspace"), exist_ok=True)

    # local service
    env = {"__class__": "Environment",
           "geomop_root": geomop_root_local,
           "geomop_analysis_workspace": os.path.abspath(os.path.join(TEST_FILES, "workspace")),
           "python": "python3"}
    cl = {"__class__": "ConnectionLocal",
          "address": "localhost",
          "environment": env,
          "name": "local"}
    local_service = ServiceBase({"service_host_connection": cl})
    local_service_thread = threading.Thread(target=local_service.run, daemon=True)
    local_service_thread.start()

    # test service data
    pe = {"__class__": "ProcessExec",
          "executable": {"__class__": "Executable",
                         "path": os.path.join(this_source_dir, "t_service.py"),
                         "script": True}}
    service_data = {"service_host_connection": cl,
                    "process": pe,
                    "workspace": "",
                    "config_file_name": "t_service.conf"}

    # start test service
    local_service.request_start_child(service_data)
    test_service = local_service._child_services[1]

    # wait for test service running
    time.sleep(10)
    assert test_service._status == ServiceStatus.running

    # long request
    answer = []
    test_service.call("request_long", None, answer)
    time.sleep(1)
    assert len(answer) == 0
    time.sleep(7)
    assert "data" in answer[0]

    # error request
    answer = []
    test_service.call("request_error", None, answer)
    time.sleep(5)
    assert "error" in answer[0]

    # stop test service
    answer = []
    test_service.call("request_stop", None, answer)
    time.sleep(5)
    #assert len(answer) > 0
