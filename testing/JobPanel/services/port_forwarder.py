import threading
import logging
import select
import socket
import socketserver


class PortForwarder:
    """
    Class for local TCP port forwarding, for testing purposes.
    """
    def __init__(self, discard_data=False):
        self.discard_data = discard_data
        """if is True, transmitted data are discarded"""

        self._forwarded_ports = {}
        """dict of forwarded ports, {'forwarded_port': (thread, server)}"""

    def __del__(self):
        self.close_all_forwarded_ports()

    def forward_port(self, forward_to_port):
        """
        Get free local port and forward it to the given 'forward to port'.
        :param forward_to_port:
        :return: forwarded_port
        """

        class ForwardServer(socketserver.ThreadingTCPServer):
            daemon_threads = True
            allow_reuse_address = True

        class Handler(socketserver.BaseRequestHandler):
            port_forwarder = self

            def handle(self):
                """
                This function must do all the work required to service a request.
                It is called for every request.
                """
                sock = socket.socket()
                try:
                    sock.connect(("localhost", forward_to_port))
                except Exception as e:
                    logging.error('Forwarding request to %s:%d failed: %r' % ("localhost", forward_to_port, e))
                    return

                logging.info('Connected!  Tunnel open %r -> %r -> %r' % (self.request.getpeername(),
                                                                         sock.getpeername(),
                                                                         ("localhost", forward_to_port)))
                peername = None
                try:
                    while not self.port_forwarder.discard_data:
                        r, w, x = select.select([self.request, sock], [], [])
                        if self.request in r:
                            data = self.request.recv(1024)
                            if len(data) == 0:
                                break
                            if not self.port_forwarder.discard_data:
                                sock.send(data)
                        if sock in r:
                            data = sock.recv(1024)
                            if len(data) == 0:
                                break
                            if not self.port_forwarder.discard_data:
                                self.request.send(data)

                    peername = self.request.getpeername()
                except OSError:
                    pass
                sock.close()
                self.request.close()
                if peername is not None:
                    logging.info('Tunnel closed from %r' % (peername,))

        # port 0 means to select an arbitrary unused port
        server = ForwardServer(('', 0), Handler)
        forwarded_port = server.server_address[1]

        # start server in thread
        t = threading.Thread(target=server.serve_forever)
        t.daemon = True
        t.start()

        # add thread and server to dict
        self._forwarded_ports[forwarded_port] = (t, server)

        return forwarded_port

    def close_forwarded_port(self, forwarded_port):
        """
        Close forwarded port.
        :param forwarded_port:
        :return:
        """
        if forwarded_port in self._forwarded_ports:
            # shutdown server
            t, server = self._forwarded_ports[forwarded_port]
            server.shutdown()
            server.server_close()

            # wait for server's thread ends
            t.join(1)
            if t.is_alive():
                logging.warning("Server's thread stopping timeout")

            # remove from dict
            del self._forwarded_ports[forwarded_port]

    def close_all_forwarded_ports(self):
        """
        Close all forwarded ports.
        """
        for port in list(self._forwarded_ports.keys()):
            self.close_forwarded_port(port)
