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
    """
    def __init__(self, repeater_address, socket_address, server_dispatcher):
        """
        :param repeater_address: Address of this repeater.
        :param socket_address: (ip, port) we connect to
        :param server_dispatcher: Server side of the repeater (can be None).
        """
        self.repeater_address = repeater_address
        # Own address given by parent repeater.
        self.address  = socket_address
        self.server = server_dispatcher
        self.answers = []
        self.sent_requests={}
        self.request_id=0
        self.received_data = bytearray()
        # Uncomplete answer.

        asynchat.async_chat.__init__(self)
        #self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        #logging.info( "Connecting: %s\n"%(str(self.address)) )
        #self.connect( self.address )

    def my_connect(self, address):
        self.create_socket()
        self.connect(address)

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



    """
    Remaining are implementations of asyncore methods.
    """

    def handle_connect(self):
        logging.info("Connected")
        self.set_terminator(_terminator)

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
    def __init__(self,  repeater_address, port, clients):
        """
        host - get automatically
        :param port - port ( same as in socket module)
        """
        asyncore.dispatcher.__init__(self)
        self.server_dispatcher = ServerDispatcher(repeater_address, port, clients)

        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind( ("", port) )
        self.address=self.socket.getsockname()
        self.answers=[]
        self.listen(5)


    def get_dispatcher(self):
        return self.server_dispatcher

    def handle_accept(self):
        # Called when a client connects to our socket
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
    def __init__(self, ar):#,  repeater_address, port, clients):
        """
        host - get automatically
        :param port - port ( same as in socket module)
        """
        asyncore.dispatcher.__init__(self)
        #self.server_dispatcher = ServerDispatcher(repeater_address, port, clients)

        self.ar = ar

        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(("", 0))
        self.address=self.socket.getsockname()
        #self.answers=[]
        self.listen(5)


    # def get_dispatcher(self):
    #     return self.server_dispatcher

    # def handle_accept(self):
    #     # Called when a client connects to our socket
    #     client_info = self.accept()
    #     logging.info("Incomming connection accepted.\n")
    #     self.server_dispatcher.accept(client_info[0])
    #     return

    def handle_accepted(self, sock, addr):
        StarterServerDispatcher(sock, self.ar)
        #print(sock.getsockname())

    # def handle_close(self):
    #     self.close()


class StarterServerDispatcher(asyncore.dispatcher):
    def __init__(self, sock, ar):
        super().__init__(sock)
        self.ar = ar

    def handle_read(self):
        data = self.recv(1024)
        #print(data)
        if data:
            s = data.decode().split("\n", maxsplit=2)
            if len(s) >= 2:
                child_id = int(s[0])
                port = int(s[1])
                #print((child_id, port))
                # je to paralelne bezpecne??????
                #print(self.ar.clients)
                if self.ar.clients[child_id] is None:
                    self.ar.clients[child_id] = _ClientDispatcher(self.ar.repeater_address, ("localhost", port), self.ar._server_dispatcher)
                #self.ar.clients[id].answers.append(AnswerData(id, sender, request, answer_dict, on_answer))
        self.close()


class AsyncRepeater():
    """
    Interface to request-answer communication tree.

    AsyncRepeaters forms a tree with root in client, first level with single node (backend),
    second level corresponding to multi jobs, and third level corresponding to Jobs.

    Repeaters handle packing and passing requests from any node to its particular childs
    and then propagating back the requests. Repeater do not process requests itself. Only in case of error
    it sends the error answer itself.

    TODO:
    listen port vzdy ziskat ze systemu (volani s listen_port=0)



    """
    def __init__(self, repeater_address, listen_port, parent_repeater_address=None):
        """
        :param repeater_address: Repeater id given be parent repeater in the tree.
        :param listen_port: None means no Server, 0 - get by kernel

        """
        self.repeater_address = repeater_address
        self.parent_repeater_address = parent_repeater_address
        self.max_client_id=0
        self.clients = {}
        """ Dict of clients. Keys client_id. """
        self._starter_client_thread = None
        self._starter_client_attempting = False
        if (listen_port is None):
            self._server_dispatcher = None
            self.listen_port = None
        else:
            self._server = Server(repeater_address, listen_port, self.clients)
            self.listen_port = self._server.address[1]
            self._server_dispatcher = self._server.get_dispatcher()

            if self.parent_repeater_address is not None:
                self._starter_client_attempting = True
                self._starter_client_thread = threading.Thread(target=self._starter_client_run)
                self._starter_client_thread.daemon = True
                self._starter_client_thread.start()

        self._starter_server = StarterServer(self)

        # TODO:
        # Start StarterClientDispatcher, trying to connect to parent and send our ID and listen_port
        # Stop StarterClienDispatcher if Server recievs connection.

        # logging.info("Listen: " + str(self.listen_port))

    def _starter_client_run(self):
        # az se repeater pripoji nastavit self._starter_client_attempting = False
        while self._starter_client_attempting:
            s = socket.socket()
            try:
                #print(self.parent_repeater_address)
                s.connect(self.parent_repeater_address)
                data = "{}\n{}\n".format(self.repeater_address, self.listen_port).encode()
                s.sendall(data)
            except ConnectionRefusedError:
                pass
            finally:
                s.close()
            time.sleep(10)

    def add_child(self):
        """
        TODO:
        1. Create StarterServer for child connection (make only one, in constructor)
           .. it listens for incomming connection from child and for getting first message, respond with OK and
            start _ClientDispatcher



        2. listen for child connection.
        2. Return Child ID
        :return:
        """
        self.max_client_id += 1
        id = self.max_client_id
        self.clients[id] = None # set ClientDispatcher after ful connection
        return id

    def _connect_child_repeater(self, socket_address):
        """
        Add new client, new connection to remote Repeater.
        :param id: Client/Repeater ID.
        :param address: (host, port)
        :return: Id of connected repeater.

        TODO: We need to reconnect if connection is broken. Should it be done in this class or by
        upper layer? In latter case we need other method to reconnect client.
        """
        # self.max_client_id += 1
        # id = self.max_client_id
        # self.clients[id] = _ClientDispatcher(self.repeater_address, socket_address, self._server_dispatcher)
        # return id


    def close_child_repeater(self, id):
        self.clients[id].close()
        del self.clients[id]
        return

    def send_request(self, target, data, on_answer):
        """
        Send request down through the connection.

         The request is given by 'data'., which could be any JSON serializable structure.
         The request is sent to the 'target' service.
         The on_naswer parameter gives additional data that are returned together with the answer to the request.
        :param target: target address continuous
            sublist of [ backend_id (=0), mj_id, job_id ]
        :param data: any JSON serializable structure
        :param on_answer: data returned together with answer
        :return: None
        """
        assert target, "Empty target."
        self.clients[target[0]].send_request(target[1:], data, on_answer)


    def send_answer(self, id, data):
        """

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

    def get_answers(self):
        """
        Get list of answers from all clients.
        :return: [ AnswerData, ... ]
        """
        #logging.info("GA")
        answers=[]
        for client in self.clients.values():
            answers.extend(client.get_answers())
        return answers

    def run(self, timeout = None):
        logging.info("before loop")

        self.loop_thread = threading.Thread(target=asyncore.loop, kwargs = {'timeout':1})
        logging.info("start")
        self.loop_thread.start()
        logging.info("after start")

    def stop(self):
        if self._server_dispatcher is not None:
            self._server_dispatcher.close()
        for c in self.clients.values():
            if c is not None:
                c.close()
        self._starter_server.close()
        self.loop_thread.join()