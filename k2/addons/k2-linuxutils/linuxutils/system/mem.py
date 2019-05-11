import logging
import re

from zaf.component.decorator import component, requires
from zaf.config.options import ConfigOption, ConfigOptionId
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name
from zaf.messages.decorator import callback_dispatcher

from k2.cmd.run import RUN_COMMAND
from k2.sut import SUT
from monitor import MONITOR_ENDPOINT, PERFORM_MEASUREMENT

logger = logging.getLogger(get_logger_name('k2', 'monitor', 'sysmem'))
logger.addHandler(logging.NullHandler())


class SystemMemoryMonitorError(Exception):
    pass


@component
@requires(exec='Exec', can=['telnet'])
class SystemMemoryUsageCollector(object):
    """Collect system memory usage statistics by reading /proc/meminfo."""

    def __init__(self, exec):
        self._exec = exec
        self._matcher = re.compile(
            r'^MemFree:\s+(?P<free>\d+)|^Buffers:\s+(?P<buffers>\d+)|^Cached:\s+(?P<cached>\d+)',
            re.MULTILINE)

    def collect(self):
        try:
            data = self._exec.send_line('cat /proc/meminfo', timeout=5)
        except Exception as e:
            raise SystemMemoryMonitorError('Could not collect system memory usage data') from e

        try:
            result = {
                k: int(v)
                for match in self._matcher.finditer(data) for k, v in match.groupdict().items()
                if v is not None
            }
            if not result:
                raise SystemMemoryMonitorError('No system memory usage data found')
        except Exception as e:
            raise SystemMemoryMonitorError('Could not parse system memory usage data') from e

        return result


SYSTEM_MEMORY_USAGE_MONITOR_ENABLED = ConfigOptionId(
    'monitors.sysmem.enabled',
    'Should the system memory usage monitor be enabled',
    at=SUT,
    option_type=bool,
    default=True)


@CommandExtension(
    name='linuxmonitor',
    extends=[RUN_COMMAND],
    config_options=[
        ConfigOption(SUT, required=True, instantiate_on=True),
        ConfigOption(SYSTEM_MEMORY_USAGE_MONITOR_ENABLED, required=True)
    ],
    groups=['monitor'],
    activate_on=[SYSTEM_MEMORY_USAGE_MONITOR_ENABLED],
)
class SystemMemoryUsageMonitor(AbstractExtension):
    """
    Collects system memory usage statistics by reading /proc/meminfo.

    For more information about the /proc/stat filesystem, please see:
    http://man7.org/linux/man-pages/man5/proc.5.html

    When enabled, this addon produces the following metrics series:
      * system.memory.free
      * system.memory.buffers
      * system.memory.cached

    Each of the above metrics are measured in KB.
    """

    def __init__(self, config, instances):
        self._entity = instances[SUT]

    @callback_dispatcher([PERFORM_MEASUREMENT], [MONITOR_ENDPOINT], entity_option_id=SUT)
    @requires(collector=SystemMemoryUsageCollector, scope='dispatcher')
    @requires(create_metric='CreateSeriesMetric', scope='dispatcher')
    def handle_collect_system_memory_usage(self, message, collector, create_metric):
        for name, value in collector.collect().items():
            create_metric('system.memory.{name}'.format(name=name), value)
