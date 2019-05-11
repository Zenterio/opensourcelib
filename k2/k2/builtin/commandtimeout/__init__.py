from zaf.config.options import ConfigOptionId
from zaf.messages.message import EndpointId

COMMAND_TIMEOUT = ConfigOptionId(
    'command.timeout',
    'The timeout of the command (e.g. run), specified as [[hh:]mm:]ss',
    default=None,
)

COMMAND_TIMEOUT_EXIT_DELAY = ConfigOptionId(
    'command.timeout.exit.delay',
    'The delay in seconds before a hard exit will be performed instead of trying to '
    'terminate the command nicely.',
    default=60,
    option_type=int,
)

COMMAND_TIMEOUT_ENDPOINT = EndpointId('commandtimeout', 'Endpoint for the command timeout')
