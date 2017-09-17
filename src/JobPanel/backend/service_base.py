import subprocess
from . import async_repeater as ar
from .json_data import JsonData, ClassFactory
from .environment import Environment
from .connection import ConnectionLocal, ConnectionSSH
from .executor import ProcessExec, ProcessPBS, ProcessDocker

# import in code
#from .service_proxy import ServiceProxy

import logging
import concurrent.futures
import enum
import time
import json
import os
import threading
import sys
import traceback
import socket
import fcntl
import struct
import hashlib


"""
TODO:
- Unit test for LongRequest?
- Unit test to catch an error request (descendent of ServiceBase)
- Otestovat mechanismus emulace pripojeni pomoci tunelu a preruseni spojeni pomoci preruseni posilani v tunelu.
- JobPanel bude povolen bezet jen v jedne instanci na stejnym Workspace (jako Eclipse)

Possible levels of error:

- during starting child ... see ServiceProxy.start_service
- error behem zpracovani requestu ...
  Unit test, lokalni odchyceni chyby ktera nastane behem call_action, zapis do logu, (descendent of ServiceBase)
  Unit test, vcetne vzdaleneho volani requastu a navratu chyby do fronty vysledku
- every uncatched error in any Service is logged and written into config file.
- check how to catch excetions in repeater.run thread - pomoci handle_error
- check how to catch excetions in tunnel threads ( possibly no problem) - pokud dojde k chybe tunel se uzavre
- no network connection:
   - correct setting of timeouts of sockets in repeater, connection (tunnels)

Questions:
- specify workdirs for individual serivces:
    - Delegator: workspace/Delegators, every execution of delegator have uique log filename given by date_time_process_id
      delegator nema conf.
    - Job: unique workspace, with name given by parent MJ and job ID within this MJ, job_service.log, .conf
    - MJ: unique workspace, name given by analysis and number of run, mj_service.log, .conf
    - Backend: main workspace, backend_service.log, .conf
    - Frontend: main wokrspace, frontend_service.log, .conf

"""


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




def LongRequest(func):
    """
    Auxiliary decorator to mark requests that takes long time or
    perform its own communication and so must be processed in its own thread.
    """
    func.run_in_thread = True
    return func


# class ServiceStarter:
#     """
#     Start a child service and return ChildServiceProxy object.
#
#
#     """
#     def __init__(self):
#         pass
#
#     def start_pbs(self):
#         pass


def call_action(obj, action, data, result=None):
    """
    Call method of 'obj' with name given by 'action' with 'data' as its only argument.
    Used for processing requests and on_answer actions.
    If the action method is marked be the LongRequest delegator it is processed in separate thread.
    If list is given in 'result' parameter, result is save in it.

    TODO:
    - catch exceptions return error answer, how to do it for exceptions in threads?
    :param action:
    :param data:
    :param result:
    :return:
    """
    logging.info("call_action(action: {}, data: {})".format(action, data))

    def save_result(res):
        if result is not None:
            result.append(res)

    try:
        action_method = getattr(obj, action)
    except AttributeError:
        save_result({'error': 'Invalid action: %s' % (action)})
        return

    def wrapper():
        try:
            res = {"data": action_method(data)}
        except:
            res = {'error': "Exception in action:\n" + "".join(traceback.format_exception(*sys.exc_info()))}
            logging.error("call_action Exception:\n{})".format(res))
        # logging.info("res: {})".format(res))
        save_result(res)

    if hasattr(action_method, "run_in_thread") and action_method.run_in_thread:
        # future = self._thread_pool.submit(action_method, data)
        t = threading.Thread(target=wrapper)
        t.daemon = True
        t.start()
        # TODO:
        # - How to get result after completion.
        # First option:
        #   keep list of processing threads
        #   check complition in c and call repeater.send_answer for result
        # Second option:
        #   keep list of results, the thread append the result to this list,
        #   list is processed and send_answer called in service_address
        # Third option:
        #   similar to previous. Result is not stored in the list, but send_answer
        #   is called directly from the thread.
        #
        # - First try without pool.

    else:
        wrapper()


