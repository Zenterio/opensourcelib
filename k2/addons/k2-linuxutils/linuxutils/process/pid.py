import logging
import re
from collections import OrderedDict

from zaf.component.decorator import component, requires
from zaf.config.options import ConfigOption, ConfigOptionId
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name
from zaf.messages.decorator import callback_dispatcher

from healthcheck import HEALTH_CHECK_ENDPOINT, PERFORM_HEALTH_CHECK, HealthCheckError
from k2.cmd.run import RUN_COMMAND
from k2.sut import SUT

logger = logging.getLogger(get_logger_name('k2', 'monitor', 'process'))
logger.addHandler(logging.NullHandler())


class PidMonitorError(Exception):
    pass


@component
@requires(exec='Exec', can=['telnet'])
class ProcPidCollector(object):
    """
    Figure out the PIDs of a collection of processes.

    Runs the ps command on using an exec component and parses the results.
    Note that this component is currently limited to the BusyBox ps implementation.
    """

    def __init__(self, exec):
        self._exec = exec
        self._matcher = re.compile(
            r'^\s*(?P<pid>\d+)\s+\S+\s+\S+\s+\S+\s+(?P<command>.+)', flags=re.MULTILINE)

    def collect(self, patterns):
        """
        Collect the PIDs of a collection of processes.

        Runs ps and parses the output using the provided list of regular expressions.
        Exclude patterns can be provided by prefixing the entry with !.

        A process in included in the PIDs list if:
        * Any of the include patterns.
        * None of the exclude patterns match.
        """

        def pattern_matches(pattern, command):
            if pattern.startswith('!'):
                return bool(re.search(pattern[1:], command))
            return bool(re.search(pattern, command))

        patterns = set(patterns)
        positive_patterns = set(filter(lambda pattern: not pattern.startswith('!'), patterns))
        negative_patterns = patterns - positive_patterns
        pids = set()

        try:
            data = self._exec.send_line('ps ww', timeout=5)
            for pid, command in self._matcher.findall(data):
                if (any({pattern_matches(pattern, command) for pattern in positive_patterns})
                        and not any({pattern_matches(pattern, command)
                                     for pattern in negative_patterns})):
                    pids.add(int(pid))
            logger.debug(
                'Found the following PIDs for proccess {patterns}: {pids}'.format(
                    patterns=patterns, pids=pids))
            return pids
        except Exception as e:
            raise PidMonitorError('Could not collect PID data') from e


SUT_HEALTHCHECK_PROC_IDS = ConfigOptionId(
    'healthcheck.proc.ids',
    'Identifies what process monitoring health checks should be active for a SUT',
    at=SUT,
    option_type=str,
    multiple=True)

HEALTHCHECK_PROC_IDS = ConfigOptionId(
    'ids',
    'Identifier for a process monitor health check',
    multiple=True,
    entity=True,
    namespace='healthcheck.proc',
    option_type=str)

HEALTHCHECK_PROC_PATTERNS = ConfigOptionId(
    'patterns',
    'Regular expression to match against process names',
    at=HEALTHCHECK_PROC_IDS,
    option_type=str,
    multiple=True)


@CommandExtension(
    name='linuxhealthcheck',
    extends=[RUN_COMMAND],
    config_options=[
        ConfigOption(SUT, required=False, instantiate_on=True),
        ConfigOption(SUT_HEALTHCHECK_PROC_IDS, required=False),
        ConfigOption(HEALTHCHECK_PROC_IDS, required=False),
        ConfigOption(HEALTHCHECK_PROC_PATTERNS, required=False),
    ],
    groups=['healthcheck'],
    activate_on=[HEALTHCHECK_PROC_IDS],
)
class ProcMonitoringHealthCheck(AbstractExtension):
    """Monitor SUT health by checking that processes matching the provided patterns are running."""

    def __init__(self, config, instances):
        self._patterns = OrderedDict(
            sorted(
                {
                    entity: config.get(HEALTHCHECK_PROC_PATTERNS, entity=entity)
                    for entity in config.get(SUT_HEALTHCHECK_PROC_IDS, [])
                }.items(),
                key=lambda item: item[0]))

    @callback_dispatcher([PERFORM_HEALTH_CHECK], [HEALTH_CHECK_ENDPOINT], entity_option_id=SUT)
    @requires(proc_pid_collector='ProcPidCollector', scope='dispatcher')
    def handle_perform_health_check(self, message, proc_pid_collector):
        pids = OrderedDict()
        for entity, patterns in self._patterns.items():
            pids[entity] = proc_pid_collector.collect(patterns)

        for entity, pids in pids.items():
            if not pids:
                msg = 'Could not find any PIDs matching health check: {entity}'.format(
                    entity=entity)
                logger.warning(msg)
                raise HealthCheckError(msg)
