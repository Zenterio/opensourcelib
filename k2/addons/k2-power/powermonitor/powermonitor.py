"""
Monitor of sut power consumption.

If possible, measure power consumption of the sut during test run. Uses the
powermeter interface.
"""

import logging

from zaf.component.decorator import component, requires
from zaf.config.options import ConfigOption, ConfigOptionId
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name
from zaf.messages.decorator import callback_dispatcher

from k2.cmd.run import RUN_COMMAND
from k2.sut import SUT
from monitor import MONITOR_ENDPOINT, PERFORM_MEASUREMENT
from powermeter import POWER_METER

logger = logging.getLogger(get_logger_name('k2', 'monitor', 'power'))
logger.addHandler(logging.NullHandler())


class PowerConsumptionMonitorError(Exception):
    pass


@component
@requires(powermeter='PowerMeter')
class PowerConsumptionCollector(object):
    """Collect power consumption using the powermeter interface."""

    def __init__(self, powermeter):
        self._powermeter = powermeter

    def collect(self):
        logger.debug('collecting')
        try:
            data = self._powermeter.power()
        except Exception as e:
            msg = 'Could not collect power consumption data'
            logger.warning(msg)
            logger.debug(msg, exc_info=True)
            raise PowerConsumptionMonitorError(msg) from e

        logger.debug('power: {power}'.format(power=data))
        return data


POWER_CONSUMPTION_MONITOR_ENABLED = ConfigOptionId(
    'monitors.power.enabled',
    'Should the sut power consumption monitor be enabled',
    at=SUT,
    option_type=bool,
    default=True)


@CommandExtension(
    name='powermonitor',
    extends=[RUN_COMMAND],
    config_options=[
        ConfigOption(SUT, required=True, instantiate_on=True),
        ConfigOption(POWER_CONSUMPTION_MONITOR_ENABLED, required=True),
        ConfigOption(POWER_METER, required=False),
    ],
    groups=['monitor'],
    activate_on=[POWER_CONSUMPTION_MONITOR_ENABLED, POWER_METER])
class PowerConsumptionMonitor(AbstractExtension):
    """
    Measure power consumption of sut using the powermeter interface.

    When enabled, this addon produces the following metrics series:
      * system.power.active [unit: W]
    """

    def __init__(self, config, instances):
        self._entity = instances[SUT]

    @callback_dispatcher([PERFORM_MEASUREMENT], [MONITOR_ENDPOINT], entity_option_id=SUT)
    @requires(collector=PowerConsumptionCollector, scope='dispatcher')
    @requires(create_metric='CreateSeriesMetric', scope='dispatcher')
    def handle_collect_power_measurement(self, message, collector, create_metric):
        value = collector.collect()
        logger.debug('collected data: {power}'.format(power=value))
        create_metric('system.power.active', value)
