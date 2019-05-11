"""
Used to trigger all available connection checks.

This extension will be triggered automatically by the POST_INTIALIZE_SUT sequence point in the run command.
It can also be triggered at other times by sending a CONNECTIONCHECK_RUN_CHECKS message.

The connection check triggers all connection checks by sending out a broadcast CONNECTIONCHECK_RUN_CHECK.
The individual connection checks respond with a ConnectionCheckResult indicating if the check was successful
and also if it is required for the continuation of the command.

If any of the required checks fail a SUT_RECOVERY_PERFORM request will be sent out to trigger a recovery of the sut.

Example of a successful recovery:

.. uml::

    runcommand -> connectioncheck: POST_INITIALIZE_SUT
    connectioncheck -> check: CONNECTIONCHECK_RUN_CHECK
    connectioncheck <- check: failed, required
    connectioncheck -> recover: SUT_RECOVERY_PERFORM
    connectioncheck <- recover: indicating success by not raising exception
    connectioncheck -> check: CONNECTIONCHECK_RUN_CHECK
    connectioncheck <- check: success, required
    runcommand <- connectioncheck: indicating success by not raising exception

Example of a failed recovery:

.. uml::

    runcommand -> connectioncheck: POST_INITIALIZE_SUT
    connectioncheck -> check: CONNECTIONCHECK_RUN_CHECK
    connectioncheck <- check: failed, required
    connectioncheck -> recover: SUT_RECOVERY_PERFORM
    connectioncheck <- recover: exception
    runcommand <- connectioncheck: exception

"""
import logging
from collections import namedtuple

from zaf.component.decorator import requires
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name
from zaf.messages.decorator import callback_dispatcher, sequential_dispatcher

from k2.cmd.run import POST_INITIALIZE_SUT, RUN_COMMAND, RUN_COMMAND_ENDPOINT
from k2.sut import SUT, SUT_RECOVERY_PERFORM

from . import CONNECTIONCHECK_ENABLED, CONNECTIONCHECK_ENDPOINT, CONNECTIONCHECK_RUN_CHECK, \
    CONNECTIONCHECK_RUN_CHECKS, CONNECTIONCHECK_SHOULD_RECOVER

logger = logging.getLogger(get_logger_name('k2', 'connectioncheck'))

ConnectionCheckResult = namedtuple(
    'ConnectionCheckResult', ['name', 'success', 'required', 'message'])


class ConnectionCheckFailed(Exception):
    pass


class SutRecoveryNotPerformed(Exception):
    pass


@CommandExtension(
    name='connectioncheck',
    extends=[RUN_COMMAND],
    config_options=[
        ConfigOption(SUT, required=True, instantiate_on=True),
        ConfigOption(CONNECTIONCHECK_ENABLED, required=True),
        ConfigOption(CONNECTIONCHECK_SHOULD_RECOVER, required=True),
    ],
    endpoints_and_messages={CONNECTIONCHECK_ENDPOINT: [
        CONNECTIONCHECK_RUN_CHECKS,
    ]},
    groups=['connectioncheck'],
    activate_on=[CONNECTIONCHECK_ENABLED])
class ConnectionCheck(AbstractExtension):
    """Implementation of the connection check."""

    def __init__(self, config, instances):
        self._entity = instances.get(SUT)
        self._should_recover = config.get(CONNECTIONCHECK_SHOULD_RECOVER)

    @callback_dispatcher([POST_INITIALIZE_SUT], [RUN_COMMAND_ENDPOINT], entity_option_id=SUT)
    @requires(messagebus='MessageBus')
    def run_initialization_check(self, message, messagebus):
        messagebus.send_request(
            CONNECTIONCHECK_RUN_CHECKS, CONNECTIONCHECK_ENDPOINT, self._entity,
            self._should_recover).wait()[0].result()

    @sequential_dispatcher(
        [CONNECTIONCHECK_RUN_CHECKS], [CONNECTIONCHECK_ENDPOINT], entity_option_id=SUT)
    @requires(messagebus='MessageBus')
    def run_all_checks(self, message, messagebus):
        self._run_all_checks_internal(messagebus, message.data)

    def _run_all_checks_internal(self, messagebus, should_recover):
        logger.info('Connection check started')
        futures = messagebus.send_request(CONNECTIONCHECK_RUN_CHECK, None, self._entity).wait()

        if len(futures) > 0:

            failed_required = []
            for future in futures:
                result = future.result(timeout=0)
                if result.success:
                    logger.info("Connection check '{name}' successful".format(name=result.name))
                elif not result.success and result.required:
                    failed_required.append(result)
                    logger.error(
                        "Required connection check '{name}' failed: {message}".format(
                            name=result.name, message=result.message))
                else:
                    logger.warning(
                        "Connection check '{name}' failed: {message}".format(
                            name=result.name, message=result.message))

            if len(failed_required) > 0:
                if should_recover:
                    logger.info('Trying to recover from failed connection checks')
                    futures = messagebus.send_request(SUT_RECOVERY_PERFORM, None,
                                                      self._entity).wait()
                    if len(futures) == 0:
                        raise SutRecoveryNotPerformed(
                            'Sut recovery failed for {entity}. No dispatcher for SUT_RECOVERY_PERFORM'.
                            format(entity=self._entity))

                    for future in futures:
                        future.result()

                    logger.info('Rerunning connection check after sut recovery')
                    self._run_all_checks_internal(messagebus, False)
                else:
                    msg = 'One or more connection checks failed and no recovery performed'
                    logger.critical(msg)
                    raise ConnectionCheckFailed(msg)
        else:
            logger.info('No connection checks performed')

        logger.info('Connection check completed')
