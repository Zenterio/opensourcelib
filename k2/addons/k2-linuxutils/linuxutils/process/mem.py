import logging
import re
from collections import OrderedDict

from zaf.component.decorator import component, requires
from zaf.config.options import ConfigOption, ConfigOptionId
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name
from zaf.messages.decorator import callback_dispatcher

from k2.cmd.run import RUN_COMMAND
from k2.sut import SUT, SUT_RESET_DONE
from monitor import MONITOR_ENDPOINT, PERFORM_MEASUREMENT

logger = logging.getLogger(get_logger_name('k2', 'monitor', 'process'))
logger.addHandler(logging.NullHandler())

# While Linux does support different page sizes, the default of 4KB seems
# very common. Should we need to monitor some more exotic CPU architectures
# such as IA64 in the future, this needs to be parameterized.
#
# For now, lets hard-code this to the default 4KB.
LINUX_DEFAULT_PAGE_SIZE = 4


class ProcMemoryMonitorError(Exception):
    pass


@component
@requires(exec='Exec', can=['telnet'])
class ProcMemoryUsageCollector(object):
    """Figure out the memory usage of a process by reading /proc/[pid]/stat."""

    def __init__(self, exec, page_size=LINUX_DEFAULT_PAGE_SIZE):
        self._exec = exec
        self._page_size = page_size
        self._matcher = re.compile(
            (
                r'(?P<size>\S+)\s+'
                r'(?P<resident>\S+)\s+'
                r'(?P<shared>\S+)\s+'
                r'(?P<text>\S+)\s+'
                r'(?P<lib>\S+)\s+'
                r'(?P<data>\S+)\s+'
                r'(?P<dt>\S+)'))

    def collect(self, pid):
        try:
            data = self._exec.send_line('cat /proc/{pid}/statm'.format(pid=pid), timeout=5)
        except Exception as e:
            raise ProcMemoryMonitorError(
                'Could not collect memory stats for process with PID {pid}'.format(pid=pid)) from e

        match = self._matcher.search(data)
        if not match:
            raise ProcMemoryMonitorError(
                'Could not parse memory stats for process with PID {pid}'.format(pid=pid))

        return {k: int(v) * self._page_size for k, v in match.groupdict().items()}


@component
@requires(proc_pid_collector='ProcPidCollector', scope='dispatcher')
@requires(proc_memory_usage_collector=ProcMemoryUsageCollector, scope='dispatcher')
class MultiProcMemoryUsage(object):

    def __init__(self, proc_pid_collector, proc_memory_usage_collector):
        self._proc_pid_collector = proc_pid_collector
        self._proc_memory_usage_collector = proc_memory_usage_collector

    def collect(self, patterns):
        pids = OrderedDict()
        for entity, patterns in patterns.items():
            pids[entity] = self._proc_pid_collector.collect(patterns)

        metrics = {}
        for entity, pids in pids.items():
            for pid in pids:
                for name, value in self._proc_memory_usage_collector.collect(pid).items():
                    metric_name = 'proc.memory.{entity}.{name}.{pid}'.format(
                        entity=entity, name=name, pid=pid)
                    if 'resident' in metric_name or 'size' in metric_name:
                        metrics[metric_name] = value

        return metrics


SUT_PROC_MEMORY_USAGE_MONITOR_IDS = ConfigOptionId(
    'monitors.proc.memory.ids',
    'Identifies what per-process memory monitors should be active for a SUT',
    at=SUT,
    option_type=str,
    multiple=True)

PROC_MEMORY_USAGE_MONITOR_IDS = ConfigOptionId(
    'ids',
    'Identifier for a per-process memory monitor',
    multiple=True,
    entity=True,
    namespace='monitors.proc.memory',
    option_type=str)

PROC_MEMORY_USAGE_MONITOR_PATTERNS = ConfigOptionId(
    'patterns',
    'Regular expression to match against process names to monitor',
    at=PROC_MEMORY_USAGE_MONITOR_IDS,
    option_type=str,
    multiple=True)


@CommandExtension(
    name='linuxmonitor',
    extends=[RUN_COMMAND],
    config_options=[
        ConfigOption(SUT, required=True, instantiate_on=True),
        ConfigOption(SUT_PROC_MEMORY_USAGE_MONITOR_IDS, required=False),
        ConfigOption(PROC_MEMORY_USAGE_MONITOR_IDS, required=False),
        ConfigOption(PROC_MEMORY_USAGE_MONITOR_PATTERNS, required=False),
    ],
    groups=['monitor'],
    activate_on=[SUT_PROC_MEMORY_USAGE_MONITOR_IDS],
)
class ProcMemoryUsageMonitor(AbstractExtension):
    """
    Collects per-process memory statistics by reading the contents of /proc/[pid]/statm.

    For more information about the /proc/statm filesystem, please see:
    http://man7.org/linux/man-pages/man5/proc.5.html

    This addon produces the following metrics series:
      * proc.memory.[MONITOR ID].size.[PID].[RESET_COUNT]
      * proc.memory.[MONITOR ID].resident_size.[PID].[RESET_COUNT]

    Each of the above metrics are measured in KB:
      * size - The virtual size of the process
      * resident_size - The real size of the process
    """

    def __init__(self, config, instances):
        self._reset_count = 0
        self._patterns = OrderedDict(
            sorted(
                {
                    entity: config.get(PROC_MEMORY_USAGE_MONITOR_PATTERNS, entity=entity)
                    for entity in config.get(SUT_PROC_MEMORY_USAGE_MONITOR_IDS, [])
                }.items(),
                key=lambda item: item[0]))

    @callback_dispatcher([PERFORM_MEASUREMENT], [MONITOR_ENDPOINT], entity_option_id=SUT)
    @requires(multi_proc_memory_usage=MultiProcMemoryUsage, scope='dispatcher')
    @requires(create_metric='CreateSeriesMetric', scope='dispatcher')
    def handle_collect_cpu_usage(self, message, multi_proc_memory_usage, create_metric):
        for metric_name, value in multi_proc_memory_usage.collect(self._patterns).items():
            create_metric(
                '{metric_name}.{reset_count}'.format(
                    metric_name=metric_name, reset_count=self._reset_count), value)

    @callback_dispatcher([SUT_RESET_DONE], entity_option_id=SUT, optional=True)
    def handle_sut_reset_done(self, message):
        self._reset_count = self._reset_count + 1
