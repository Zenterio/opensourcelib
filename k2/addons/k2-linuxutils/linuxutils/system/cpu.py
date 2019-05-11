import logging
import re
from collections import Counter

from zaf.component.decorator import component, requires
from zaf.config.options import ConfigOption, ConfigOptionId
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name
from zaf.messages.decorator import callback_dispatcher

from k2.cmd.run import RUN_COMMAND
from k2.sut import SUT, SUT_RESET_DONE
from monitor import MONITOR_ENDPOINT, PERFORM_MEASUREMENT

logger = logging.getLogger(get_logger_name('k2', 'monitor', 'cpu'))
logger.addHandler(logging.NullHandler())


class SystemCpuMonitorError(Exception):
    pass


@component
@requires(exec='Exec', can=['telnet'])
class SystemCpuTicksCollector(object):
    """Collect current CPU ticks statistics by reading the contents of /proc/stat."""

    def __init__(self, exec):
        self._exec = exec
        self._matcher = re.compile(r'cpu\s+(?P<user>\d+)\s+\d+\s+(?P<system>\d+)\s+(?P<idle>\d+)')

    def collect(self):
        try:
            data = self._exec.send_line('cat /proc/stat', timeout=5)
        except Exception as e:
            raise SystemCpuMonitorError('Could not collect CPU ticks data') from e

        match = self._matcher.search(data)
        if not match:
            raise SystemCpuMonitorError('Could not parse CPU ticks data')

        return Counter({k: int(v) for k, v in match.groupdict().items()})


@component
@requires(collector=SystemCpuTicksCollector)
class SystemCpuUsage(object):

    def __init__(self, collector):
        logger.debug('Collecting initial CPU ticks data')
        self._last_cpu_ticks = {'user': 0, 'system': 0, 'idle': 0}
        self._collector = collector

    def collect(self):
        current_cpu_ticks = self._collector.collect()
        difference = current_cpu_ticks.copy()
        difference.subtract(self._last_cpu_ticks)
        self._last_cpu_ticks = current_cpu_ticks
        return SystemCpuUsage.as_percentages(difference)

    @staticmethod
    def as_percentages(ticks):
        total_ticks = sum(ticks.values())

        def as_percent_of_total(name):
            if total_ticks > 0:
                return 100 * ticks[name] / total_ticks
            return 0

        return {
            'user': as_percent_of_total('user'),
            'system': as_percent_of_total('system'),
            'idle': as_percent_of_total('idle'),
        }


CPU_USAGE_MONITOR_ENABLED = ConfigOptionId(
    'monitors.cpu.enabled',
    'Should the CPU usage monitor be enabled',
    at=SUT,
    option_type=bool,
    default=True)


@CommandExtension(
    name='linuxmonitor',
    extends=[RUN_COMMAND],
    config_options=[
        ConfigOption(SUT, required=True, instantiate_on=True),
        ConfigOption(CPU_USAGE_MONITOR_ENABLED, required=True)
    ],
    groups=['monitor'],
    activate_on=[CPU_USAGE_MONITOR_ENABLED],
)
class SystemCpuUsageMonitor(AbstractExtension):
    """
    Collects system CPU ticks statistics by reading the contents of /proc/stat.

    For more information about the /proc/stat filesystem, please see:
    http://man7.org/linux/man-pages/man5/proc.5.html

    When enabled, this addon produces the following metrics series:
      * system.cpu.user
      * system.cpu.system
      * system.cpu.idle

    Each of the above metrics are percentages, indicating how much time the CPU
    spent executing a user program, in system calls and idling respectively.
    """

    def __init__(self, config, instances):
        self._entity = instances[SUT]
        self._first_iteration = True

    @callback_dispatcher([PERFORM_MEASUREMENT], [MONITOR_ENDPOINT], entity_option_id=SUT)
    @requires(collector=SystemCpuUsage, scope='dispatcher')
    @requires(create_metric='CreateSeriesMetric', scope='dispatcher')
    def handle_collect_cpu_usage(self, message, collector, create_metric):
        for name, value in collector.collect().items():
            # Skip creating metrics for the first measurement as it contains all since the system was started.
            if not self._first_iteration:
                create_metric('system.cpu.{name}'.format(name=name), value)
            self._first_iteration = False

    @callback_dispatcher([SUT_RESET_DONE], entity_option_id=SUT, optional=True)
    def handle_sut_reset_done(self, message):
        self._first_iteration = True
