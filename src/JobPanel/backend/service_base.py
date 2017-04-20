import subprocess
from . import async_repeater as ar
import logging
import concurrent.futures



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

            result = action_method(data)
        return result

class ChildServiceProxy(ActionProcessor):
    """
    TODO:
    - move request methods into ServiceProxyBase
    - delete this class

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
    def __init__(self, child_id, service):
        self.child_id = child_id
        self.service = service

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


class ServiceBase(ActionProcessor):
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

    def __init__(self, service_address, listen_port, parent_repeater_address=None):
        """
        TODO:
        - design config data
        - derive from JSONData
        - write down config file
        """
        self.child_services={}
        self.requests=[]
        self.repeater = ar.AsyncRepeater(service_address, listen_port, parent_repeater_address)

    def get_listen_port(self):
        """
        TODO: Remove, service should maintain its config file and fill the listen_port there.
        :return:
        """


        return self.repeater.listen_port


    def make_child_proxy(self, address):
        """
        TODO:
        - remove address parameter since currently the child initiates the first connection
        - Use ServiceProxyBase instead of
        - id = repeater.add_child() #instead of connect_child_repeater

        :return: Created child proxy.
        """
        child_id = self.repeater.connect_child_repeater(address)
        proxy = ChildServiceProxy(child_id, self)
        self.child_services[child_id] = proxy
        return proxy


    def process_answers(self):
        logging.info("Process answers ...")
        for answer_data in self.repeater.get_answers():
            logging.info("Processing: " + str(answer_data))
            child_id = answer_data.sender[0]
            on_answer = answer_data.on_answer
            answer = answer_data.answer
            if 'error' in answer.keys():
                self.child_services[child_id].error_answer(answer_data)
            self.child_services[child_id].call_action(on_answer['action'], ( on_answer['data'],  answer['data'] ))
        return

    def process_requests(self):
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

    """"""
    def request_start_child(self, request_data):
        """
        TODO:

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


    def request_ping(self, data):
        return self.answer_ok

    def request_stop(self, data):
        self.closing = True
        return {'data' : 'closing'}


    """
    Delegator requests. (WIP)
    """

    def request_start_service(self, executor_config):
        executor  = JsonData.make_instance(executor_config)
        executor.exec()

    def request_kill_service(self, executor_config):
        executor = JsonData.make_instance(executor_config)
        executor.kill()

    def request_clean_workspace(self):
        pass


