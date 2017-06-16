from .service_base import ServiceBase, ServiceStatus, call_action

import time
import logging

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

        self.status=None
        """ ServiceStatus enum"""
        self.connected=False
        """ True if remote service is connected. Is it necessary?? """
        self.changing_status=False
        """ True if a status change action is processed: stopping"""

        self._child_id = None
        """Child id"""
        self.child_service_process_id = []
        """Child service process id"""

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
            if 'error' in answer.keys():
                self.error_answer(answer_data)
            call_action(self, on_answer['action'], (on_answer['data'], answer['data']))

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

        # 1.
        # todo: upload config file and possible other files according to service configuration,
        # see key 'input_files'

        # 2.
        delegator_proxy = self.connection.get_delegator()

        # 3.
        self._child_id, remote_port = self.repeater.add_child(self.connection)

        # 4.
        # process_config = {"__class__": "ProcessExec", "executable" : {"__class__": "Executable", "name": "sleep"},
        #                    "exec_args": {"__class__": "ExecArgs", "args": ["60"]}}
        process_config = self.service_data["process"]

        # todo: v budoucnu predavat konfiguraci v souboru
        process_config["exec_args"] = {"__class__": "ExecArgs", "args": [str(self._child_id), "172.17.42.1", str(remote_port)]}

        delegator_proxy.call("request_process_start", process_config, self.child_service_process_id)

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

        # 1.
        self.repeater.clients[self._child_id]


    def get(self, variable_name):
        self.call("request_get", variable_name, self.__dict__[variable_name])

    def stop(self):
        self.call("stop", None, )



    def on_answer_connect(self, data=None):
        self.status = ServiceStatus.running



    def make_ping(self):
        self.service.repeater.send_request(
            target=[self.child_id],
            data={'action': 'ping'},
            on_answer={'action': 'on_answer_ok'})

    def on_answer_no_error(self, data):
        pass

    def on_answer_ok(self, data):
        answer_data=data[1]
        logging.info(str(answer_data))
        logging.info("answer: OK")
        pass

    def error_answer(self, data):
        """
        Called if the answer reports an error.
        :param data:
        :return:
        """
        #answer_data =
        pass


"""
Use class factory to make proxy classes to Service classes.
"""
def class_factory(name, service=None):
    """
    service: class to which we creat a proxy
    Function used for creating subclasses of class Shape
    """

    def __init__(self, service_data):
        super(self.__class__, self).__init__(service_data)

    class_dict = {"__init__": __init__}

    # just scatch
    for  (func_name, func) in service.__dict__.items():
        if is_request_method(func_name):
            def new_func(self, json_data, result_list):
                self.call("%s"%(func_name), json_data, result_list)

            class_dict[func_name] = new_func
    return type(name, (ServiceProxy,), class_dict)