import logging
import signal

from zaf.application.signalhandler import SignalHandler
from zaf.extensions.extension import AbstractExtension, FrameworkExtension

from k2 import ABORT, CRITICAL_ABORT, K2_APPLICATION_ENDPOINT

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class ApplicationSignalHandler(SignalHandler):

    def __init__(self):
        super().__init__()
        self.aborts = 0
        self.register_handler(signal.SIGINT, self._handle_sigint)
        self.register_handler(signal.SIGABRT, self._handle_sigabrt)
        self.register_handler(signal.SIGTERM, self._handle_sigterm)

    def _handle_sigint(self, sig, frame):
        logger.debug('sigint')
        self.aborts += 1
        if self.aborts == 1:
            self.messagebus.trigger_event(ABORT, K2_APPLICATION_ENDPOINT)
        elif self.aborts == 2:
            self.messagebus.trigger_event(CRITICAL_ABORT, K2_APPLICATION_ENDPOINT)
        else:
            self._original_signal_handlers[signal.SIGINT]()

    def _handle_sigabrt(self, sig, frame):
        logger.debug('sigabrt')
        self.messagebus.trigger_event(CRITICAL_ABORT, K2_APPLICATION_ENDPOINT)

    def _handle_sigterm(self, sig, frame):
        logger.debug('sigterm')
        self.messagebus.trigger_event(CRITICAL_ABORT, K2_APPLICATION_ENDPOINT)


@FrameworkExtension(
    name='signalhandler', endpoints_and_messages={
        K2_APPLICATION_ENDPOINT: [ABORT, CRITICAL_ABORT]
    })
class SignalHandler(AbstractExtension):
    pass
