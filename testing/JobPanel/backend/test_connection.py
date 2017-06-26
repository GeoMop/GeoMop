# prerequisites for this tests:
# 1: on machine must be user "test" with ssh keys set for user which runs tests (or password in secret file)
# 2: directory "/home/test/test_dir" must be writable for user which runs tests


from backend.connection import *
from backend.service_base import ServiceBase, ServiceStatus
from backend.service_proxy import ServiceProxy

import threading
import socket
import socketserver
import os
import shutil
import logging
import time


#logging.basicConfig(filename='test_connection.log', filemode='w', level=logging.INFO)


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


def get_test_password():
    u = "test"
    p = ""
    d = get_passwords()
    if "test" in d:
        u = d["test"][0]
        p = d["test"][1]
    return u, p


REMOTE_WORKSPACE = "/home/test/workspace"


def test_port_forwarding():
    class Server(socketserver.ThreadingTCPServer):
        daemon_threads = True
        allow_reuse_address = True

    class RequestHandler(socketserver.BaseRequestHandler):
        def handle(self):
            data = str(self.request.recv(1024), 'ascii')
            if data == "hello":
                self.request.sendall(bytes("hello", 'ascii'))

    def connection_test(ip, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        try:
            sock.sendall(bytes("hello", 'ascii'))
            response = str(sock.recv(1024), 'ascii')
            if response == "hello":
                return True
        finally:
            sock.close()
        return False

    server = Server(('', 0), RequestHandler)
    ip, origin_port = server.server_address

    # start server in thread
    t = threading.Thread(target=server.serve_forever)
    t.daemon = True
    t.start()

    # ConnectionLocal
    con = ConnectionLocal()
    con.connect()

    forwarded_port = con.forward_local_port(origin_port)
    assert connection_test("localhost", forwarded_port)

    forwarded_port = con.forward_remote_port(origin_port)
    assert connection_test("localhost", forwarded_port)

    con.close_connections()

    # environment
    env = {"__class__": "Environment",
           "geomop_analysis_workspace": REMOTE_WORKSPACE}

    # ConnectionSSH
    u, p = get_test_password()
    con = ConnectionSSH({"address": "localhost", "uid": u, "password": p, "environment": env})
    con.connect()

    forwarded_port = con.forward_local_port(origin_port)
    assert connection_test("localhost", forwarded_port)

    forwarded_port = con.forward_remote_port(origin_port)
    assert connection_test("localhost", forwarded_port)

    con.close_connections()

    # shutdown server
    server.shutdown()
    server.server_close()


LOCAL_TEST_FILES = os.path.abspath("test_files")
REMOTE_TEST_FILES = "/home/test/test_dir/test_files"


def test_upload_download(request):
    def clear_test_files():
        shutil.rmtree(LOCAL_TEST_FILES, ignore_errors=True)
        shutil.rmtree(REMOTE_TEST_FILES, ignore_errors=True)
    request.addfinalizer(clear_test_files)

    files = ["f1.txt", "f2.txt"]

    def create_dir(path):
        shutil.rmtree(path, ignore_errors=True)
        os.makedirs(path)
        os.chmod(path, 0o777)

    def create_files(path):
        create_dir(path)
        for file in files:
            with open(os.path.join(path, file), 'w') as fd:
                fd.write(file)

    def check_files(path):
        for file in files:
            with open(os.path.join(path, file), 'r') as fd:
                assert fd.read() == file

    def remove_files(path):
        shutil.rmtree(path)

    # ConnectionLocal
    con = ConnectionLocal()
    con.connect()

    loc = os.path.join(LOCAL_TEST_FILES, "loc")
    rem = os.path.join(LOCAL_TEST_FILES, "rem")

    # upload
    create_files(loc)
    create_dir(rem)
    con.upload(files, loc, rem)
    check_files(rem)
    remove_files(loc)
    remove_files(rem)

    # download
    create_files(rem)
    create_dir(loc)
    con.download(files, loc, rem)
    check_files(loc)
    remove_files(loc)
    remove_files(rem)

    con.close_connections()

    # environment
    env = {"__class__": "Environment",
           "geomop_analysis_workspace": REMOTE_WORKSPACE}

    # ConnectionSSH
    u, p = get_test_password()
    con = ConnectionSSH({"address": "localhost", "uid": u, "password": p, "environment": env})
    con.connect()

    loc = os.path.join(LOCAL_TEST_FILES, "loc")
    rem = os.path.join(REMOTE_TEST_FILES, "rem")

    # upload
    create_files(loc)
    create_dir(rem)
    con.upload(files, loc, rem)
    check_files(rem)
    remove_files(loc)
    remove_files(rem)

    # download
    create_files(rem)
    create_dir(loc)
    con.download(files, loc, rem)
    check_files(loc)
    remove_files(loc)
    remove_files(rem)

    # FileNotFoundError
    try:
        con.upload(["x.txt"], loc, rem)
        assert False
    except FileNotFoundError:
        pass

    try:
        con.download(["x.txt"], loc, rem)
        assert False
    except FileNotFoundError:
        pass

    con.close_connections()


def test_exceptions():
    con = ConnectionSSH({"address": "localhost", "uid": "user_not_exist", "password": ""})
    try:
        con.connect()
        assert False
    except SSHAuthenticationError:
        pass

    con = ConnectionSSH({"address": "unknown_host", "uid": "user", "password": ""})
    try:
        con.connect()
        assert False
    except SSHAuthenticationError:
        assert False
    except SSHError:
        pass


def test_get_delegator():
    # local service
    local_service = ServiceBase({})
    local_service._repeater.run()

    # environment
    env = {"__class__": "Environment",
           "geomop_root": os.path.abspath("../src"),
           "geomop_analysis_workspace": REMOTE_WORKSPACE,
           "python": "python3"}

    # ConnectionSSH
    u, p = get_test_password()
    con = ConnectionSSH({"address": "localhost", "uid": u, "password": p, "environment":env})
    con.set_local_service(local_service)
    con.connect()

    # get_delegator
    delegator_proxy = con.get_delegator()
    assert isinstance(delegator_proxy, ServiceProxy)

    # stopping, closing
    local_service._repeater.close()
    con.close_connections()


def test_delegator_exec():
    # local service
    local_service = ServiceBase({})
    threading.Thread(target=local_service.run, daemon=True).start()

    # environment
    env = {"__class__": "Environment",
           "geomop_root": os.path.abspath("../src"),
           "geomop_analysis_workspace": REMOTE_WORKSPACE,
           "python": "python3"}

    # ConnectionSSH
    u, p = get_test_password()
    con = ConnectionSSH({"address": "localhost", "uid": u, "password": p, "environment":env})
    con.set_local_service(local_service)
    con.connect()

    # get_delegator
    delegator_proxy = con.get_delegator()
    assert isinstance(delegator_proxy, ServiceProxy)

    # start process
    process_config = {"__class__": "ProcessExec",
                      "executable": {"__class__": "Executable", "name": "sleep"},
                      "exec_args": {"__class__": "ExecArgs", "args": ["60"]}}
    answer = []
    delegator_proxy.call("request_process_start", process_config, answer)

    # wait for answer
    time.sleep(5)
    process_id = answer[-1]

    # get status
    process_config = {"__class__": "ProcessExec", "process_id": process_id}
    answer = []
    delegator_proxy.call("request_process_status", process_config, answer)

    # wait for answer
    time.sleep(5)
    assert answer[-1][process_id]["running"] is True

    # kill
    process_config = {"__class__": "ProcessExec", "process_id": process_id}
    answer = []
    delegator_proxy.call("request_process_kill", process_config, answer)

    # wait for answer
    time.sleep(5)
    assert answer[-1] is True

    # stopping, closing
    local_service._closing = True
    con.close_connections()


def test_docker():
    # local service
    local_service = ServiceBase({})
    threading.Thread(target=local_service.run, daemon=True).start()

    # service data
    env = {"__class__": "Environment",
           "geomop_root": os.path.abspath("../src"),
           "python": "python3"}
    pd = {"__class__": "ProcessDocker",
          "executable": {"__class__": "Executable",
                         "path": "JobPanel/services",
                         "name": "backend_service.py",
                         "script": True},
          "environment": env}
    cl = {"__class__": "ConnectionLocal",
          "address": "localhost"}
    service_data = {"service_host_connection": cl,
                    "process": pd}

    # start backend
    local_service.request_start_child(service_data)
    backend = local_service._child_services[1]

    # wait for backend running
    time.sleep(5)
    assert backend.status == ServiceStatus.running

    # stop backend
    answer = []
    backend.call("request_stop", None, answer)
    time.sleep(5)
    assert len(answer) > 0

    # stopping, closing
    local_service._closing = True


METACENTRUM_FRONTEND = "skirit.metacentrum.cz"
METACENTRUM_HOME = "/storage/brno2/home/"


def test_mc_get_delegator():
    # metacentrum credentials
    mc_u, mc_p = get_passwords()["metacentrum"]

    # local service
    local_service = ServiceBase({})
    local_service._repeater.run()

    # environment
    env = {"__class__": "Environment",
           "geomop_root": os.path.join(METACENTRUM_HOME, mc_u, "jenkins_test/GeoMop/src"),
           "python": os.path.join(METACENTRUM_HOME, mc_u, "jenkins_test/geomop_python.sh")}

    # ConnectionSSH
    con = ConnectionSSH({"address": METACENTRUM_FRONTEND, "uid": mc_u, "password": mc_p, "environment":env})
    con.set_local_service(local_service)
    con.connect()

    # get_delegator
    delegator_proxy = con.get_delegator()
    assert isinstance(delegator_proxy, ServiceProxy)

    # stopping, closing
    local_service._repeater.stop()
    con.close_connections()


def test_mc_delegator_pbs():
    # metacentrum credentials
    mc_u, mc_p = get_passwords()["metacentrum"]

    # local service
    local_service = ServiceBase({})
    threading.Thread(target=local_service.run, daemon=True).start()

    # environment
    env = {"__class__": "Environment",
           "geomop_root": os.path.join(METACENTRUM_HOME, mc_u, "jenkins_test/GeoMop/src"),
           "geomop_analysis_workspace": os.path.join(METACENTRUM_HOME, mc_u, "jenkins_test/workspace"),
           "python": os.path.join(METACENTRUM_HOME, mc_u, "jenkins_test/geomop_python.sh")}

    # ConnectionSSH
    con = ConnectionSSH({"address": METACENTRUM_FRONTEND, "uid": mc_u, "password": mc_p, "environment":env})
    con.set_local_service(local_service)
    con.connect()

    # get_delegator
    delegator_proxy = con.get_delegator()
    assert isinstance(delegator_proxy, ServiceProxy)

    # start process
    process_config = {"__class__": "ProcessPBS",
                      "executable": {"__class__": "Executable", "name": "sleep"},
                      "exec_args": {"__class__": "ExecArgs", "args": ["600"], "pbs_args": {"__class__": "PbsConfig", "dialect":{"__class__": "PbsDialectPBSPro"}}},
                      "environment": env}
    answer = []
    delegator_proxy.call("request_process_start", process_config, answer)

    # wait for answer
    def wait_for_answer(ans, t):
        for i in range(t):
            time.sleep(1)
            if len(ans) > 0:
                break

    wait_for_answer(answer, 60)
    process_id = answer[-1]

    # get status
    time.sleep(10)
    process_config = {"__class__": "ProcessPBS", "process_id": process_id}
    answer = []
    delegator_proxy.call("request_process_status", process_config, answer)

    # wait for answer
    wait_for_answer(answer, 60)
    status = answer[-1][process_id]["status"]
    assert status == ServiceStatus.queued or status == ServiceStatus.running

    # kill
    process_config = {"__class__": "ProcessPBS", "process_id": process_id}
    answer = []
    delegator_proxy.call("request_process_kill", process_config, answer)

    # wait for answer
    wait_for_answer(answer, 60)
    assert answer[-1] is True

    # stopping, closing
    local_service._closing = True
    con.close_connections()
