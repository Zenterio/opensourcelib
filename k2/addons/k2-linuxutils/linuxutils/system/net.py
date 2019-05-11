import logging
import re
from collections import Counter, defaultdict
from time import time

from zaf.component.decorator import component, requires
from zaf.config.options import ConfigOption, ConfigOptionId
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name
from zaf.messages.decorator import callback_dispatcher

from k2.cmd.run import RUN_COMMAND
from k2.sut import SUT, SUT_RESET_DONE
from monitor import MONITOR_ENDPOINT, PERFORM_MEASUREMENT

logger = logging.getLogger(get_logger_name('k2', 'monitor', 'process'))
logger.addHandler(logging.NullHandler())


class SystemNetworkMonitorError(Exception):
    pass


@component
@requires(exec='Exec', can=['telnet'])
class SystemNetworkStatisticsCollector(object):
    """Figure out the network RX and TX statistics by reading /proc/net/dev."""

    def __init__(self, exec):
        self._exec = exec
        self._matcher = re.compile(
            (
                r'\s+?'
                r'(?P<interface>\S+):\s+'
                r'(?P<rx_bytes>\S+)\s+'
                r'(?P<rx_packets>\S+)\s+'
                r'(?P<rx_errs>\S+)\s+'
                r'(?P<rx_drop>\S+)\s+'
                r'(?P<rx_fifo>\S+)\s+'
                r'(?P<rx_frame>\S+)\s+'
                r'(?P<rx_compressed>\S+)\s+'
                r'(?P<rx_multicast>\S+)\s+'
                r'(?P<tx_bytes>\S+)\s+'
                r'(?P<tx_packets>\S+)\s+'
                r'(?P<tx_errs>\S+)\s+'
                r'(?P<tx_drop>\S+)\s+'
                r'(?P<tx_fifo>\S+)\s+'
                r'(?P<tx_colls>\S+)\s+'
                r'(?P<tx_carrier>\S+)\s+'
                r'(?P<tx_compressed>\S+)'))

    def collect(self):
        try:
            data = self._exec.send_line('cat /proc/net/dev', timeout=5)
        except Exception as e:
            raise SystemNetworkMonitorError('Could not collect network statistics') from e

        matches = list(self._matcher.finditer(data))

        if not matches:
            raise SystemNetworkMonitorError('Could not parse network statistics')

        result = {}
        for match in matches:
            data = match.groupdict()
            result[data['interface']] = {k: int(v) for k, v in data.items() if not k == 'interface'}

        return result


@component
@requires(collector=SystemNetworkStatisticsCollector)
class SystemNetworkStatistics(object):

    def __init__(self, collector):
        self._last_measurement = defaultdict(lambda: Counter({'rx_bytes': 0, 'tx_bytes': 0}))
        self._last_time = defaultdict(lambda: 0)
        self._collector = collector

    def collect(self):
        new_measurement = self._collector.collect()
        current_time = time()
        result = {}

        for interface, data in new_measurement.items():
            new_measurement = Counter({'rx_bytes': data['rx_bytes'], 'tx_bytes': data['tx_bytes']})
            difference = new_measurement - self._last_measurement[interface]
            time_spent = current_time - self._last_time[interface]

            self._last_measurement[interface] = new_measurement
            self._last_time[interface] = current_time

            result[interface] = {
                'rx_kbps': difference['rx_bytes'] / (1024 * time_spent),
                'tx_kbps': difference['tx_bytes'] / (1024 * time_spent),
            }

        return result


SYSTEM_NETWORK_USAGE_MONITOR_ENABLED = ConfigOptionId(
    'monitors.sysnet.enabled',
    'Should the system network usage monitor be enabled',
    at=SUT,
    option_type=bool,
    default=True)


@CommandExtension(
    name='linuxmonitor',
    extends=[RUN_COMMAND],
    config_options=[
        ConfigOption(SUT, required=True, instantiate_on=True),
        ConfigOption(SYSTEM_NETWORK_USAGE_MONITOR_ENABLED, required=False),
    ],
    groups=['monitor'],
    activate_on=[SYSTEM_NETWORK_USAGE_MONITOR_ENABLED],
)
class SystemNetworkUsageMonitor(AbstractExtension):
    """
    Collects system network statistics by reading the contents of /proc/dev/net.

    For more information about the /proc/stat filesystem, please see:
    http://man7.org/linux/man-pages/man5/proc.5.html

    This addon produces the following metrics series:
      * system.network.[NETWORK INTERFACE].rx_kbps
      * system.network.[NETWORK_INTERFACE].tx_kbps

    Each of the above metrics are KB per second.
    """

    def __init__(self, config, instances):
        self._entity = instances[SUT]
        self._first_iteration = True

    @callback_dispatcher([PERFORM_MEASUREMENT], [MONITOR_ENDPOINT], entity_option_id=SUT)
    @requires(system_network_statistics=SystemNetworkStatistics, scope='dispatcher')
    @requires(create_metric='CreateSeriesMetric', scope='dispatcher')
    def handle_collect_cpu_usage(self, message, system_network_statistics, create_metric):
        for interface, data in system_network_statistics.collect().items():
            if not self._first_iteration:
                create_metric(
                    'system.network.{interface}.rx_kbps'.format(interface=interface),
                    data['rx_kbps'])
                create_metric(
                    'system.network.{interface}.tx_kbps'.format(interface=interface),
                    data['tx_kbps'])
            self._first_iteration = False

    @callback_dispatcher([SUT_RESET_DONE], entity_option_id=SUT, optional=True)
    def handle_sut_reset_done(self, message):
        self._first_iteration = True
