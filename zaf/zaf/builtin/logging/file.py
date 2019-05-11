"""
Provides functionality to configure the logging to write to files.

It allows for very general configuration to redirect the specific loggers and the level of each logger.
It also allows for rotating log files on specific *scopes* that can be defined by other extensions.

Example of how to configure a simple log file::

    log.file.ids: [file1]                   # Creates a new log file ID

    log.file.file1.log.level: debug         # Sets the default log level to debug

    log.file.file1.loggers: [zaf.runner]     # Redirects the zaf.runner with the
                                            # default log level to the file

    log.file.file1.path: ${log.dir}/f1.log  # Creates the file in the directory
                                            # defined by the log.dir config

    log.file.file1.warning: [zaf.messagebus] # Redirects the zaf.messagebus logger
                                            # to the file with the warning level
                                            # instead of the default log level

Example of how to configre a rotating log file::

    log.file.ids: [file2]                 # Creates a new log file ID

    log.file.file2.log.level: debug       # Sets the default log level to debug

    log.file.file2.loggers: [zaf]          # Redirects the zaf logger to the file

    log.file.file2.rotate.scope: testcase # Rotate on the testcase scope

    log.file.file2.path: f2_{scope}.log   # Defines the file using the {scope}
                                          # variable that will be named when
                                          # entering the scope

    log.file.file2.rotate.deleteforresults: [PASSED]
                                          # Deletes the file if the result of the
                                          # scope matches one of the values.
                                          # Result names are defined by the
                                          # creator of the scope

"""
import logging
import os
from logging.handlers import BaseRotatingHandler

from zaf.builtin.logging.utils import CustomJSONFormatter, Filter, combine_loggers
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, FrameworkExtension, get_logger_name
from zaf.messages.dispatchers import SequentialDispatcher

from . import ENTER_LOG_SCOPE, EXIT_LOG_SCOPE, LOG_END_POINT, LOG_FILE_DEBUG, LOG_FILE_ENABLED, \
    LOG_FILE_ERROR, LOG_FILE_FORMAT, LOG_FILE_INFO, LOG_FILE_LEVEL, LOG_FILE_LOGGERS, \
    LOG_FILE_PATH, LOG_FILE_ROTATE_DELETE_RESULTS, LOG_FILE_ROTATE_SCOPE, LOG_FILE_TYPE, \
    LOG_FILE_WARNING, LOG_FILES, LOG_LEVEL_OFF
from .logging import map_level

logger = logging.getLogger(get_logger_name('zaf', 'filelogger'))
logger.addHandler(logging.NullHandler())


@FrameworkExtension(
    name='filelogger',
    load_order=101,
    config_options=[
        ConfigOption(LOG_FILES, required=False, instantiate_on=True),
        ConfigOption(LOG_FILE_ENABLED, required=True),
        ConfigOption(LOG_FILE_PATH, required=True),
        ConfigOption(LOG_FILE_LOGGERS, required=True),
        ConfigOption(LOG_FILE_LEVEL, required=True),
        ConfigOption(LOG_FILE_FORMAT, required=True),
        ConfigOption(LOG_FILE_ROTATE_SCOPE, required=False),
        ConfigOption(LOG_FILE_ROTATE_DELETE_RESULTS, required=False),
        ConfigOption(LOG_FILE_DEBUG, required=False),
        ConfigOption(LOG_FILE_INFO, required=False),
        ConfigOption(LOG_FILE_WARNING, required=False),
        ConfigOption(LOG_FILE_ERROR, required=False),
        ConfigOption(LOG_FILE_TYPE, required=False)
    ],
    endpoints_and_messages={LOG_END_POINT: [ENTER_LOG_SCOPE, EXIT_LOG_SCOPE]},
    groups=['logging'])
