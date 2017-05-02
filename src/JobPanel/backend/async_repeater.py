import socket
import asynchat
import asyncore
import threading
import json
import traceback
import sys
import logging
import time

"""
TODO:
- AsyncRepeater umi:
    - poslat pozadavek
    - dat posledni odpoved z fronty, odpoved i s pozadavakem?
    - restartovat connect
    - restartovt listen (zmena portu?)

    - odpovedi automaticky posila dale, pokud neni spojeni, zahazuje
    - pozadavky bud uklada do sve fronty, nebo preposila (podle adresy), pokud neni spojeni,
      vraci odpoved s chybou

Struktura zprav:
zadani pozadavku : recipient, data
odeslani pozadavku: id, recipient, sender, data; (data also stored)
odpoved: id,  sender, answer data
vraceni odpovedi: id, recipient, answer, request
"""


_terminator = '\n'.encode()

def _pack_message(id, sender, recipient, data):
    str_json=json.dumps((id, sender, recipient, data))
    return str_json.encode() + _terminator

def _unpack_message(msg):
    return json.loads(msg.decode())

def _exception_answer(e):
    """
    Retrun answer with catched exception, stack, ...
    :param e: The excpetion.
    :return:
    """
    return { 'error': 'Exception', 'exception': repr(e), 'traceback': traceback.format_tb() }

def _close_request():
    """
    Auxiliary request to inform service about clossed server-side connection.
    Action should return no answer.
    :return:
    """
    return {'action': 'request_close'}

def _close_answer():
    """
    Auxiliary answer to inform service about clossed clinet-side connection.
    :return:
    """
    return {'action': 'on_answer_close'}

class RequestData:
    """
    Format of request returned by the AsyncRepeater.
    The processing of the request should not depend on id and sender, but
    they are provided for possible logging.

    Attributes:
        self.id          request id, unique per child service
        self.sender      address of the service the send the request
        self.request     request itself
    """
    def __init__(self, id, sender, data):
        self.id = id            # request id, unique per child service
        self.sender = sender    # address of the service the send the request
        self.request = data     # request itself

class AnswerData:
    """
    Format of answer returned by the AsyncRepeater.

    Attributes:
        self.id         request id, unique id= id
        self.sender     sender of answer, target of request
        self.request    request_data
        self.answer     answer_data
        self.on_answer  data stored when request was sent
    """
    def __init__(self, id, sender, request, answer, on_answer):
        self.id = id
        self.sender = sender # target of the request
        self.request = request
        self.answer = answer
        self.on_answer = on_answer



