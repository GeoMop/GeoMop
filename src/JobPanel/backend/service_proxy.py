from .service_base import ServiceBase, ServiceStatus, call_action
from .connection import ConnectionStatus, SSHError

import time
import logging
import os
import json


class ServiceProxy:
    """
    Automatic proxy class, provides methods to call 'request_XYZ' methods of
    the class passed as parameter of constructor. Further own thread is created
    (or reused) for every such call (this can be possibly optimized for simple requests in future).
    Returned data are stored in the variable of the name 'answer_XYZ'


        Auxiliary class to store state of a child service.

    Can keep status, near history, downloaded data, etc.
    Implements simple request

    TODO, idea:
    This is key class, it should define classes for all actions with MJs. These remote actions are only of two kinds:
    1. Make something on remote and confirm success on client or report an error.
    2. Update some state variables of the proxy.

    This can be called in async way and should be ok for GUI.
    Actions are mentioned in client_test.py.
    Would be nice if we can make methods corresponding to remote actions using metaprograming .. can be done using __getattr__

    def __getattr__(name):
        func = ServiceClass.getattr(name)
        assert( func and func is decorated as remote )
        def wrapper(*karg):
            repeater.send_request({'action': name, 'data': *karg})
        return wrapper


    - how to get parameters
    - use  unpack **dict when calling actions


    """
    def __init__(self, service_data, repeater, connection):
        self.repeater = repeater
        """ Object for communication with remote service."""
        self.service_data = service_data
        """
        JSON data used to initialize the service. ?? Should it contain also data of the proxy??
        Proxy data:
        - service listenning port (necessary)
        - service files, service status, ... (convenient)
        """
        self.connection = connection
        self.connection_id = connection._id

        self.status=None
        """ ServiceStatus enum"""
        self.connected=False
        """ True if remote service is connected. Is it necessary?? """
        self.changing_status=False
        """ True if a status change action is processed: stopping"""

        self._child_id = None
        """Child id"""

        # Result lists
        self.results_process_start = []
        """Child service process id save as result list"""
        self.results_get_status = []
        """List of result list of get status request"""

        self.last_time = time.time()
        """Last time we had info from service"""
        self.online = False
        """We are connected to service"""
        self.downloaded_config = None
        """Config downloaded from service config file"""

        #TODO:
        #  smazat
        return

        if (self.service.status != None):
            # reinit, download port, status, etc. from remote file using delegator
            self.connect_service(self, self.service.listening_port)

    def call(self, method_name, data, result):
        """
        Call 'method_name(data)' of the remote service returned result is appended
        to the result which has to be a list.

        TODO: If necessary implement alternative method which calls a given answer processing once the  answer is received.
        TODO: How we process errors. !!!!


        :param method_name: Name of method to call.
        :param data: Serializable (JSONData) passed to the method.
        :param result: List of results.
        :return: None, error.
        """
        self.repeater.send_request([self._child_id], {'action': method_name, 'data': data}, {'action': 'save_result', 'data': result})

    def _process_answers(self):
        for answer_data in self.repeater.get_answers(self._child_id):
            logging.info("Processing: " + str(answer_data))
            #child_id = answer_data.sender[0]
            on_answer = answer_data.on_answer
            answer = answer_data.answer
            # if 'error' in answer.keys():
            #     self.error_answer(answer_data)
            call_action(self, on_answer['action'], (on_answer['data'], answer))

    def save_result(self, answer_data):
        """
        Method for saving answered data.
        :param answer_data: must be in this format: (result_list, result_data)
        :return:
        """
        (result_list, result_data) = answer_data
        result_list.append(result_data)

    def start_service(self):
        """
        Process of starting a Job:
        0. # have repeater, connection, and service configuration data (from constructor)
        1. upload job files (specified in service_data, using the connection, upload config file).
           Have to upload config data serialized to a JSON file, so that the child service may start even if
           the parent service is not running or is not accessible (e.g. MJ or Job started over PBS)
        2. get delegator proxy from connection
        3. repeater.add_child, store child_ID, ( it also returns remote forwarded local port, seems we doesn't need it.
        4. delegator_proxy.call( "request_process_start", process_config, self.child_service_process_id )
           Need to prepare process_config, self.child_service_process_id=[]
        5. set  Job state as 'queued'

        ...
        Job process:
        - read Job configuration from cofig file (given as argument)
        - start calculation in separate thread
        - open and listen on final port RYY
        - connect back to the parent service
        - send port RYY, wait for OK
        - after OK, close starting connection


        TODO:
        -
        """

        # 2.
        delegator_proxy = self.connection.get_delegator()

        # 3.
        self._child_id, remote_port = self.repeater.add_child(self.connection)

        # update service data, remove password
        self.service_data = self.service_data.copy()
        self.service_data["repeater_address"] = [self._child_id]
        self.service_data["parent_address"] = [self.service_data["service_host_connection"]["address"], remote_port]

        self.service_data["service_host_connection"] = self.service_data["service_host_connection"].copy()
        self.service_data["service_host_connection"]["password"] = ""

        self.service_data["process"] = self.service_data["process"].copy()
        if "exec_args" in self.service_data["process"]:
            self.service_data["process"]["exec_args"] = self.service_data["process"]["exec_args"].copy()
        else:
            self.service_data["process"]["exec_args"] = {"__class__": "ExecArgs"}
        self.service_data["process"]["exec_args"]["work_dir"] = self.service_data["workspace"]

        if "environment" in self.service_data["process"]:
            logging.warning("Start service: Overwriting environment in service_data['process'].")
        self.service_data["process"]["environment"] = self.service_data["service_host_connection"]["environment"]

        self.service_data["status"] = "queued"

        # save config file
        file = os.path.join(
            self.connection._local_service.service_host_connection.environment.geomop_analysis_workspace,
            self.service_data["workspace"],
            self.service_data["config_file_name"])
        with open(file, 'w') as fd:
            json.dump(self.service_data, fd, indent=4, sort_keys=True)

        # 1.
        files = []
        if "input_files" in self.service_data:
            for file in self.service_data["input_files"]:
                files.append(os.path.join(self.service_data["workspace"], file))
        files.append(os.path.join(self.service_data["workspace"], self.service_data["config_file_name"]))
        self.connection.upload(files,
                               self.connection._local_service.service_host_connection.environment.geomop_analysis_workspace,
                               self.connection.environment.geomop_analysis_workspace)

        # 4.
        process_config = self.service_data["process"]
        delegator_proxy.call("request_process_start", process_config, self.results_process_start)

        # 5.
        self.status = ServiceStatus.queued

        return self._child_id


    def get_status(self):
    #def connect_service(self, child_id):
        """
        Update service status according to state info in repeater,
        and least received status info, and
        send request to get new status.

        Assumes Job is running and listening on given remote port. (we get port either throuhg initial socket
        connection or by reading the remote config file - reinit part of __init__)

        Nasledujici body jiz neplati.
        1. Check if repeater.client[child_id] have target port (ClientDispatcher exists)
        2. If No or child_id == None, download service config file and get port from there ( ... postpone)
        3. Open forward tunnel
        4. Call repeater.client[id].connect(port)
           self.repeater._connect_child_repeater(socket_address)
        5. set Job state to running
        """

        #TODO:
        # if status == queued:
        #       check in repeater if child is connected, then set status to running, write the listenning port to the status file
        #       otherwise run in separate thread downloading of the service status file through delegator
        # if status == running:
        #       send request get status

        # if status == runnign and no answer for last request:
        #       run in separate thread downloading of the service status file through delegator

        # return current status

        # 1.
        #self.repeater.clients[self._child_id]

        if self.online:
            # check get status result
            self.results_get_status = self.results_get_status[-5:]
            res = None
            for item in reversed(self.results_get_status):
                if len(item) > 0:
                    res = item[0]
                    break
            if (res is None and len(self.results_get_status) >= 5) or (res is not None and "error" in res):
                self.online = False
            else:
                if res is not None:
                    self.status = res["data"]
                    self.last_time = time.time()

                # request get status
                result = []
                self.call("request_get_status", None, result)
                self.results_get_status.append(result)
        elif self.status == ServiceStatus.queued or self.status == ServiceStatus.running:
            if time.time() > self.last_time + 1:
                if self.download_config():
                    self.status = ServiceStatus[self.downloaded_config["status"]]
                    if self.status == ServiceStatus.running:
                        disp = self.repeater.clients[self._child_id]
                        if disp._remote_address is None:
                            disp.set_remote_address(self.downloaded_config["listen_address"])
                        else:
                            self.repeater.reconnect_child(self._child_id)
                self.last_time = time.time()
        return self.status

    def download_config(self):
        if self.connection._status != ConnectionStatus.online:
            return False
        try:
            self.connection.download(
                [os.path.join(self.service_data["workspace"], self.service_data["config_file_name"])],
                self.connection._local_service.service_host_connection.environment.geomop_analysis_workspace,
                self.connection.environment.geomop_analysis_workspace)
        except (SSHError, FileNotFoundError, PermissionError):
            return False
        file = os.path.join(
            self.connection._local_service.service_host_connection.environment.geomop_analysis_workspace,
            self.service_data["workspace"],
            self.service_data["config_file_name"])
        try:
            with open(file, 'r') as fd:
                try:
                    self.downloaded_config = json.load(fd)
                except ValueError:
                    return False
        except OSError:
            return False
        return True

    # def get(self, variable_name):
    #     self.call("request_get", variable_name, self.__dict__[variable_name])

    def stop(self):
        self.call("stop", None, )



    def on_answer_connect(self, data=None):
        self.status = ServiceStatus.running
        self.online = True
        self.results_get_status.clear()
        self.last_time = time.time()

    def close(self):
        self.repeater.remove_child(self._child_id)



    # def make_ping(self):
    #     self.service.repeater.send_request(
    #         target=[self.child_id],
    #         data={'action': 'ping'},
    #         on_answer={'action': 'on_answer_ok'})
    #
    # def on_answer_no_error(self, data):
    #     pass
    #
    # def on_answer_ok(self, data):
    #     answer_data=data[1]
    #     logging.info(str(answer_data))
    #     logging.info("answer: OK")
    #     pass

    def error_answer(self, data):
        """
        Called if the answer reports an error.
        :param data:
        :return:
        """
        #answer_data =
        pass


class DelegatorProxy(ServiceProxy):
    def get_status(self):
        super().get_status()
        if self.status == ServiceStatus.running and not self.online:
            self.status = ServiceStatus.done
        return self.status

    def download_config(self):
        return False


# """
# Use class factory to make proxy classes to Service classes.
# """
# def class_factory(name, service=None):
#     """
#     service: class to which we creat a proxy
#     Function used for creating subclasses of class Shape
#     """
#
#     def __init__(self, service_data):
#         super(self.__class__, self).__init__(service_data)
#
#     class_dict = {"__init__": __init__}
#
#     # just scatch
#     for  (func_name, func) in service.__dict__.items():
#         if is_request_method(func_name):
#             def new_func(self, json_data, result_list):
#                 self.call("%s"%(func_name), json_data, result_list)
#
#             class_dict[func_name] = new_func
#     return type(name, (ServiceProxy,), class_dict)