import logging
import re
from collections import Counter, OrderedDict, defaultdict

from zaf.component.decorator import component, requires
from zaf.config.options import ConfigOption, ConfigOptionId
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name
from zaf.messages.decorator import callback_dispatcher

from k2.cmd.run import RUN_COMMAND
from k2.sut import SUT, SUT_RESET_DONE
from linuxutils.system.cpu import CPU_USAGE_MONITOR_ENABLED
from monitor import MONITOR_ENDPOINT, PERFORM_MEASUREMENT

logger = logging.getLogger(get_logger_name('k2', 'monitor', 'process'))
logger.addHandler(logging.NullHandler())


class ProcCpuMonitorError(Exception):
    pass


@component
@requires(exec='Exec', can=['telnet'])
class ProcStatusCollector(object):
    """Figure out the status of a process by reading /proc/[pid]/stat."""

    def __init__(self, exec):
        self._exec = exec
        # What follows should be compatible with Linux 2.1.22 and later.
        self._matcher = re.compile(
            (
                r'(?P<pid>\S+)\s+'
                r'\S+\s+'
                r'(?P<state>\S+)\s+'
                r'(?P<ppid>\S+)\s+'
                r'(?P<pgrp>\S+)\s+'
                r'(?P<session>\S+)\s+'
                r'(?P<tty_nr>\S+)\s+'
                r'(?P<tpgid>\S+)\s+'
                r'(?P<flags>\S+)\s+'
                r'(?P<minflt>\S+)\s+'
                r'(?P<cminflt>\S+)\s+'
                r'(?P<majflt>\S+)\s+'
                r'(?P<cmajflt>\S+)\s+'
                r'(?P<utime>\S+)\s+'
                r'(?P<stime>\S+)\s+'
                r'(?P<cutime>\S+)\s+'
                r'(?P<cstime>\S+)\s+'
                r'(?P<priority>\S+)\s+'
                r'(?P<nice>\S+)\s+'
                r'(?P<num_threads>\S+)\s+'
                r'(?P<itrealvalue>\S+)\s+'
                r'(?P<starttime>\S+)\s+'
                r'(?P<vsize>\S+)\s+'
                r'(?P<rss>\S+)\s+'
                r'(?P<rsslim>\S+)\s+'
                r'(?P<startcode>\S+)\s+'
                r'(?P<endcode>\S+)\s+'
                r'(?P<startstack>\S+)\s+'
                r'(?P<kstkesp>\S+)\s+'
                r'(?P<kstkeip>\S+)\s+'
                r'(?P<signal>\S+)\s+'
                r'(?P<blocked>\S+)\s+'
                r'(?P<sigignore>\S+)\s+'
                r'(?P<sigcatch>\S+)\s+'
                r'(?P<wchan>\S+)\s+'
                r'(?P<nswap>\S+)\s+'
                r'(?P<cnswap>\S+)\s+'
                r'(?P<exit_signal>\S+)'))

    def collect(self, pid):
        try:
            data = self._exec.send_line('cat /proc/{pid}/stat'.format(pid=pid), timeout=5)
        except Exception as e:
            raise ProcCpuMonitorError(
                'Could not collect status data for process with PID {pid}'.format(pid=pid)) from e

        match = self._matcher.search(data)
        if not match:
            raise ProcCpuMonitorError(
                'Could not parse status data for process with PID {pid}'.format(pid=pid))

        def try_and_convert_to_int(value):
            try:
                return int(value)
            except ValueError:
                return value

        return {k: try_and_convert_to_int(v) for k, v in match.groupdict().items()}


@component
@requires(system_cpu_ticks_collector='SystemCpuTicksCollector')
@requires(proc_status_collector=ProcStatusCollector)
class ProcCpuUsage(object):

    def __init__(self, system_cpu_ticks_collector, proc_status_collector):
        self._system_cpu_ticks_collector = system_cpu_ticks_collector
        self._proc_status_collector = proc_status_collector
        self._last_system_cpu_ticks = defaultdict(lambda: 0)
        self._last_proc_cpu_ticks = defaultdict(lambda: {'utime': 0, 'stime': 0, 'cutime': 0, 'cstime': 0})

    def collect(self, pid):
        system_cpu_ticks = sum(self._system_cpu_ticks_collector.collect().values())
        total_ticks = system_cpu_ticks - self._last_system_cpu_ticks[pid]
        self._last_system_cpu_ticks[pid] = system_cpu_ticks

        proc_status = self._proc_status_collector.collect(pid)
        current_proc_cpu_ticks = Counter(
            {
                'utime': proc_status['utime'],
                'stime': proc_status['stime'],
                'cutime': proc_status['cutime'],
                'cstime': proc_status['cstime'],
            })
        difference = current_proc_cpu_ticks.copy()
        difference.subtract(self._last_proc_cpu_ticks[pid])
        self._last_proc_cpu_ticks[pid] = current_proc_cpu_ticks

        def as_percentage(ticks):
            if total_ticks > 0:
                return 100 * ticks / total_ticks
            return 0

        return {
            'utime': as_percentage(difference['utime']),
            'stime': as_percentage(difference['stime']),
            'cutime': as_percentage(difference['cutime']),
            'cstime': as_percentage(difference['cstime']),
        }


