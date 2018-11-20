from JobPanel.backend.service_base import ServiceBase, LongRequest, ServiceStatus
from JobPanel.backend.service_proxy import ServiceProxy
from JobPanel.backend.connection import *

import time
import threading
import os
import logging
import shutil
import pytest


logging.basicConfig(filename='test_service_proxy.log', filemode='w', level=logging.INFO)


this_source_dir = os.path.dirname(os.path.realpath(__file__))
geomop_root_local = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(this_source_dir))), "src")

TEST_FILES = "test_files"


@pytest.mark.slow
def test_serialize_proxy(request):
    local_service = None
    local_service_thread = None
    new_local_service = None
    new_local_service_thread = None

    def finalizer():
        # stopping, closing
        if local_service_thread is not None:
            local_service._closing = True
            local_service_thread.join(timeout=5)
            assert not local_service_thread.is_alive()

        if new_local_service_thread is not None:
            new_local_service._closing = True
            new_local_service_thread.join(timeout=5)
            assert not new_local_service_thread.is_alive()

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
    test_service_proxy = local_service._child_services[1]

    # wait for test service running
    time.sleep(5)
    assert test_service_proxy._status == ServiceStatus.running

    # serialize proxy
    serialized_proxy = test_service_proxy.serialize()

    # stop local service
    local_service._closing = True
    local_service_thread.join(timeout=5)
    assert not local_service_thread.is_alive()

    # new local service
    new_local_service = ServiceBase({"service_host_connection": cl})
    new_local_service_thread = threading.Thread(target=new_local_service.run, daemon=True)
    new_local_service_thread.start()

    # deserialize proxy
    del serialized_proxy["__class__"]
    test_service_proxy = ServiceProxy(serialized_proxy)
    con = new_local_service.get_connection(service_data["service_host_connection"])
    test_service_proxy.set_rep_con(new_local_service._repeater, con)
    test_service_proxy.connect_service()
    new_local_service._child_services[1] = test_service_proxy

    # check if test service running
    time.sleep(5)
    assert test_service_proxy._status == ServiceStatus.running
    assert test_service_proxy._online

    # stop test service
    answer = []
    test_service_proxy.call("request_stop", None, answer)
    time.sleep(5)
    #assert len(answer) > 0
