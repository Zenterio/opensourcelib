from zaf.application import ApplicationContext
from zaf.config.options import ConfigOptionId
from zaf.messages.message import EndpointId

REMOTE_ENABLED = ConfigOptionId(
    'remote.enabled',
    'Enabled remote messagebus interface',
    option_type=bool,
    default=False,
    hidden=True,
    application_contexts=ApplicationContext.EXTENDABLE)

REMOTE_PORT = ConfigOptionId(
    'remote.port',
    'The port to use for the remote interface',
    option_type=int,
    default=18861,
    hidden=True,
    application_contexts=ApplicationContext.EXTENDABLE)

REMOTE_CLIENT_ENABLED = ConfigOptionId(
    'remoteclient.enabled',
    'Enabled remote messagebus client',
    option_type=bool,
    default=False,
    hidden=True,
    application_contexts=ApplicationContext.EXTENDABLE)

REMOTE_CLIENT_PORT = ConfigOptionId(
    'remoteclient.port',
    'The port to use to connect to the remote interface',
    option_type=int,
    default=18861,
    hidden=True,
    application_contexts=ApplicationContext.EXTENDABLE)

REMOTE_CLIENT_HOST = ConfigOptionId(
    'remoteclient.host',
    'The host to use to connect to the remote interface',
    default='localhost',
    hidden=True,
    application_contexts=ApplicationContext.EXTENDABLE)

REMOTE_ENDPOINT = EndpointId('REMOTE_ENDPOINT', 'Endpoint for remote messagebus interface')
