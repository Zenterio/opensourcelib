import os

from zaf.application.context import ApplicationContext
from zaf.builtin.changelog import ChangeLogType
from zaf.config.options import ConfigOptionId
from zaf.config.types import Choice
from zaf.messages.message import EndpointId, MessageId

BEFORE_COMMAND = MessageId(
    'BEFORE_COMMAND', """
    Event triggered before the command has been started

    data: command name
    """)

AFTER_COMMAND = MessageId(
    'AFTER_COMMAND', """
    Event triggered after the command has been finished

    data: command name
    """)

APPLICATION_ENDPOINT = EndpointId('application', """
    The Zaf application endpoint
    """)

MESSAGEBUS_TIMEOUT = ConfigOptionId(
    'application.messagebus.timeout',
    'Specifies how long application should wait for the messagebus to finish on shutdown, in seconds',
    option_type=float,
    default=3,
    hidden=True,
    application_contexts=[ApplicationContext.EXTENDABLE])

APPLICATION_NAME = ConfigOptionId(
    'application.name', 'Name of the application', application_contexts=ApplicationContext.INTERNAL)
APPLICATION_ROOT = ConfigOptionId(
    'application.root',
    'The root package of the application',
    application_contexts=ApplicationContext.INTERNAL)
ENTRYPOINT_NAME = ConfigOptionId(
    'application.entrypoint',
    'Name of the entrypoint',
    application_contexts=ApplicationContext.INTERNAL)
APPLICATION_VERSION = ConfigOptionId(
    'application.version',
    'Version of the application',
    application_contexts=ApplicationContext.INTERNAL)
APPLICATION_CONTEXT = ConfigOptionId(
    'application.context',
    'The application context for the application',
    option_type=Choice([item.name for item in list(ApplicationContext)]),
    default='EXTENDABLE',
    transform=ApplicationContext.__getitem__,
    application_contexts=ApplicationContext.INTERNAL)
APPLICATION_CHANGELOG_TYPE = ConfigOptionId(
    'application.changelog.type',
    'Changelog type for this application',
    option_type=Choice([item.name for item in list(ChangeLogType)]),
    default='NONE',
    transform=ChangeLogType.__getitem__,
    application_contexts=ApplicationContext.INTERNAL)
CWD = ConfigOptionId(
    'cwd',
    'Current working directory',
    default=os.getcwd(),
    application_contexts=ApplicationContext.INTERNAL)