class _ClientDispatcher(asynchat.async_chat):
    """
    Client part of the communication. Send requests, process answers.

    The _ClientDispatcher have following states:

        1. Waiting to get address from child through StarterServer.

        2. Waiting for call connect_to_address(). Have valid self._remote_address, but not connected yet (can not send or recieve message).

        3. Connecting.

        4. Connected.
    """
    def __init__(self, repeater_address, server_dispatcher, connection, get_answer_on_connect=None):
        """
        :param repeater_address: Address of this repeater.
        :param server_dispatcher: Server side of the repeater (can be None). Used to resend answers.
        :param connection: A conncetion object for port forwarding of final connection to the child repeater.
        """
        self.repeater_address = repeater_address
        # Own address given by parent repeater.
        self.address = None
        # Local address to which we connect for permanent connection.
        self._remote_address = None
        # Romete address at which child is listening.
        # (ip, port) on remote machine we connect to over tunnel
        self.server = server_dispatcher
        self.answers = []
        # Received answers for local service.
        self.sent_requests={}
        # Sent requests from local service
        self.request_id=0
        # ID of the next request.
        self.received_data = bytearray()
        # Storage for partially received answer.
        self.connection = connection

        # create request 0
        self.sent_requests[0] = (None, None)

        asynchat.async_chat.__init__(self)

    def connect_to_address(self, address):
        assert not self.connected
        self.address = address
        self.create_socket()
        logging.info("Connecting: %s\n" % (str(self.address)))
        self.connect(self.address)

    def is_connected(self):
        return self.connected

    def get_answers(self):
        """
        Extract and return (almost) all recieved requests to proceess.
        Since this extraction is done by the single thread, it should be safe.
        :return:
        """
        copy=[]
        size=len(self.answers)
        for i in range(size):
            answer = self.answers.pop(0)
            logging.info("Copy answer: " + str(answer))
            (id, sender, reciever, answer_dict) = answer
            (request, on_answer) = self.sent_requests.pop(id)
            copy.append( AnswerData(id, sender, request, answer_dict, on_answer) )
        return copy


    def send_request(self, target, data, on_answer):
        """
        Send request down through the connection tree.
        :param target: repeter list, continuous sublist of [ backend_id, mj_id, job_id]
        :param data: JSON data
        :return:
        """
        self.request_id +=1
        id = self.request_id
        self.sent_requests[id] = (data, on_answer)
        logging.info('Push: %s\n'%( _pack_message(id, self.repeater_address, target, data)) )
        self.push( _pack_message(id, self.repeater_address, target, data) )

    def set_remote_address(self, address):
        # Set remote address of the child repeater.
        # This force port forwarding through connection object and connect.
        if self._remote_address is not None:
            return

        self._remote_address = address

        # forward tunnel
        local_port = self.connection.forward_local_port(self._remote_address[1])

        self.connect_to_address(("localhost", local_port))


    """
    Remaining are implementations of asyncore methods.
    """

    def handle_connect(self):
        logging.info("Connected")
        self.set_terminator(_terminator)

        # create answer 0
        self.answers.append((0, None, None, None))

    def collect_incoming_data(self, data):
        """Read an incoming message from the client and put it into our outgoing queue."""
        logging.info("Collect")
        self.received_data.extend(data)

    def found_terminator(self):

        msg = _unpack_message(self.received_data)
        logging.info("Client, message: "+ str(msg))
        self.received_data = bytearray()
        if msg:
            recipient = msg[2]
            logging.info("recp: %s addr: %s"%(str(recipient), str(self.repeater_address)))
            if recipient != self.repeater_address:
                assert self.server, "Wrong recipient: %s"%(str(recipient))
                # forward answer
                self.server.push(msg)
            else:
                # process answers t own reqests
                self.answers.append( msg )




class Server(asyncore.dispatcher):
    def __init__(self,  repeater, port, clients):
        """
        host - get automatically
        :param port - port ( same as in socket module)
        """
        self.repeater = repeater
        asyncore.dispatcher.__init__(self)
        self.server_dispatcher = ServerDispatcher(repeater.repeater_address, port, clients)

        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind( ("", port) )
        self.address=self.socket.getsockname()
        self.answers=[]
        self.listen(5)


    def get_dispatcher(self):
        return self.server_dispatcher

    def handle_accept(self):
        # Called when a client connects to our socket

        # stop starter client
        self.repeater._starter_client_attempting = False

        client_info = self.accept()
        logging.info("Incomming connection accepted.\n")
        #print("Incomming connection accepted.")
        self.server_dispatcher.accept(client_info[0])
        return

    def handle_close(self):
        self.close()