class FileLogger(AbstractExtension):
    """
    Configures log files.

    The log files can either be configured as single files or rotated on scope changes.
    When a file uses rotation on scope it will listen to ENTER_LOG_SCOPE and EXIT_LOG_SCOPE
    requests and if the scope id matches the wanted scope then the log files will be changed.
    """

    def __init__(self, config, instances):
        self.dispatcher = None
        self.enabled = config.get(LOG_FILE_ENABLED)
        if self.enabled:
            self.path = config.get(LOG_FILE_PATH)

            self.rotate_path = self.path
            self.log_level = map_level(config.get(LOG_FILE_LEVEL))
            self.rotate_scope = config.get(LOG_FILE_ROTATE_SCOPE)
            self.rotate_delete_results = config.get(LOG_FILE_ROTATE_DELETE_RESULTS)
            exclude_dict = {}

            for logger in config.get(LOG_FILE_LOGGERS):
                if self.log_level:
                    exclude_dict[logger] = self.log_level
                else:
                    exclude_dict[logger] = LOG_LEVEL_OFF

            for logger_name in config.get(LOG_FILE_ERROR):
                exclude_dict[logger_name] = logging.ERROR

            for logger_name in config.get(LOG_FILE_WARNING):
                exclude_dict[logger_name] = logging.WARNING

            for logger_name in config.get(LOG_FILE_INFO):
                exclude_dict[logger_name] = logging.INFO

            for logger_name in config.get(LOG_FILE_DEBUG):
                exclude_dict[logger_name] = logging.DEBUG

            log_format = config.get(LOG_FILE_FORMAT)
            log_type = config.get(LOG_FILE_TYPE)

            log_dir = os.path.dirname(self.path)
            if log_dir != '':
                os.makedirs(os.path.dirname(self.path), exist_ok=True)

            if self.rotate_scope:
                self.default_path = self.path.format(scope=self.rotate_scope)
                self.log_handler = ScopedRotatingLogHandler(self.path, self.rotate_scope)
                self.log_handler.setLevel(LOG_LEVEL_OFF)
            else:
                self.log_handler = logging.FileHandler(self.path, 'w', delay=True)
            if log_type == 'json':
                formatter = CustomJSONFormatter()
            else:
                formatter = logging.Formatter(log_format)
            self.log_handler.setFormatter(formatter)
            self.log_handler.addFilter(Filter(exclude_dict))

            for logger_name in combine_loggers(exclude_dict.keys()):
                logger = logging.getLogger(logger_name)
                logger.addHandler(self.log_handler)
                logger.setLevel(logging.DEBUG)

    def register_dispatchers(self, messagebus):
        if self.enabled and self.rotate_scope:
            self.dispatcher = SequentialDispatcher(
                messagebus, self.handle_rotate_scope_change_messages)
            self.dispatcher.register([ENTER_LOG_SCOPE, EXIT_LOG_SCOPE], [LOG_END_POINT])

    def handle_rotate_scope_change_messages(self, message):
        scope = message.data
        if scope.id == self.rotate_scope:
            if message.message_id == ENTER_LOG_SCOPE:
                logger.debug(
                    'Entering log scope {scope_id} with name {scope_name}'.format(
                        scope_id=scope.id, scope_name=scope.name))
                self.log_handler.setLevel(logging.NOTSET)

            elif message.message_id == EXIT_LOG_SCOPE:
                logger.debug(
                    'Exiting log scope {scope_id} with name {scope_name}'.format(
                        scope_id=scope.id, scope_name=scope.name))
                self.log_handler.setLevel(LOG_LEVEL_OFF)
                delete = self.rotate_delete_results is not None and scope.result in self.rotate_delete_results
                self.log_handler.exit_scope(scope.name, delete)

    def destroy(self):
        if self.enabled and self.rotate_scope:
            if self.dispatcher:
                self.dispatcher.destroy()

            self.log_handler.cleanup()


class ScopedRotatingLogHandler(BaseRotatingHandler):
    """
    Rotate files when exiting a scope.

    This expects a path with a '{scope}' formatting string to be able to name the files.
    It also has the possibility to delete files when rotating.
    """

    def __init__(self, path_template, scope_id):
        """
        Create the logger using the scope_id to create a default file path.

        :param path_template: the template with {scope} to generate file names
        :param scope_id: the id of the scope that will be used to create the default file path
        """
        self.path_template = path_template
        self.scope_id = scope_id
        self.default_path = path_template.format(scope=scope_id)
        BaseRotatingHandler.__init__(self, self.default_path, 'w', delay=True)
        self.exiting_scope = None
        self.delete_next_file_after_rollover = False

    def doRollover(self):
        self.acquire()
        try:
            if self.stream:
                self.stream.close()
                self.stream = None

            path = self.path_template.format(scope=self.exiting_scope)
            self.rotate(self.default_path, path)

            if self.delete_next_file_after_rollover:
                logger.debug(
                    'Deleting log file for log scope {scope_id} with name {scope_name}'.format(
                        scope_id=self.scope_id, scope_name=self.exiting_scope))
                os.remove(path)

            self.delete_next_file_after_rollover = False
            self.stream = self._open()
        finally:
            self.release()

    def shouldRollover(self, record):
        return False

    def exit_scope(self, scope_name, delete_file=False):
        """
        Exit the scope and triggers a rollover.

        :param scope_name: the new scope name that will be used to name the file
        :param delete_file: if True the file will be deleted after rollover
        """
        self.delete_next_file_after_rollover = delete_file
        self.exiting_scope = scope_name
        self.doRollover()

    def cleanup(self):
        """Clean up the default file."""
        if os.path.exists(self.default_path):
            os.remove(self.default_path)
