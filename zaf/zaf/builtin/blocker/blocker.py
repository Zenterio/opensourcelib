"""
Used to block ZAF execution by registering a CallbackDispatcher on an event.

The functionality is controlled by a set of messages.
Start the blocking by sending the :ref:`message-START_BLOCKING_ON_MESSAGE` message as a request with the
message data being a StartBlockingInfo with the message_id, endpoint_id, entity describing which
message that should be blocked on, as well as the timeout (seconds as float) of the *blocking*.
The return value is an ID and following messages for this *blocking* must be sent with entity=ID.

When the blocking message is received by the blocker then a :ref:`message-BLOCKING_STARTED` is sent.

If the *blocking* isn't stopped before the timeout then a :ref:`message-BLOCKING_TIMED_OUT` is sent.

To stop the *blocking* send the :ref:`message-STOP_BLOCKING_ON_MESSAGE`.
When the *blocking* is stopped this way a :ref:`message-BLOCKING_COMPLETED` will be sent out.

A blocking on the initialization of ZAF can be configured using the config options :ref:`option-blocker.init.enabled`
and :ref:`option-blocker.init.timeout`.
This can be used to wait with the start of ZAF until an outside user is ready for it, for example until
a user has connected with the :ref:`extension-remote` client.
The ID for this blocking is hard coded to *init*.
Similarly, the config options :ref:`option-blocker.exit.enabled` and :ref:`option-blocker.exit.timeout`
can be used to wait for ZAF to exit. The ID for this blocking is hard coded to *exit*.
"""

import functools
import logging
from uuid import uuid4

from zaf.application import AFTER_COMMAND, APPLICATION_ENDPOINT, BEFORE_COMMAND
from zaf.builtin.blocker import BLOCKER_ENABLED, BLOCKER_ENDPOINT, BLOCKER_EXIT_ENABLED, \
    BLOCKER_EXIT_TIMEOUT, BLOCKER_INIT_ENABLED, BLOCKER_INIT_TIMEOUT, BLOCKING_COMPLETED, \
    BLOCKING_STARTED, BLOCKING_TIMED_OUT, START_BLOCKING_ON_MESSAGE, STOP_BLOCKING_ON_MESSAGE, \
    StartBlockingInfo
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, FrameworkExtension
from zaf.messages.dispatchers import CallbackDispatcher, LocalMessageQueue, SequentialDispatcher

logger = logging.getLogger(__name__)


class BlockerState(object):

    def __init__(self, id, blocker, blocking_dispatcher):
        self.id = id
        self.blocker = blocker
        self.blocking_dispatcher = blocking_dispatcher
        self.started = False

    def set_started(self):
        self.started = True

    def cleanup(self):
        logger.debug('cleaning up blocker dispatchers')
        self.blocker.__exit__(None, None, None)
        self.blocking_dispatcher.destroy()
        logger.debug('blocker dispatchers cleaned up')


@FrameworkExtension(
    'blocker',
    config_options=[
        ConfigOption(BLOCKER_ENABLED, required=True),
        ConfigOption(BLOCKER_INIT_ENABLED, required=True),
        ConfigOption(BLOCKER_INIT_TIMEOUT, required=True),
        ConfigOption(BLOCKER_EXIT_ENABLED, required=True),
        ConfigOption(BLOCKER_EXIT_TIMEOUT, required=True),
    ],
    endpoints_and_messages={
        BLOCKER_ENDPOINT: [
            START_BLOCKING_ON_MESSAGE, STOP_BLOCKING_ON_MESSAGE, BLOCKING_STARTED,
            BLOCKING_TIMED_OUT, BLOCKING_COMPLETED
        ]
    })