class ServerDispatcher(asynchat.async_chat):
    def __init__(self,  repeater_address, port, clients):
        """
        host - get automatically
        :param port - port ( same as in socket module)
        """
        self.repeater_address = repeater_address
        logging.info("Raddr: %s"%(str(repeater_address)))
        # Own address given by parent repeater.
        self.port = port
        # Port we will connect after accept.
        self.clients = clients
        # Dict of client dispatchers.
        self.requests = []
        # Recieved requests to be processed.
        self.request_senders={}
        # Dict  id-> sender. Used to send answers to correct origin.
        self.received_data = bytearray()
        # Uncomplete request.
        self.answer_id = 0
        # Server numbering of answers.


    def accept(self, socket):
        logging.info("Accept\n")
        asynchat.async_chat.__init__(self, sock = socket)
        #self.set_socket(socket)
        self.set_terminator(_terminator)
        return

    def get_requests(self):
        """
        Extract and return (almost) all recieved requests to proceess.
        Since this extraction is done by the single thread, it should be safe.
        :return:
        """
        copy=[]
        req_len=len(self.requests)
        logging.info("GET requests len: %d"%( len(self.requests) ))
        for i in range(req_len):
            request = self.requests.pop(0)
            logging.info("copy req: " + str(request) )
            (request_id, sender, recipient, data) = request
            self.request_senders[self.answer_id]=(request_id, sender)
            copy.append( RequestData(self.answer_id, sender, data) )
            self.answer_id += 1
        return copy

    def send_answer(self, answer_id, data):

        (id, sender) = self.request_senders.pop(answer_id)
        logging.info("send answer: " + str(_pack_message(id, self.repeater_address, sender, data)) )
        self.push( _pack_message(id, self.repeater_address, sender, data) )


    """
    Remaining are implementations of asyncore methods.
    """
    def collect_incoming_data(self, data):
        """
        Read an incoming message from the client and put it into our outgoing queue.
        """
        self.received_data.extend(data)

    def found_terminator(self):
        """
        The end of a command or message has been seen.
        """
        msg = _unpack_message(self.received_data)
        logging.info("Server, message: " + str(msg))
        self.received_data = bytearray()
        if msg:
            (id, sender, recipient, request) = msg
            if len(recipient) == 0:
                # empty recipient, we have to process
                logging.info("process: " + str(msg))
                self.requests.append( msg )
                logging.info("requests len: %d"%( len(self.requests)  ))
            else:
                if recipient[0] in self.clients:
                    client = self.clients[recipient[0]]
                    if client.connected:
                        try:
                            # forward message
                            client.push( _pack_message(id, sender, recipient[1:], request) )
                        except Exception as e:
                            self.push( _pack_message(id, self.repeater_address, sender, _exception_answer(e)) )
                            return

                    else:
                        msg = {'error': "Recipient not connected", 'recipient': self.repeater_address + recipient[0]}
                        self.push(_pack_message(id, self.repeater_address, sender, msg) )

                else:
                    msg={ 'error' : "Unknown recipient", 'recipient': self.own_address + recipient[0] }
                    self.push( _pack_message(id, self.repeater_address, sender, msg ) )


    def handle_close(self):
        #self.logger.debug('handle_close()')
        self.close()
        return


class StarterServer(asyncore.dispatcher):
    """
    Server which accepts reverse connection from child repeaters.
    """
    def __init__(self, async_repeater):
        """
        :param async_repeater:
        """
        asyncore.dispatcher.__init__(self)

        self.async_repeater = async_repeater

        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(("", 0))
        self.address=self.socket.getsockname()
        self.listen(5)
        logging.info("Starter Server listening at address: {}", self.address)

    def handle_accepted(self, sock, addr):
        StarterServerDispatcher(sock, self.async_repeater)
        #print(sock.getsockname())


class StarterServerDispatcher(asyncore.dispatcher):
    def __init__(self, sock, async_repeater):
        super().__init__(sock)
        self.async_repeater = async_repeater

    def handle_read(self):
        data = self.recv(1024)
        #print(data)
        if data:
            s = data.decode().split("\n", maxsplit=2)
            # Skip connections with wrong number of parameters.
            if len(s) == 2:
                child_id = int(s[0])
                port = int(s[1])
                print((child_id, port))
                #print(self.async_repeater.clients)

                if child_id in self.async_repeater.clients:
                    self.async_repeater.clients[child_id].set_remote_address((self.socket.getpeername(), port))
                    logging.info("Initial back connection done.")
        self.close()
        # We close also if we get wrong data. As whole connection is from bad guy.

