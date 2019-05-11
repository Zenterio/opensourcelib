import logging
import socket
from contextlib import contextmanager

from zaf.builtin.remote.client import RemoteClient
from zaf.component.decorator import component
from zaf.extensions.extension import get_logger_name

logger = logging.getLogger(get_logger_name('k2', 'systestutils'))
logger.addHandler(logging.NullHandler())


@component(name='SystestRemoteClient', provided_by_extension='systestutils')
class SystestRemoteClient(object):

    def __init__(self):
        with socket.socket() as s:
            s.bind(('localhost', 0))
            self.port = s.getsockname()[1]

        logger.debug('Creating SystestRemoteClient with port {port}'.format(port=self.port))

    @contextmanager
    def client(self):
        with RemoteClient(host='localhost', port=self.port) as client:
            yield client
