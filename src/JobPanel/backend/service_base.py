import subprocess
from . import async_repeater as ar
from .json_data import JsonData
from .environment import Environment
import logging
import concurrent.futures
import enum
import time



class ServiceStatus(enum.IntEnum):
    """
    State of a service.
    """
    queued = 1
    """
    Start of service executed, service queued in PBS.
    """
    running = 2
    """
    Service is running.
    """
    done = 3
    """
    Service is finished (both sucess and error), but still alive.
    """




def LongRequest():
    """
    Auxiliary decorator to mark requests that takes long time or
    perform its own communication and so must be processed in its own thread.
    """
    def decorator(func):
        func.run_in_thread = True
        return func
    return decorator


class ServiceStarter:
    """
    Start a child service and return ChildServiceProxy object.


    """
    def __init__(self):
        pass

    def start_pbs(self):
        pass


class ActionProcessor:
    """
    Base class for request processing and on_answer processing classes.
    If a method is decorated as @LongRequest it is executed in sepatate thread
    and future is stored in a special queue, this queue should be checked in the main service
    loop for the completed requests.

    TODO: Any particular reason why this is not part of ServiceBase??
    """
    def __init__(self):
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=10)

    def call_action(self, action, data):
        """
        Call method with name given by 'action' with 'data' as its only argument.
        Used for processing requests and on_answer actions.
        If the action method is marked be the LongRequest delegator it is processed in separate thread.
        :param action:
        :param data:
        :return:
        """
        try:
            action_method = getattr(self, action)

        except  AttributeError:
            result = {'error': 'Invalid action: %s' % (action)}
        else:
            if action_method.run_in_thread:
                future = self.thread_pool.submit(action_method, data)
            else:
                result = action_method(data)
        return result


class ServiceBase(ActionProcessor, JsonData):
    """
    Process requests and answers.

    Main event processing loop is started by method 'run'.
    Event types are: request, answer;
    An event is processed by calling the action method with name given
    by the event data.

    Request format:
    { 'action': 'request_*', 'data': <data to be passed to the remote called request function> }

    service.request_method(self, request_data)

    Answer format:
    { 'data': <return value  of the remote request action>, 'error': <the error type string, details in a_data> }

    On_answer format:
    { 'action': 'on_answer_*', 'data': further data provided to the on_answwer function with answer data> }

    service.on_answer_method(self, child_id, request_data, answer_data, oa_data)

    """
    answer_ok = { 'data' : 'ok' }

    def __init__(self, config):
        """
        Create the service and its repeater.
        """

        """
        JSONData initialization
        """
        self.repeater_address = []
        # Repeater address  of the service (path from root). Default is root repeater.
        self.parent_address=("", 0)
        # Socket address of the parent. Default is root service, no parent.
        self.environment=Environment()
        # environment of local installation
        self.executable=""
        # executable (script) by which the service is started
        self.exec_args=""
        # commandline parameters passed to the executable
        self.workspace = ""
        # service workspace relative to the geomop workspace
        self.listen_port=None
        #
        ActionProcessor.__init__(self)
        JsonData.__init__(self, config)

        self._geomop_workspace = ""
        # Geomop workspace dir on particular machine the service should run on. This should be
        # obtained from the global geomop setting not retrieved form the service configuration.

        self.child_services={}
        self.requests=[]

        self.repeater = ar.AsyncRepeater(self.repeater_address, self.parent_address)
        self.listen_port=self.repeater.listen_port

        self._closing = False

        # Write down the JSONData of the service into a config file.

    def get_listen_port(self):
        """
        TODO: Remove, service should maintain its config file and fill the listen_port there.
        :return:
        """
        return self.repeater.listen_port

    def run(self):
        """
        :return:
        """
        # Start the repeater loop.
        self.repeater.run()
        logging.info("After run")

        # Service processing loop.
        while not self._closing:
            logging.info("Loop")
            time.sleep(1)
            self._process_answers()
            self._process_requests()
            self._do_work()
        self.repeater.close()

    # Methods that implements a request but can also be called directly by the service.
    #

    def make_child_proxy(self, address):
        """
        TODO:
        - Use ServiceProxyBase instead of

        :return: Created child proxy.
        """
        child_id = self.repeater.add_child()
        proxy = ChildServiceProxy(child_id, self)
        self.child_services[child_id] = proxy
        return proxy


    def _process_answers(self):
        logging.info("Process answers ...")
        for ch_id in self.child_services.keys():
            for answer_data in self.repeater.get_answers(ch_id):
                logging.info("Processing: " + str(answer_data))
                child_id = answer_data.sender[0]
                on_answer = answer_data.on_answer
                answer = answer_data.answer
                if 'error' in answer.keys():
                    self.child_services[child_id].error_answer(answer_data)
                self.child_services[child_id].call_action(on_answer['action'], ( on_answer['data'],  answer['data'] ))
        return

    def _process_requests(self):
        self.requests.extend( self.repeater.get_requests() )
        for request_data in self.requests:
            request = request_data.request
            logging.info("Process Request: " + str(request))
            data = None
            if 'data' in request.keys():
                data = request['data']
            assert( 'action' in request.keys() )
            answer = self.call_action(request['action'], data)
            self.repeater.send_answer(request_data.id, answer)
        return

    """ Requests. """
    def request_start_child(self, request_data):
        """
        Start a new child service with given data.
        TODO:
        - implemented only in: RootService, BackendService

        proxy=self.make_child_proxy()
        proxy.start_service() ... enqueue the seervice
        :param request_data:
        :return: `OK`
        """
        address = request_data['socket_address']
        self.make_child_proxy(address)
        return self.answer_ok


    def request_stop_child(self, request_data):
        id = request_data['child_id']
        self.repeater.send_request([id], {'action' :' stop'}, { 'action' : 'on_answer_stop_child', 'data' : id})

    #def on_answer_stop_child(self, ):
    #    self.repeater.close_child_repeater(id)
    #    return self.answer_ok


    def request_get_status(self, data):
        """
        Return service status (obviously 'running').
        :param data: None
        :return:
        """
        return ServiceStatus.running

    def request_stop(self, data):
        self._closing = True
        return {'data' : 'closing'}





