import datetime
import logging
import time

from zaf.component.decorator import component, requires
from zaf.config.options import Choice, ConfigOption, ConfigOptionId
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name
from zaf.messages.decorator import callback_dispatcher
from zaf.messages.dispatchers import CallbackDispatcher, ConcurrentDispatcher, SequentialDispatcher
from zaf.messages.message import EndpointId, MessageId

from k2.cmd.run import RUN_COMMAND, RUN_COMMAND_ENDPOINT, TEST_RUN

logger = logging.getLogger(get_logger_name('k2', 'measureeventsandrequests'))
logger.addHandler(logging.NullHandler())


def to_dispatcher_constructor(dispatcher_type):
    if dispatcher_type is None:
        return None
    elif dispatcher_type == 'sequential':
        return SequentialDispatcher
    elif dispatcher_type == 'concurrent':
        return ConcurrentDispatcher
    elif dispatcher_type == 'callback':
        return CallbackDispatcher
    else:
        raise ValueError('invalid dispatcher type {type}'.format(type=dispatcher_type))


NUMBER_OF_MESSAGES = ConfigOptionId(
    'number.of.messages', 'Set the number of messages that should be sent', option_type=int)
DISPATCHER_TYPE = ConfigOptionId(
    'dispatcher.type',
    'The type of dispatcher',
    option_type=Choice(['sequential', 'concurrent', 'callback']),
    transform=to_dispatcher_constructor)
MESSAGE_TYPE = ConfigOptionId(
    'message.type', 'The type of message', option_type=Choice(['event', 'request']))
NUMBER_OF_DISPATCHERS = ConfigOptionId(
    'number.of.dispatchers',
    'Set the number of dispatchers that should receive the message',
    option_type=int,
    default=1)
HANDLER_TYPE = ConfigOptionId(
    'handler.type',
    'The type of handler',
    option_type=Choice(['no_component', 'one_component', 'transitive_components']))

MESSAGE = MessageId('MESSAGE', 'a message')
ENDPOINT = EndpointId('endpoint', 'an endpoint')


@component(name='Child', scope='session')
def child():
    yield 'child'
    pass


@component(name='Parent', scope='session')
@requires(child='Child', scope='session')
def parent(child):
    yield 'parent'
    pass


@CommandExtension(
    name='measureeventsandrequests',
    extends=[RUN_COMMAND],
    config_options=[
        ConfigOption(NUMBER_OF_MESSAGES, required=True),
        ConfigOption(DISPATCHER_TYPE, required=True),
        ConfigOption(MESSAGE_TYPE, required=True),
        ConfigOption(HANDLER_TYPE, required=True),
        ConfigOption(NUMBER_OF_DISPATCHERS, required=True),
    ],
    endpoints_and_messages={ENDPOINT: [MESSAGE]},
)
class MeasureEventsAndRequests(AbstractExtension):

    def __init__(self, config, instances):
        self._received = []
        self._number_of_messages = config.get(NUMBER_OF_MESSAGES)
        self._number_of_dispatchers = config.get(NUMBER_OF_DISPATCHERS)
        self._dispatcher_type = config.get(DISPATCHER_TYPE)
        self._message_type = config.get(MESSAGE_TYPE)
        self._handler_type = config.get(HANDLER_TYPE)

        self._messagebus = None
        self._dispatchers = []

    def register_dispatchers(self, messagebus):
        self._messagebus = messagebus

        for i in range(self._number_of_dispatchers):
            logger.info('registering to dispatcher {i}'.format(i=str(i)))
            dispatcher = self._dispatcher_type(messagebus, self.receiver(self._handler_type))
            self._dispatchers.append(dispatcher)
            dispatcher.register([MESSAGE], [ENDPOINT])

    def destroy(self):
        try:
            for dispatcher in self._dispatchers:
                dispatcher.destroy()
        finally:
            self._dispatchers = []

    @callback_dispatcher([TEST_RUN], [RUN_COMMAND_ENDPOINT])
    def run(self, message):
        logger.info('starting measurement run')
        futures = []

        start = datetime.datetime.now()
        for i in range(self._number_of_messages):
            if self._message_type == 'event':
                self._messagebus.trigger_event(MESSAGE, ENDPOINT)
            elif self._message_type == 'request':
                futures.append(self._messagebus.send_request(MESSAGE, ENDPOINT))

        logger.info('waiting for all messages to be received')
        while len(self._received) < self._number_of_messages * self._number_of_dispatchers:
            logger.info(
                'received {received} < {messages}*{dispatchers}'.format(
                    received=len(self._received),
                    messages=self._number_of_messages,
                    dispatchers=self._number_of_dispatchers))
            time.sleep(0.02)
        logger.info(
            'all messages received: {received} out of {expected}'.format(
                received=len(self._received),
                expected=self._number_of_messages * self._number_of_dispatchers))

        if futures:
            logger.info('waiting for all futures to be completed')
        for future in futures:
            future.wait(timeout=5)
        logger.info('all futures completed')

        stop = datetime.datetime.now()

        delta = (stop - start)
        print('time: {time}'.format(time=delta.seconds * 1000 + delta.microseconds // 1000))
        logger.info('measurement run completed')

    def receiver(self, handler_type):
        if handler_type == 'no_component':
            return self.receive
        elif handler_type == 'one_component':
            return self.receive_with_one_component
        elif handler_type == 'transitive_components':
            return self.receive_with_transitive_components
        else:
            raise Exception('invalid handler type {type}'.format(type=self._handler_type))

    def receive(self, message):
        self._received.append(message)
        for handler in logger.handlers:
            handler.flush()

    @requires(component='Child', scope='session')
    def receive_with_one_component(self, message, component):
        self._received.append(message)
        for handler in logger.handlers:
            handler.flush()

    @requires(component='Parent', scope='session')
    def receive_with_transitive_components(self, message, component):
        self._received.append(message)
        for handler in logger.handlers:
            handler.flush()
