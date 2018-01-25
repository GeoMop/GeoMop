from backend.service_base import ServiceBase, LongRequest, ServiceStatus
from backend.service_proxy import ServiceProxy
from backend.connection import *

import time
import threading
import os
import logging
import shutil


logging.basicConfig(filename='test_service_proxy.log', filemode='w', level=logging.INFO)


TEST_FILES = "test_files"


def test_serialize_proxy(request):
    def clear_test_files():
        shutil.rmtree(TEST_FILES, ignore_errors=True)
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
          "environment": env,
          "name": "local"}
    local_service = ServiceBase({"service_host_connection": cl})
    t = threading.Thread(target=local_service.run, daemon=True)
    t.start()

    # test service data
    pe = {"__class__": "ProcessExec",
          "executable": {"__class__": "Executable",
                         "path": "../testing/JobPanel/backend/t_service.py",
                         "script": True}}
    service_data = {"service_host_connection": cl,
                    "process": pe,
                    "workspace": "",
                    "config_file_name": "t_service.conf"}

    # start test service
    local_service.request_start_child(service_data)
    test_service_proxy = local_service._child_services[1]

    # wait for test service running
    time.sleep(5)
    assert test_service_proxy._status == ServiceStatus.running

    # serialize proxy
    serialized_proxy = test_service_proxy.serialize()

    # stop local service
    local_service._closing = True
    t.join(timeout=5)
    assert not t.is_alive()

    # new local service
    local_service = ServiceBase({"service_host_connection": cl})
    t = threading.Thread(target=local_service.run, daemon=True)
    t.start()

    # deserialize proxy
    del serialized_proxy["__class__"]
    test_service_proxy = ServiceProxy(serialized_proxy)
    con = local_service.get_connection(service_data["service_host_connection"])
    test_service_proxy.set_rep_con(local_service._repeater, con)
    test_service_proxy.connect_service()
    local_service._child_services[1] = test_service_proxy

    # check if test service running
    time.sleep(5)
    assert test_service_proxy._status == ServiceStatus.running
    assert test_service_proxy._online

    # stop test service
    answer = []
    test_service_proxy.call("request_stop", None, answer)
    time.sleep(5)
    #assert len(answer) > 0

    # stopping, closing
    local_service._closing = True
