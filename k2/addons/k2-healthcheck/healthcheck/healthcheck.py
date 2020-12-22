"""
Monitor SUT health.

The health monitor sends a PERFORM_HEALTH_CHECK request when a health check is
to be performed. Any extension providing health monitoring services can respond
to this request. If a health monitoring service wants to communicate that the
SUT is in an unhealthy state, it raises an exception.

Should a health check fail, this extension is responsible for triggering
appropriate follow up events, such as resetting the SUT.

The PERFORM_HEALTH_CHECK request is triggered automatically if a test case
completed with the verdict failed or error.


Example flow of events
======================

.. uml::

    participant runner
    participant healthcheck
    participant "healthcheck service"
    participant stbrecover

    runner -> healthcheck: TEST_CASE_STARTED
    runner -> healthcheck: "TEST_CASE_FINISHED (success)"

    runner -> healthcheck: TEST_CASE_STARTED
    runner -> healthcheck: "TEST_CASE_FINISHED (failure or error)"

    activate healthcheck

    healthcheck -> "healthcheck service": PERFORM_HEALTH_CHECK
    "healthcheck service" -> healthcheck: "PERFORM_HEALTH_CHECK (raised exception)"

    healthcheck -> stbrecover: SUT_RECOVERY_PERFORM

    deactivate healthcheck

"""

import logging

from zaf.component.decorator import requires
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name
from zaf.messages.decorator import callback_dispatcher

from healthcheck import HealthCheckError
from k2.cmd.run import RUN_COMMAND
from k2.runner import TEST_CASE_FINISHED
from k2.runner.testcase import Verdict
from k2.sut import SUT, SUT_RECOVERY_PERFORM

from . import HEALTH_CHECK_ENDPOINT, PERFORM_HEALTH_CHECK

logger = logging.getLogger(get_logger_name('k2', 'healthcheck'))
logger.addHandler(logging.NullHandler())


@CommandExtension(
    name='healthcheck',
    extends=[RUN_COMMAND],
    config_options=[
        ConfigOption(SUT, required=False, instantiate_on=True),
    ],
    endpoints_and_messages={
        HEALTH_CHECK_ENDPOINT: [PERFORM_HEALTH_CHECK]
    })
class HealthMonitor(AbstractExtension):
    """Monitor SUT health."""

    def __init__(self, config, instances):
        self._entity = instances.get(SUT)

    @callback_dispatcher([TEST_CASE_FINISHED])
    @requires(messagebus='MessageBus')
    def handle_test_case_finished(self, message, messagebus):
        if message.data.verdict in [Verdict.FAILED, Verdict.ERROR]:
            logger.info('Health check triggered')
            futures = messagebus.send_request(PERFORM_HEALTH_CHECK, entity=self._entity)
            for future in futures.as_completed():
                exception = future.exception()
                if isinstance(exception, HealthCheckError):
                    logger.warning(f'Health check failed: {str(exception)}')
                    messagebus.send_request(SUT_RECOVERY_PERFORM, entity=self._entity).wait()
                    break
                else:
                    logger.warning(f'Could not perform health check: {str(exception)}')
            else:
                logger.info('Health check OK')
