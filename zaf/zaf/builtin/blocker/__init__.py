from collections import namedtuple

from zaf.application.context import ApplicationContext
from zaf.config.options import ConfigOptionId
from zaf.messages.message import EndpointId, MessageId

BLOCKER_ENABLED = ConfigOptionId(
    'blocker.enabled',
    'Enables the possibility to block on messages',
    option_type=bool,
    default=False,
    hidden=True,
    application_contexts=ApplicationContext.EXTENDABLE)

BLOCKER_INIT_ENABLED = ConfigOptionId(
    'blocker.init.enabled',
    'Enable blocking on initialization of zaf. ID for blocking is "init".',
    option_type=bool,
    default=False,
    hidden=True,
    application_contexts=ApplicationContext.EXTENDABLE)

BLOCKER_INIT_TIMEOUT = ConfigOptionId(
    'blocker.init.timeout',
    'Timeout for init blocking.',
    option_type=float,
    default=5.0,
    hidden=True,
    application_contexts=ApplicationContext.EXTENDABLE)

BLOCKER_ENDPOINT = EndpointId('blocker', 'Endpoint for blocker extension')

StartBlockingInfo = namedtuple(
    'StartBlockingInfo', ['message_id', 'endpoint_id', 'entity', 'timeout'])

START_BLOCKING_ON_MESSAGE = MessageId(
    'START_BLOCKING_ON_MESSAGE', """
    Starts blocking on message described by the message data.
    Send as request to receive an ID that should be used as entity
    when sending the STOP_BLOCKING_ON_MESSAGE

    data: StartBlockingInfo
    """)

STOP_BLOCKING_ON_MESSAGE = MessageId(
    'STOP_BLOCKING_ON_MESSAGE', """
    Stop blocking on message.
    This message should be sent with the ID that was received from START_BLOCKING_ON_MESSAGE as the entity.

    data: None
    """)

BLOCKING_STARTED = MessageId(
    'BLOCKING_STARTED', """
    Event that is triggered when message that should be blocked on has been received.
    This message is sent with the ID returned by START_BLOCKING_ON_MESSAGE as the entity.

    data: None
    """)

BLOCKING_COMPLETED = MessageId(
    'BLOCKING_COMPLETED', """
    Event sent if the blocking has completed without problems.
    This message is sent with the ID returned by START_BLOCKING_ON_MESSAGE as the entity.

    data: None
    """)

BLOCKING_TIMED_OUT = MessageId(
    'BLOCKING_TIMED_OUT', """
    Event sent if the blocking timeed out.
    This message is sent with the ID returned by START_BLOCKING_ON_MESSAGE as the entity.

    data: None
    """)
