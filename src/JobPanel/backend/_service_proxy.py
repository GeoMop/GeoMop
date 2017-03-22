class ServiceProxy:
    """
    Automatic proxy class, provides methods to call 'request_XYZ' methods of
    the class passed as parameter of constructor. Further own thread is created
    (or reused) for every such call (this can be possibly optimized for simple requests in future).
    Returned data are stored in the variable of the name 'answer_XYZ'
    """
    def __init__(self, repeater, service_data):
        self.repeater = repeater
        self.service_class = service_class
        self.status=None
        """ ServiceStatus enum""""
        self.connected=False
        """ True if remote service is connected."""
        self.changing_status=False
        """ True if a astatus change action is processed: stopping"""

        pass

    def call(self, method_name, data, result):
        """
        Call 'method_name(data)' of the remote service returned result is appended
        to the result.
        :param method_name: Name of method to call.
        :param data: Serializable (JSONData) passed to the method.
        :param result: List of results.
        :return:
        """


    def get(self, variable_name):
        self.call("request_get", variable_name, self.__dict__[variable_name])

    def stop(self):
        self.call("stop", None, )

    def start_service(self):
        """
        Process of starrting a Job
        1. get job data: resource(ssh, exec), payload(dirs, files, init config)
        2. get connection (posibly existing)
        3. upload job files by connection
        4. get delegator from connection
        5. open starting port XX (localhost)
        5. remote port forwarding tunnel to local port XX
        6. submit (or start) job through delegator
        7. mark Jobb state as 'queued'
        8. sleep, wait for Job connection (different timeout for PBS and for exec)
        Job process:
        - open and listen on final port
        - connect back to the parent service
        - send listening port, wait for OK
        - after OK, close starting connection
        9. on received connection, get port, respond with OK, close starting connection
        10. forward tunnel to final port
        11. create final connection
        12. set Job state to running

        :return:
        """


        pass

"""
Use class factory to make proxy classes to Service classes.
"""
def class_factory(name, service=None):
    """
    Function used for creating subclasses of class Shape
    """

    def __init__(self, service_data):
        super(self.__class__, self).__init__(service_data)

    class_dict = {"__init__": __init__}
    for  func in service.__dict__:
        func_name = ...
        if is_request_method(func_name):
            def new_func(args):
                self.call("%s"%(func_name), args)

            class_dict[func_name] = new_func
    return type(name, (ServiceBase,), class_dict)