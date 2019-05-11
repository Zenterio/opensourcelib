import logging
import os
import signal
import subprocess
from collections import defaultdict, namedtuple

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

SignalHandler = namedtuple('SignalHandler', ['handle', 'original_signal_handler'])


class SignalListener(object):

    def __init__(self):
        self.occurred = False


class DockerSignalHandler(object):

    def __init__(self, container_name):
        self._container = Container(container_name)

        self._handlers = {
            signal.SIGINT:
            SignalHandler(self.handle_int_quit_abrt_term, signal.getsignal(signal.SIGINT)),
            signal.SIGQUIT:
            SignalHandler(self.handle_int_quit_abrt_term, signal.getsignal(signal.SIGQUIT)),
            signal.SIGABRT:
            SignalHandler(self.handle_int_quit_abrt_term, signal.getsignal(signal.SIGABRT)),
            signal.SIGTERM:
            SignalHandler(self.handle_int_quit_abrt_term, signal.getsignal(signal.SIGTERM)),
            signal.SIGTSTP:
            SignalHandler(self.handle_sigtstp, signal.getsignal(signal.SIGTSTP)),
            signal.SIGCONT:
            SignalHandler(self.handle_sigcont, signal.getsignal(signal.SIGCONT)),
        }

        self._listeners = defaultdict(list)

    def add_listener(self, sig, listener):
        self._listeners[sig].append(listener)

    def remove_listener(self, sig, listener):
        self._listeners[sig].remove(listener)

    def __enter__(self):
        for sig, handler in self._handlers.items():
            signal.signal(sig, handler.handle)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for sig, handler in self._handlers.items():
            signal.signal(sig, handler.original_signal_handler)

    def handle_int_quit_abrt_term(self, sig, frame):
        logger.debug('Received signal {sig}'.format(sig=sig))
        self._container.kill()

        # Reset original signal handler and triggering signal again
        signal.signal(sig, self._handlers[sig].original_signal_handler)
        os.kill(os.getpid(), sig)

    def handle_sigtstp(self, sig, frame):
        logger.debug('Received signal SIGTSTP')
        self._container.pause()

        # Forwarding to original signal handler but uses SIGSTOP instead of SIGTSTP
        # to not have to keep track of which signal handler is registered.
        os.kill(os.getpid(), signal.SIGSTOP)

    def handle_sigcont(self, sig, frame):
        logger.debug('Received signal SIGCONT')

        for listener in self._listeners[sig]:
            listener.occurred = True

        self._container.unpause()


class Container(object):

    def __init__(self, name):
        self._name = name

    def kill(self):
        logger.info('Killing container {name}'.format(name=self._name))

        command = ['docker', 'rm', '-f', self._name]
        logger.debug("Sending command '{command}'".format(command=' '.join(command)))
        try:
            output = subprocess.check_output(command, shell=False, universal_newlines=True)
            logger.debug('Command output: {output}'.format(output=output))
        except Exception as e:
            logger.warning(
                "Failed to kill docker container '{name}': {msg}".format(
                    name=self._name, msg=str(e)))

    def pause(self):
        logger.info('Pausing container {name}'.format(name=self._name))

        command = ['docker', 'pause', self._name]
        logger.debug("Sending command '{command}'".format(command=' '.join(command)))
        try:
            output = subprocess.check_output(command, shell=False, universal_newlines=True)
            logger.debug('Command output: {output}'.format(output=output))
        except Exception as e:
            logger.warning(
                "Failed to pause docker container '{name}': {msg}".format(
                    name=self._name, msg=str(e)))

    def unpause(self):
        logger.info('Unpausing container {name}'.format(name=self._name))

        command = ['docker', 'unpause', self._name]
        logger.debug("Sending command '{command}'".format(command=' '.join(command)))
        try:
            output = subprocess.check_output(command, shell=False, universal_newlines=True)
            logger.debug('Command output: {output}'.format(output=output))
        except Exception as e:
            logger.warning(
                "Failed to unpause docker container '{name}': {msg}".format(
                    name=self._name, msg=str(e)))