@component
@requires(proc_pid_collector='ProcPidCollector', scope='dispatcher')
@requires(proc_cpu_usage_collector=ProcCpuUsage, scope='dispatcher')
class MultiProcCpuUsage(object):

    def __init__(self, proc_pid_collector, proc_cpu_usage_collector):
        self._proc_pid_collector = proc_pid_collector
        self._proc_cpu_usage_collector = proc_cpu_usage_collector

    def collect(self, patterns):
        pids = OrderedDict()
        for entity, patterns in patterns.items():
            pids[entity] = self._proc_pid_collector.collect(patterns)

        metrics = {}
        for entity, pids in pids.items():
            for pid in pids:
                for name, value in self._proc_cpu_usage_collector.collect(pid).items():
                    metric_name = 'proc.cpu.{entity}.{name}.{pid}'.format(
                        entity=entity, name=name, pid=pid)
                    metrics[metric_name] = value

        return metrics


SUT_PROC_CPU_USAGE_MONITOR_IDS = ConfigOptionId(
    'monitors.proc.cpu.ids',
    'Identifies what per-process CPU monitors should be active for a SUT',
    at=SUT,
    option_type=str,
    multiple=True)

PROC_CPU_USAGE_MONITOR_IDS = ConfigOptionId(
    'ids',
    'Identifier for a per-process CPU monitor',
    multiple=True,
    entity=True,
    namespace='monitors.proc.cpu',
    option_type=str)

PROC_CPU_USAGE_MONITOR_PATTERNS = ConfigOptionId(
    'patterns',
    'Regular expression to match against process names to monitor',
    at=PROC_CPU_USAGE_MONITOR_IDS,
    option_type=str,
    multiple=True,
)


@CommandExtension(
    name='linuxmonitor',
    extends=[RUN_COMMAND],
    config_options=[
        ConfigOption(SUT, required=True, instantiate_on=True),
        ConfigOption(CPU_USAGE_MONITOR_ENABLED, required=False),
        ConfigOption(SUT_PROC_CPU_USAGE_MONITOR_IDS, required=False),
        ConfigOption(PROC_CPU_USAGE_MONITOR_IDS, required=False),
        ConfigOption(PROC_CPU_USAGE_MONITOR_PATTERNS, required=False),
    ],
    groups=['monitor'],
    activate_on=[CPU_USAGE_MONITOR_ENABLED, SUT_PROC_CPU_USAGE_MONITOR_IDS],
)
class ProcCpuUsageMonitor(AbstractExtension):
    """
    Collects per-process CPU ticks statistics by reading the contents of /proc/[pid]/stat.

    For more information about the /proc/stat filesystem, please see:
    http://man7.org/linux/man-pages/man5/proc.5.html

    This addon produces the following metrics series:
      * proc.cpu.[MONITOR ID].utime.[PID].[RESET_COUNT]
      * proc.cpu.[MONITOR ID].stime.[PID].[RESET_COUNT]
      * proc.cpu.[MONITOR ID].cutime.[PID].[RESET_COUNT]
      * proc.cpu.[MONITOR ID].cstime.[PID].[RESET_COUNT]

    Each of the above metrics are percentages:
      * utime - CPU time in user mode
      * stime - CPU time in kernel mode
      * cutime - Children CPU time in user mode
      * cstime - Children CPU time in kernel mode
    """

    def __init__(self, config, instances):
        self._patterns = OrderedDict(
            sorted(
                {
                    entity: config.get(PROC_CPU_USAGE_MONITOR_PATTERNS, entity=entity)
                    for entity in config.get(SUT_PROC_CPU_USAGE_MONITOR_IDS, [])
                }.items(),
                key=lambda item: item[0]))
        self._first_iteration = True
        self._reset_count = 0

    @callback_dispatcher([PERFORM_MEASUREMENT], [MONITOR_ENDPOINT], entity_option_id=SUT)
    @requires(multi_proc_cpu_usage=MultiProcCpuUsage, scope='dispatcher')
    @requires(create_metric='CreateSeriesMetric', scope='dispatcher')
    def handle_collect_cpu_usage(self, message, multi_proc_cpu_usage, create_metric):
        for metric_name, value in multi_proc_cpu_usage.collect(self._patterns).items():
            # Skip creating metrics for the first measurement as it contains all since the system was started.
            if not self._first_iteration:
                create_metric(
                    '{metric_name}.{reset_count}'.format(
                        metric_name=metric_name, reset_count=self._reset_count), value)
            self._first_iteration = False

    @callback_dispatcher([SUT_RESET_DONE], entity_option_id=SUT, optional=True)
    def handle_sut_reset_done(self, message):
        self._reset_count = self._reset_count + 1
        self._first_iteration = True
