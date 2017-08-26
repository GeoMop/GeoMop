from backend.service_base import ServiceBase, LongRequest, ServiceStatus
from backend.service_proxy import ServiceProxy
from backend.connection import *
from t_service import TService

import time
import threading
import os
import logging


logging.basicConfig(filename='test_service_base.log', filemode='w', level=logging.INFO)


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


def test_request_remote(request):
    def clear_test_files():
        #shutil.rmtree(TEST_FILES, ignore_errors=True)
        pass
    request.addfinalizer(clear_test_files)

    # create analysis workspace
    os.makedirs(os.path.join(TEST_FILES, "workspace"), exist_ok=True)

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

    # test service data
    pe = {"__class__": "ProcessExec",
          "executable": {"__class__": "Executable",
                         "path": "../testing/JobPanel/backend",
                         "name": "t_service.py",
                         "script": True}}
    service_data = {"service_host_connection": cl,
                    "process": pe,
                    "workspace": "",
                    "config_file_name": "t_service.conf"}

    # start test service
    local_service.request_start_child(service_data)
    test_service = local_service._child_services[1]

    # wait for test service running
    time.sleep(5)
    assert test_service.status == ServiceStatus.running

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
    assert len(answer) > 0

    # stopping, closing
    local_service._closing = True