class Blocker(AbstractExtension):
    """Blocker implementation."""

    def __init__(self, config, instances):
        self._enabled = config.get(BLOCKER_ENABLED)

        self._init_enabled = config.get(BLOCKER_INIT_ENABLED)
        self._init_timeout = config.get(BLOCKER_INIT_TIMEOUT)
        self._exit_enabled = config.get(BLOCKER_EXIT_ENABLED)
        self._exit_timeout = config.get(BLOCKER_EXIT_TIMEOUT)

        self._ongoing_blockers = {}

        self._start_blocking_dispatcher = None
        self._after_command_dispatcher = None

    def register_dispatchers(self, messagebus):
        if self._enabled:
            self._messagebus = messagebus
            self._start_blocking_dispatcher = SequentialDispatcher(messagebus, self.start_blocking)
            self._start_blocking_dispatcher.register(
                [START_BLOCKING_ON_MESSAGE], [BLOCKER_ENDPOINT])

            self._after_command_dispatcher = CallbackDispatcher(messagebus, self.after_command)
            self._after_command_dispatcher.register([AFTER_COMMAND], [APPLICATION_ENDPOINT])

            if self._init_enabled:
                print('INITING BLOCKER')
                self._start_blocking(
                    StartBlockingInfo(
                        BEFORE_COMMAND,
                        APPLICATION_ENDPOINT,
                        entity=None,
                        timeout=self._init_timeout),
                    id='init',
                    priority=100)

            if self._exit_enabled:
                print('EXITING BLOCKER')
                self._start_blocking(
                    StartBlockingInfo(
                        AFTER_COMMAND,
                        APPLICATION_ENDPOINT,
                        entity=None,
                        timeout=self._exit_timeout),
                    id='exit',
                    priority=100)

    def start_blocking(self, message):
        return self._start_blocking(blocking_info=message.data)

    def _start_blocking(self, blocking_info, id=None, priority=0):
        logger.debug('Starting to block on {data}'.format(data=blocking_info))

        def blocking_callback(id, timeout, message):
            """Block until STOP_BLOCKING_ON_MESSAGE is received in the blocker LocalMessageQueue."""
            logger.debug(
                'Blocker received message {name}, waiting for stop blocking for {timeout} seconds'.
                format(name=message.message_id.name, timeout=timeout))
            self._messagebus.trigger_event(BLOCKING_STARTED, BLOCKER_ENDPOINT, entity=id)
            blocker_state = self._ongoing_blockers[id]
            blocker_state.set_started()
            try:
                blocker_state.blocker.get(timeout=timeout)
                logger.debug(
                    'Blocker no longer blocks on message {name}'.format(
                        name=message.message_id.name))
                self._messagebus.trigger_event(BLOCKING_COMPLETED, BLOCKER_ENDPOINT, entity=id)
            except Exception:
                logger.warning(
                    'Blocker timed out when blocking on message {name}'.format(
                        name=message.message_id.name))
                self._messagebus.trigger_event(BLOCKING_TIMED_OUT, BLOCKER_ENDPOINT, entity=id)
            finally:
                blocker_state.cleanup()
                del self._ongoing_blockers[id]

        # Creates an ID for the specific instance of blocking. Is used in all messages communication.
        if id is None:
            id = str(uuid4())

        # Creates a blocking message queue.
        # This can be used to block until a STOP_BLOCKING_ON_MESSAGE is received with entity=id.
        blocker = LocalMessageQueue(self._messagebus, [STOP_BLOCKING_ON_MESSAGE], entities=[id])

        # Starts the blocker message queue
        blocker.__enter__()

        # Creates the blocking dispatcher that listens to the message described in the received StartBlockingInfo
        blocking_dispatcher = CallbackDispatcher(
            self._messagebus, functools.partial(blocking_callback, id, blocking_info.timeout), priority)
        blocking_dispatcher.register(
            message_ids=[blocking_info.message_id],
            endpoint_ids=[blocking_info.endpoint_id] if blocking_info.endpoint_id else None,
            entities=[blocking_info.entity] if blocking_info.entity else None)

        self._ongoing_blockers[id] = BlockerState(id, blocker, blocking_dispatcher)

        # Return the id so that the user can use it when sending STOP_BLOCKING_ON_MESSAGE
        # or to listen for BLOCKING_STARTED, BLOCKING_COMPLETED and/or BLOCKING_TIMED_OUT
        return id

    def after_command(self, message):
        self.destroy()

    def destroy(self):
        try:
            if self._start_blocking_dispatcher:
                self._start_blocking_dispatcher.destroy()

            if self._after_command_dispatcher:
                self._after_command_dispatcher.destroy()

            for id, blocker_state in self._ongoing_blockers.items():
                if blocker_state.started:
                    # Just puts something in the blockers queue to make it stop
                    # If a blocker is running at destroy time we don't want to raise exceptions
                    logger.debug('Deregister blocker dispatcher by adding stop message')
                    blocker_state.blocker.handle_message('stop')
                else:
                    blocker_state.cleanup()
                    del self._ongoing_blockers[id]
        finally:
            self._start_blocking_dispatcher = None
            self._after_command_dispatcher = None
            self._ongoing_blockers = {}
