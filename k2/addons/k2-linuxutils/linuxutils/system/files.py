import logging
import re
from collections import Counter

from zaf.component.decorator import component, requires
from zaf.config.options import ConfigOption, ConfigOptionId
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name
from zaf.messages.decorator import callback_dispatcher

from k2.cmd.run import RUN_COMMAND
from k2.sut import SUT
from monitor import MONITOR_ENDPOINT, PERFORM_MEASUREMENT

logger = logging.getLogger(get_logger_name('k2', 'monitor', 'files'))
logger.addHandler(logging.NullHandler())


class SystemFilesMonitorError(Exception):
    pass


@component
@requires(exec='Exec', can=['telnet'])
class SystemFilesCollector(object):
    """Collect file usage data by reading the contents of /proc/sys/fs/file-nr."""

    def __init__(self, exec):
        self._exec = exec

    def collect(self):
        try:
            data = self._exec.send_line('cat /proc/sys/fs/file-nr', timeout=5)
            opened, _, max_allowed = tuple(re.split(r'\s+', data.strip()))
        except Exception as e:
            raise SystemFilesMonitorError('Could not collect file usage data') from e

        return Counter({'opened': int(opened), 'max_allowed': int(max_allowed)})


FILES_MONITOR_ENABLED = ConfigOptionId(
    'monitors.files.enabled',
    'Should the file usage monitor be enabled',
    at=SUT,
    option_type=bool,
    default=True)


@CommandExtension(
    name='linuxmonitor',
    extends=[RUN_COMMAND],
    config_options=[
        ConfigOption(SUT, required=True, instantiate_on=True),
        ConfigOption(FILES_MONITOR_ENABLED, required=True)
    ],
    groups=['monitor'],
    activate_on=[FILES_MONITOR_ENABLED],
)
class SystemFileUsageMonitor(AbstractExtension):
    """
    Collects file usage statistics by reading the contents of /proc/sys/fs/file-nr.

    For more information about the /proc/sys filesystem, please see:
    http://man7.org/linux/man-pages/man5/proc.5.html

    When enabled, this addon produces the following metrics series:
      * system.files.opened
      * system.files.max_allowed

    Each of the above metrics represents the number of files.
    """

    def __init__(self, config, instances):
        self._entity = instances[SUT]

    @callback_dispatcher([PERFORM_MEASUREMENT], [MONITOR_ENDPOINT], entity_option_id=SUT)
    @requires(collector=SystemFilesCollector, scope='dispatcher')
    @requires(create_metric='CreateSeriesMetric', scope='dispatcher')
    def handle_collect_files_usage(self, message, collector, create_metric):
        for name, value in collector.collect().items():
            create_metric('system.files.{name}'.format(name=name), value)
