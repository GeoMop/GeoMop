from .service_base import ServiceStatus

import time

class ServiceProxy:
    """
    Automatic proxy class, provides methods to call 'request_XYZ' methods of
    the class passed as parameter of constructor. Further own thread is created
    (or reused) for every such call (this can be possibly optimized for simple requests in future).
    Returned data are stored in the variable of the name 'answer_XYZ'
    """
    def __init__(self, repeater, service_data, connection):
        self.repeater = repeater
        """ Object for communication with remote service."""
        self.service = service_data
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


        # smazat
        return

        if (self.service.status != None):
            # reinit, download port, status, etc. from remote file using delegator
            self.connect_service(self, self.service.listening_port)

    def call(self, method_name, data, result):
        """
        Call 'method_name(data)' of the remote service returned result is appended
        to the result.
        :param method_name: Name of method to call.
        :param data: Serializable (JSONData) passed to the method.
        :param result: List of results.
        :return:
        """
        pass

    def get(self, variable_name):
        self.call("request_get", variable_name, self.__dict__[variable_name])

    def stop(self):
        self.call("stop", None, )

    def start_service(self):
        """
        Process of starrting a Job
        1. # have service configuration data (from constructor)
        2. # get connection parameter - (in constructor)
        3. upload job files (specified in service_data, using the connection, upload config file
        4. get delegator proxy from connection
        5. setup remote port forwarding for the starter port (get it from repeater)

        6. repeater.expected_answer ... Sort of implicit request, we expect that ClientDispatcher
           form an answer when child service connection is accepted and we recieve its listenning port.
           We set that connect_service should be called `on_answer`.

        7. submit (or start) job through delegator
        8. set  Job state as 'queued'
        ...
        Job process:
        - read Job configuration from cofig file (given as argument)
        - start calculation in separate thread
        - open and listen on final port RYY
        - connect back to the parent service
        - send port RYY, wait for OK
        - after OK, close starting connection
        """

        # 4.
        delegator = self.connection.get_delegator()


    def connect_service(self, child_id):
        """
        Assumes Job is running and listening on given remote port. (we get port either throuhg initial socket
        connection or by reading the remote config file - reinit part of __init__)

        1. Check if repeater.client[child_id] have target port (ClientDispatcher exists)
        2. If No or child_id == None, download service config file and get port from there ( ... postpone)
        3. Open forward tunnel
        4. Call repeater.client[id].connect(port)
           self.repeater._connect_child_repeater(socket_address)
        5. set Job state to running
        """

        # 1.
        # if self.repeater.clients[child_id] is None:
        #     return

        # 3.
        # moved to _ClientDispatcher.set_remote_address()

        # 4.

        # 5.
        # for i in range(10):
        #     time.sleep(0.1)
        #     if self.repeater.is_child_connected(child_id):
        #         self.status = ServiceStatus.running
        #         break

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