from collections import namedtuple

from zaf.application import ApplicationContext
from zaf.config.options import Choice, ConfigOptionId
from zaf.extensions import ENABLED_EXTENSIONS
from zaf.messages.message import EndpointId, MessageId

LOG_LEVEL_CHOICE = Choice(['debug', 'info', 'warning', 'error', 'off', 'global'])
LOG_TYPE_CHOICE = Choice(['text', 'json'])
LOG_LEVEL_OFF = 100
DEFAULT_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

LOG_LEVEL = ConfigOptionId(
    'log.level', 'The global log level', default='info', option_type=LOG_LEVEL_CHOICE)

LOG_FORMAT = ConfigOptionId(
    'log.format', 'The log format string', default=DEFAULT_LOG_FORMAT, hidden=True)

LOG_DIR = ConfigOptionId('log.dir', 'The log directory', default='${output.dir}/logs')

LOG_DEBUG = ConfigOptionId(
    'log.debug', 'Set named logger to log at debug level', default=[], multiple=True, hidden=True)

LOG_INFO = ConfigOptionId(
    'log.info', 'Set named logger to log at info level', default=[], multiple=True, hidden=True)

LOG_WARNING = ConfigOptionId(
    'log.warning',
    'Set named logger to log at warning level',
    default=[],
    multiple=True,
    hidden=True)

LOG_ERROR = ConfigOptionId(
    'log.error', 'Set named logger to log at error level', default=[], multiple=True, hidden=True)

EXTENSION_LOG_LEVEL = ConfigOptionId(
    'log.level',
    'The log level used for the extension',
    default='global',
    option_type=LOG_LEVEL_CHOICE,
    at=ENABLED_EXTENSIONS,
    hidden=True,
    application_contexts=ApplicationContext.EXTENDABLE)

LOG_FILES = ConfigOptionId(
    'ids', 'IDs of the log files to create', multiple=True, entity=True, namespace='log.file')

LOG_FILE_ENABLED = ConfigOptionId(
    'enabled', 'Enable the log file', option_type=bool, at=LOG_FILES, default=True, hidden=True)

LOG_FILE_PATH = ConfigOptionId(
    'path',
    'The path for the log file. If rotate is active for this log file then the path should contain {scope} '
    'that will be filled in with the name of the scope',
    at=LOG_FILES,
    hidden=True)

LOG_FILE_LOGGERS = ConfigOptionId(
    'loggers',
    'The loggers that should be logged to the log file',
    at=LOG_FILES,
    multiple=True,
    hidden=True)

LOG_FILE_LEVEL = ConfigOptionId(
    'log.level',
    'The default log level used for the log file',
    option_type=LOG_LEVEL_CHOICE,
    default='info',
    at=LOG_FILES,
    hidden=True)

LOG_FILE_FORMAT = ConfigOptionId(
    'format',
    'The log format string used for the log file',
    default=DEFAULT_LOG_FORMAT,
    at=LOG_FILES,
    hidden=True)

LOG_FILE_ROTATE_SCOPE = ConfigOptionId(
    'rotate.scope', 'The scope to rotate the log file on', at=LOG_FILES, hidden=True)

LOG_FILE_ROTATE_DELETE_RESULTS = ConfigOptionId(
    'rotate.deleteforresults',
    'The log file will not be kept if the scope result matches one of these values',
    at=LOG_FILES,
    multiple=True,
    hidden=True)

LOG_FILE_DEBUG = ConfigOptionId(
    'debug',
    'Set named logger to log at debug level to the file',
    default=[],
    at=LOG_FILES,
    multiple=True,
    hidden=True)

LOG_FILE_INFO = ConfigOptionId(
    'info',
    'Set named logger to log at info level to the file',
    default=[],
    at=LOG_FILES,
    multiple=True,
    hidden=True)

LOG_FILE_WARNING = ConfigOptionId(
    'warning',
    'Set named logger to log at warning level to the file',
    default=[],
    at=LOG_FILES,
    multiple=True,
    hidden=True)

LOG_FILE_ERROR = ConfigOptionId(
    'error',
    'Set named logger to log at error level to the file',
    default=[],
    at=LOG_FILES,
    multiple=True,
    hidden=True)

LOG_FILE_TYPE = ConfigOptionId(
    'type',
    'What type of log file to write. Choose from text or json',
    option_type=LOG_TYPE_CHOICE,
    default='text',
    at=LOG_FILES,
    hidden=True)

LOG_END_POINT = EndpointId('logging', 'The Logging endpoint')

ENTER_LOG_SCOPE = MessageId(
    'ENTER_LOG_SCOPE', """
    Entering log scope

    data: LogScopeMessageData
    """)

EXIT_LOG_SCOPE = MessageId(
    'EXIT_LOG_SCOPE', """
    Exiting log scope

    data: LogScopeMessageData
    """)

InternalLogScopeMessageData = namedtuple('InternalLogScopeMessageData', ['id', 'name', 'result'])


class LogScopeMessageData(InternalLogScopeMessageData):
    __slots__ = ()

    def __new__(cls, id, name, result=None):
        """
        Create a new LogScopeMessageData.

        :param id: the id of the scope
        :param name: the current name used for the scope
        :param result: String that can be included in EXIT_LOG_SCOPE to indicate the result of the scope
                       Can be used to decide if the log should be kept or not
        """
        return super().__new__(cls, id, name, result)
