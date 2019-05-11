import abc
import logging
import re

from zaf.config import ConfigException
from zaf.extensions.extension import AbstractExtension, get_logger_name
from zaf.messages.dispatchers import CallbackDispatcher

from metrics import GENERATE_METRICS_REPORT

logger = logging.getLogger(get_logger_name('k2', 'metrics.reporter'))
logger.addHandler(logging.NullHandler())


class AbstractMetricsReportExtension(AbstractExtension, metaclass=abc.ABCMeta):

    def __init__(self, config, instances):
        self._generate_metrics_report_dispatcher = None

    def register_dispatchers(self, messagebus):
        self.messagebus = messagebus

        self._generate_metrics_report_dispatcher = CallbackDispatcher(
            messagebus, self._handle_generate_metrics_report_wrapper)
        self._generate_metrics_report_dispatcher.register([GENERATE_METRICS_REPORT])

    def _handle_generate_metrics_report_wrapper(self, message):
        try:
            self.handle_generate_metrics_report(message)
        except Exception:
            msg = 'Could not generate metrics report: {reporter}'.format(reporter=str(self))
            logger.debug(msg, exc_info=True)
            logger.warning(msg)

    @abc.abstractmethod
    def handle_generate_metrics_report(self, message):
        pass

    def destroy(self):
        if self._generate_metrics_report_dispatcher is not None:
            self._generate_metrics_report_dispatcher.destroy()

        self._generate_metrics_report_dispatcher = None

    def parse_regex_option(self, config, option):
        regex_string = config.get(option)
        if regex_string is None:
            return None
        else:
            try:
                return re.compile(regex_string)
            except re.error:
                raise ConfigException(
                    "Error parsing regex '{regex}' for config option '{option}'".format(
                        regex=config.get(option), option=option.key))