class ServiceBase(JsonData):
    """
    From ActionProcessor:
    Base class for request processing and on_answer processing classes.
    If a method is decorated as @LongRequest it is executed in sepatate thread
    and future is stored in a special queue, this queue should be checked in the main service
    loop for the completed requests.


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
    # answer_ok = { 'data' : 'ok' }

    def __init__(self, config):
        """
        Create the service and its repeater.
        """

        """
        JSONData initialization
        """
        self.service_host_connection = ClassFactory( [ConnectionLocal, ConnectionSSH] )
        # IP where the service should be executed.
        self.repeater_address = []
        # Repeater address  of the service (path from root). Default ([]) is root repeater.
        self.parent_address=("", 0)
        # Socket address of the parent. Default is root service, no parent.
        #self.environment=Environment()
        # environment of local installation
        #self.executable=""
        # executable (script) by which the service is started
        #self.exec_args=""
        # commandline parameters passed to the executable
        self.process = ClassFactory([ProcessExec, ProcessPBS, ProcessDocker])
        """process for starting service"""
        self.workspace = ""
        # service workspace relative to the geomop workspace
        self.input_files = []
        # List of file paths to upload befor service is started. Paths are relative to
        # the service workspace, i.e. self.workspace.

        self.listen_address = ("", 0)
        """Socket address where service listening."""
        self.status = ServiceStatus.queued
        """Service status"""
        self.wait_before_run = 0.0
        """Wait before run service, used for testing purposes."""
        self.config_file_name = ""
        """Name of service config file."""

        super().__init__(config)

        self._thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=10)

        self._geomop_workspace = ""
        # Geomop workspace dir on particular machine the service should run on. This should be
        # obtained from the global geomop setting not retrieved form the service configuration.

        self._child_services = {}
        """Dict of child service proxies."""

        self._repeater = ar.AsyncRepeater(self.repeater_address, self.parent_address)
        self.listen_address = (self.get_ip_address(), self._repeater.listen_port)

        self._closing = False

        self._connections = {}
        """dict of active connections"""
        self._connections_lock = threading.Lock()
        """Lock for _connections"""

        self._answers_to_send = []
        """list of answers to send (id, [answer])"""

        self._process_class_factory = ClassFactory([ProcessExec, ProcessPBS, ProcessDocker])
        """process class factory for process start/status/kill"""


    def save_config(self):
        """
        Save config to file.
        :return:
        """
        if len(self.config_file_name) == 0:
            return

        file = os.path.join(self.get_analysis_workspace(),
                            self.workspace,
                            self.config_file_name)
        with open(file, 'w') as fd:
            json.dump(self.serialize(), fd, indent=4, sort_keys=True)

    def run(self):
        """
        :return:
        """
        time.sleep(self.wait_before_run)

        # Start the repeater loop.
        self._repeater.run()
        logging.info("After run")

        self.status = ServiceStatus.running
        self.save_config()

        last_time = time.time()

        # Service processing loop.
        while not self._closing:
            #logging.info("Loop")
            self._process_answers()
            self._process_requests()
            self._send_answers()
            self._do_work()
            self._check_connections()
            self._check_child_services()
            self._repeater.discard_closed_childs()

            # sleep, not too much
            remaining_time = 0.1 - (time.time() - last_time)
            if remaining_time > 0:
                time.sleep(remaining_time)
            last_time = time.time()

        self._repeater.close()
        self.close_connections()



    def _process_answers(self):
        #logging.info("Process answers ...")
        for ch_service in self._child_services.values():
            ch_service._process_answers()
        # for d_service in self._delegator_services.values():
        #     d_service._process_answers()
        for con in self._connections.values():
            if (con._delegator_proxy is not None) and (con._delegator_proxy is not self):
                con._delegator_proxy._process_answers()

    def _process_requests(self):
        requests = self._repeater.get_requests()
        for request_data in requests:
            request = request_data.request
            logging.info("Process Request: " + str(request))
            data = None
            if 'data' in request.keys():
                data = request['data']
            assert( 'action' in request.keys() )

            answer = []
            call_action(self, request['action'], data, answer)
            self._answers_to_send.append((request_data.id, answer))

            # TODO:
            # catch exceptions, use async_repeater._exception_answer(e) to return
            # exception result. Use format_exception in _exception_answer instead of just traceback.
            # For correct result introduce similar formater.


    def _send_answers(self):
        """
        Send filled answers form self._answers_to_send.
        Method is thread safe.
        :return:
        """
        done = False
        while not done:
            for i in range(len(self._answers_to_send)):
                if len(self._answers_to_send[i][1]) > 0:
                    item = self._answers_to_send.pop(i)
                    self._repeater.send_answer(item[0], item[1][0])
                    break
            done = True

    def _do_work(self):
        """
        Periodically called in service processing loop.
        :return:
        """
        pass

    def _check_connections(self):
        for con in self._connections.values():
            con.get_status()

    def _check_child_services(self):
        for child in self._child_services.values():
            child.get_status()

    def get_connection(self, connection_data):
        """
        Keep active connections in a dict and reuse connection to same hosts.
        :param connection_data:
        :return:
        """
        text = json.dumps(connection_data, separators=(',', ':'), sort_keys=True)
        hash = hashlib.sha512(bytes(text, "utf-8")).hexdigest()
        with self._connections_lock:
            if hash in self._connections:
                return self._connections[hash]
            else:
                con = ClassFactory([ConnectionSSH, ConnectionLocal]).make_instance(connection_data)
                con.set_local_service(self)
                con.connect()
                self._connections[hash] = con
                return con

    def close_connections(self):
        """
        Close connections and remove it from dict.
        :return:
        """
        with self._connections_lock:
            for con in self._connections.values():
                con.close_connections()
            self._connections.clear()

    def get_analysis_workspace(self):
        return self.service_host_connection.environment.geomop_analysis_workspace

    def get_ip_address(self):
        """
        Return IP address of eth0.
        If fails return 127.0.0.1.
        :return:
        """
        ifname = 'eth0'
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            return socket.inet_ntoa(fcntl.ioctl(
                s.fileno(),
                0x8915,  # SIOCGIFADDR
                struct.pack('256s', ifname[:15].encode())
            )[20:24])
        except OSError:
            return "127.0.0.1"

    def get_ip_address2(self):
        """
        Return IP address of interface connected to internet.
        If fails return 127.0.0.1.
        :return:
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
        except OSError:
            return "127.0.0.1"
        finally:
            s.close()

    def call(self, method_name, data, result):
        """
        Call 'method_name(data)' of this service, returned result is appended
        to the result which has to be a list.

        :param method_name: Name of method to call.
        :param data: Serializable (JSONData) passed to the method.
        :param result: List of results.
        :return: None, error.
        """
        call_action(self, method_name, data, result)


    #######################################################################################
    # Methods that implements a request but can also be called directly by the service.
    #


    """ Requests. """

    @LongRequest
    def request_start_child(self, service_data):
        """
        Start a new child service with config given by `service_data`.
        - Marked as LongRequest so it runs in separated thread as it takes longer time to complete.

        TODO:
        - Root starts Backend in Docker either:
          - docker have same IP as Root, then we can set connection in service_data
          - docker have separate IP, then we must create container and get its IP before
            executing backend in the container

        :param service_data: Service configuration data.
        :return: STATUS
        """
        connection = self.get_connection(service_data["service_host_connection"])


        from .service_proxy import ServiceProxy
        proxy = ServiceProxy({})
        proxy.set_rep_con(self._repeater, connection)
        child_id = proxy.start_service(service_data)
        self._child_services[child_id] = proxy

        return child_id


    # def request_stop_child(self, request_data):
    #     id = request_data['child_id']
    #     self._repeater.send_request([id], {'action' :' stop'}, { 'action' : 'on_answer_stop_child', 'data' : id})

    #def on_answer_stop_child(self, ):
    #    self._repeater.close_child_repeater(id)
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

    def request_process_start(self, process_config):
        logging.info("request_process_start(process_config: {})".format(process_config))
        executor = self._process_class_factory.make_instance(process_config)
        return executor.start()

    def request_process_status(self, process_config):
        executor = self._process_class_factory.make_instance(process_config)
        return executor.get_status()


    def request_process_kill(self, process_config):
        executor = self._process_class_factory.make_instance(process_config)
        return executor.kill()




