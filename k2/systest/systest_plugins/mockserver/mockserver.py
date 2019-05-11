import logging
import socketserver
import threading
from http.server import HTTPServer

from zaf.extensions.extension import CommandExtension

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


@CommandExtension('mockserver')
class MockServer(object):
    pass


class GenericMockServerBaseClass():
    allow_reuse_address = True

    def default_values(self, host, port):
        host = 'localhost' if host is None else host
        port = 0 if port is None else port
        return host, port

    @property
    def port(self):
        return self.server_address[-1]

    def start(self):
        self.thread = threading.Thread(target=self.serve_forever)
        self.thread.start()

    def stop(self):
        self.shutdown()
        self.server_close()
        self.thread.join()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *exc_info):
        self.stop()


class TcpMockServer(GenericMockServerBaseClass, socketserver.TCPServer):

    def __init__(self, request_handler, host=None, port=None):
        host, port = self.default_values(host, port)
        socketserver.TCPServer.__init__(self, (host, port), request_handler)


class UdpMockServer(GenericMockServerBaseClass, socketserver.UDPServer):

    def __init__(self, request_handler, host=None, port=None):
        host, port = self.default_values(host, port)
        socketserver.UDPServer.__init__(self, (host, port), request_handler)


class HttpMockServer(GenericMockServerBaseClass, HTTPServer):

    def __init__(self, request_handler, host=None, port=None):
        host, port = self.default_values(host, port)
        socketserver.UDPServer.__init__(self, (host, port), request_handler)
