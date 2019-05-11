"""
Provides facilities for monitoring the SUT.

The SUT is monitored by periodically performing some measurement, for example
checking how much free memory is available.

The results of each measurement are sent to the metrics addon.
"""

import functools
import logging
import threading

from zaf.component.decorator import requires
from zaf.config.options import ConfigOption, ConfigOptionId
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name
from zaf.messages.decorator import callback_dispatcher

from k2 import ABORT, CRITICAL_ABORT, K2_APPLICATION_ENDPOINT
from k2.cmd.run import RUN_COMMAND
from k2.runner import TEST_RUN_FINISHED, TEST_RUN_STARTED
from k2.sut import SUT, SUT_RESET_DONE, SUT_RESET_EXPECTED, SUT_RESET_NOT_EXPECTED, \
    SUT_RESET_STARTED
from monitor import MONITOR_ENDPOINT, PERFORM_MEASUREMENT

logger = logging.getLogger(get_logger_name('k2', 'monitor'))
logger.addHandler(logging.NullHandler())

MONITOR_ENABLED = ConfigOptionId(
    'monitors.enabled', 'Should monitoring be enabled', at=SUT, option_type=bool, default=True)

MONITOR_INTERVAL = ConfigOptionId(
    'monitors.interval',
    'The interval at which monitors should perform measurements in seconds',
    at=SUT,
    option_type=float,
    default=5.0)


@CommandExtension(
    name='monitor',
    extends=[RUN_COMMAND],
    config_options=[
        ConfigOption(SUT, required=True, instantiate_on=True),
        ConfigOption(MONITOR_ENABLED, required=True),
        ConfigOption(MONITOR_INTERVAL, required=True)
    ],
    endpoints_and_messages={
        MONITOR_ENDPOINT: [PERFORM_MEASUREMENT],
    },
    groups=['monitor'],
    activate_on=[MONITOR_ENABLED],
)
class Monitor(AbstractExtension):
    """
    Manages all enabled monitors.

    Keeps track of when measurements are to be performed.
    Periodically sends PERFORM_MEASUREMENT requests.
    """

    def __init__(self, config, instances):
        self._timer = None
        self._active = True
        self._entity = instances[SUT]
        self._trigger_interval = config.get(MONITOR_INTERVAL)
        self._lock = threading.Lock()
        self._sut_is_resetting = False

    @callback_dispatcher([TEST_RUN_STARTED])
    @requires(messagebus='MessageBus')
    def start_sending_perform_measurement_requests(self, message, messagebus):

        def schedule_next_perform_measurement_request():
            self._timer = threading.Timer(
                self._trigger_interval,
                functools.partial(
                    self.start_sending_perform_measurement_requests, message, messagebus))
            self._timer.start()

        def send_perform_measurement_request():
            logger.debug('Starting measurements')
            return messagebus.send_request(
                PERFORM_MEASUREMENT, MONITOR_ENDPOINT, data=None, entity=self._entity)

        def log_any_failed_measurement(futures):
            for future in futures.as_completed():
                exception = future.exception()
                if exception:
                    try:
                        raise exception
                    except Exception:
                        if not self._sut_is_resetting:
                            logger.debug(str(exception), exc_info=True)
                            logger.error(str(exception))
                        else:
                            logger.debug(
                                'Failed measurement during reset: {exception}'.format(
                                    exception=str(exception)))

        if self._active:
            with self._lock:
                schedule_next_perform_measurement_request()
                if not self._sut_is_resetting:
                    log_any_failed_measurement(send_perform_measurement_request())
                else:
                    logger.debug('Skipping measurements because SUT is resetting')

    @callback_dispatcher(
        [SUT_RESET_EXPECTED, SUT_RESET_STARTED], entity_option_id=SUT, optional=True)
    def handle_sut_reset_started(self, message):
        logger.debug('Disabling monitoring during reset')
        self._sut_is_resetting = True

    @callback_dispatcher(
        [SUT_RESET_DONE, SUT_RESET_NOT_EXPECTED], entity_option_id=SUT, optional=True)
    def handle_sut_reset_done(self, message):
        logger.debug('Enabling monitoring after reset')
        self._sut_is_resetting = False

    @callback_dispatcher([TEST_RUN_FINISHED])
    @callback_dispatcher([ABORT, CRITICAL_ABORT], [K2_APPLICATION_ENDPOINT])
    def stop_sending_perform_measurement_requests(self, message):
        with self._lock:
            if self._timer is not None:
                self._timer.cancel()
            self._timer = None
            self._active = False

    def destroy(self):
        self.stop_sending_perform_measurement_requests(None)
