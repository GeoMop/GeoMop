from backend.service_base import ServiceBase, LongRequest, ServiceStatus
from backend.service_proxy import ServiceProxy
from backend.connection import *
from t_service import TService

import time
import threading
import os
import logging


logging.basicConfig(filename='test_service_base.log', filemode='w', level=logging.INFO)


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


def test_request_remote():
    # local service
    local_service = ServiceBase({})
    threading.Thread(target=local_service.run, daemon=True).start()

    # test service data
    env = {"__class__": "Environment",
           "geomop_root": os.path.abspath("../src"),
           "python": "python3"}
    pd = {"__class__": "ProcessExec",
          "executable": {"__class__": "Executable",
                         "path": "../testing/JobPanel/backend",
                         "name": "t_service.py",
                         "script": True},
          "exec_args": {"__class__": "ExecArgs",
                        "args": ["1", "localhost", str(local_service._repeater._starter_server.address[1])]},
          "environment": env}
    cl = {"__class__": "ConnectionLocal",
          "address": "localhost"}
    service_data = {"service_host_connection": cl,
                    "process": pd}

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