class AsyncRepeater():
    """
    Interface to request-answer communication tree.

    AsyncRepeaters form a tree with root in client, first level with single node (backend),
    second level corresponding to multi jobs, and third level corresponding to Jobs.

    Repeaters handle packing and passing a request from any node to its particular child
    and then propagating back the answer to the request.
    Repeater do not process requests itself.
    Only in the case of error it sends the error answer itself.
    """
    def __init__(self, repeater_address, parent_address=None):
        """
        :param repeater_address: Repeater address as a list of IDs for path from root repeater to self.
            last item is ID of self repeater.
        :param listen_port: The port for permanent connection of the parent repeater to the self.
               None - means no listening port is open (i.e. root repeater)
               0 - get by kernel (usual case)
        :param parent_address:
                socket address ( address, port) of the parent repeater to connect for initialization.
        """
        self.repeater_address = repeater_address
        self.parent_address = parent_address
        self.max_client_id=0
        self.clients = {}
        """ Dict of clients. Keys client_id. """
        self._starter_client_thread = None
        self._starter_client_attempting = False
        if (parent_address is None):
            self._server_dispatcher = None
            self.listen_port = None
        else:
            self._server = Server(self, 0, self.clients)
            self.listen_port = self._server.address[1]
            self._server_dispatcher = self._server.get_dispatcher()

            self._starter_client_attempting = True
            self._starter_client_thread = threading.Thread(target=self._starter_client_run)
            self._starter_client_thread.daemon = True
            self._starter_client_thread.start()

        self._starter_server = StarterServer(self)


    def run(self):
        """
        Start the repeater loop in separate thread.
        :return: None
        """
        self.loop_thread = threading.Thread(target=asyncore.loop, kwargs = {'timeout':0.1})
        self.loop_thread.start()
        logging.info("Repeater loop started.")


    def add_child(self, connection, remote_address=None):
        """
        Setup connection to a child repeater.
        1. Create a Dispatcher for connection to the child repeater, but do not connect.
        2. Ask `connection` for romote port forwarding to the StarterServer port.
        2. StarterServer wait for back connection from the child repeater, to get its listening port.
        3. Then StarterServer asks the Dispatcher to connect to the child repeater through the `connection`
         passed as parameter (local port forwarding).

        :param connection: The connection object used for port forwarding (None forwarding or SSH).
        :param remote_port: If the remote port is known, we skip the StarterServer connection and call
        connection to the child repeater directly.

        :return: ( child_id, forwarded_remote_port)
            child_id: ID of the child repeater it must be passed to the repeater when its process is started
            (e.g. as command parameter)
            forwarded_remote_port: a port on the remote machine the child repeater runs on to which it should connect
            to send its listening_port to the parent.

        TODO: test and possibly finish support for the remote_port parameter.
        IDEA: to check that we get correct child we may generate child ids not incermentaly, but at random.
             Then it servers also as a unique token to check that the correct repeater is connecting to the StarterServer.
        """
        self.max_client_id += 1
        id = self.max_client_id
        self.clients[id] = _ClientDispatcher(self.repeater_address, self._server_dispatcher, connection)

        if remote_address:
            self.clients[id].set_remote_address(remote_address)
            remote_port = None
        else:
            # remote tunnel
            local_port = self._starter_server.address[1]
            remote_port = connection.forward_remote_port(local_port)

        return id, remote_port


    def close_child_repeater(self, id):
        """
        Check that socket to child is closed. Delete the dispatcher.

        TODO: thread safe?
        :param id:
        :return:
        """
        self.clients[id].close()
        del self.clients[id]
        return

    def send_request(self, target, data, on_answer):
        """
        Send request down through the connection.

         The request is given by 'data'., which could be any JSON serializable structure.
         The request is sent to the 'target' service.
         The on_naswer parameter gives additional data that are returned together with the answer to the request.

        TODO: test and finish.
        :param target: target repeater address relative to local repeater.
            I.e. sublist of [ backend_id (=0), mj_id, job_id ]
        :param data: any JSON serializable structure
        :param on_answer: data returned together with answer
        :return: None
        """
        #assert target, "Empty target."
        self.clients[target[0]].send_request(target[1:], data, on_answer)


    def send_answer(self, id, data):
        """
        Send an answer from local service. This is automatically paired with
        the corresponding request. From which we get the target of the answer.
        :param id: Id of request to which we answer.
        :param data: Answer data.
        :return:
        """
        self._server_dispatcher.send_answer(id, data)

    def get_requests(self):
        """
        Get list of requests to process.
        :return: [ RequestData, ... ]
        """
        #logging.info("GR")
        return self._server_dispatcher.get_requests()

    def get_answers(self, child_id):
        """
        Get list of answers from client (child_id).
        :return: [ AnswerData, ... ]
        """
        #logging.info("GA")
        return self.clients[child_id].get_answers()


    def close(self):
        """

        :return:
        """
        if self._server_dispatcher is not None:
            self._server_dispatcher.close()
        for c in self.clients.values():
            if c is not None:
                c.close()
        self._starter_server.close()
        self.loop_thread.join()

    def _starter_client_run(self):
        logging.info("Atempting for  back to parent initial connection to address: {}", self.parent_address)
        while self._starter_client_attempting:
            s = socket.socket()
            try:
                s.connect(self.parent_address)
                data = "{}\n{}".format(self.repeater_address[-1], self.listen_port).encode()
                s.sendall(data)
            except ConnectionRefusedError:
                pass
            finally:
                s.close()
            time.sleep(10)
