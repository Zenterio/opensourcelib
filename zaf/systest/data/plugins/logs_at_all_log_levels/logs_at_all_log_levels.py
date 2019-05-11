import logging

from zaf.builtin.logging import LOG_END_POINT, LogScopeMessageData
from zaf.builtin.logging.file import ENTER_LOG_SCOPE, EXIT_LOG_SCOPE
from zaf.builtin.noop import NOOP_COMMAND
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension

from . import ERRORS_OPTION, ITERATIONS_OPTION

logger = logging.getLogger('logsatallloglevels')
logger.addHandler(logging.NullHandler())


@CommandExtension(
    name='logsatallloglevels',
    extends=[NOOP_COMMAND],
    config_options=[
        ConfigOption(ITERATIONS_OPTION, required=True),
        ConfigOption(ERRORS_OPTION, required=True),
    ],
)
class LogsAtAllLogLevels(AbstractExtension):

    def __init__(self, config, instances):
        self.iterations = config.get(ITERATIONS_OPTION)
        self.errors = config.get(ERRORS_OPTION)

    def register_dispatchers(self, messagebus):
        self.messagebus = messagebus

    def destroy(self):
        log_levels = (logging.CRITICAL, logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG)
        for i in range(self.iterations):
            self._enter_log_scope(i)
            for log_level in log_levels:
                logger.log(log_level, str(log_level))
            self._exit_log_scope(i)

    def _enter_log_scope(self, iteration):
        self.messagebus.send_request(
            ENTER_LOG_SCOPE,
            receiver_endpoint_id=LOG_END_POINT,
            data=LogScopeMessageData(id='iteration', name=iteration)).wait()

    def _exit_log_scope(self, iteration):
        result = 'OK' if self.errors <= 0 else 'ERROR'
        self.errors = self.errors - 1
        print(result)
        self.messagebus.send_request(
            EXIT_LOG_SCOPE,
            receiver_endpoint_id=LOG_END_POINT,
            data=LogScopeMessageData(id='iteration', name=iteration, result=result)).wait()
