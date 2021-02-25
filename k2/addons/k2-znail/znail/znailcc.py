"""
A :ref:`connection check <extension-connectioncheck>` implementation for Znail.

Checks that the Znail connection is working by connecting to it.
"""
import logging

from zaf.component.decorator import requires
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name
from zaf.messages.decorator import callback_dispatcher
from zaf.messages.message import MessageId

from connectioncheck import CONNECTIONCHECK_RUN_CHECK
from connectioncheck.connectioncheck import ConnectionCheckResult
from k2.cmd.run import RUN_COMMAND
from k2.sut import SUT

from . import ZNAIL_CONNECTION_CHECK_ENABLED, ZNAIL_CONNECTION_CHECK_ENDPOINT, \
    ZNAIL_CONNECTION_CHECK_REQUIRED, ZNAIL_IP

logger = logging.getLogger(get_logger_name('k2', 'znailcc'))

CHECK_ZNAIL_REQUEST = MessageId(
    'CHECK_ZNAIL_REQUEST', """\
    Request that Znail connection check runs
    """)


@CommandExtension(
    name='znailcc',
    extends=[RUN_COMMAND],
    config_options=[
        ConfigOption(SUT, required=False, instantiate_on=True),
        ConfigOption(ZNAIL_IP, required=False),
        ConfigOption(ZNAIL_CONNECTION_CHECK_ENABLED, required=False),
        ConfigOption(ZNAIL_CONNECTION_CHECK_REQUIRED, required=True),
    ],
    endpoints_and_messages={
        ZNAIL_CONNECTION_CHECK_ENDPOINT: [CONNECTIONCHECK_RUN_CHECK, CHECK_ZNAIL_REQUEST]
    },
    groups=['connectioncheck'],
    activate_on=[ZNAIL_IP, ZNAIL_CONNECTION_CHECK_ENABLED])
class ZnailConnectionCheck(AbstractExtension):
    """
    Znail connection check.

    Checks that it's possible to connect to a Znail.
    """

    def __init__(self, config, instances):
        self._required = config.get(ZNAIL_CONNECTION_CHECK_REQUIRED)
        self._entity = instances.get(SUT)

    @callback_dispatcher(
        [CONNECTIONCHECK_RUN_CHECK], [ZNAIL_CONNECTION_CHECK_ENDPOINT], entity_option_id=SUT)
    @requires(messagebus='MessageBus')
    @requires(znail='Znail')
    def run_check(self, message, messagebus, znail):
        try:
            return self._run_check(None, znail)
        except Exception as e:
            logger.debug(
                'Znail connection check for sut {entity} failed: {error}'.format(
                    entity=self._entity, error=str(e)),
                stack_info=True)
            return ConnectionCheckResult(
                self.name,
                success=False,
                required=self._required,
                message='Znail connection check for sut {entity} failed: {error}'.format(
                    entity=self._entity, error=str(e)))

    @callback_dispatcher(
        [CHECK_ZNAIL_REQUEST], [ZNAIL_CONNECTION_CHECK_ENDPOINT], entity_option_id=SUT)
    @requires(znail='Znail')
    def _run_check(self, message, znail):
        logger.info(
            'Running Znail connection check for entity {entity}'.format(entity=self._entity))

        try:
            znail.health_check()
            logger.info(
                'Znail connection check for sut {entity} was successful'.format(
                    entity=self._entity))
            return ConnectionCheckResult(
                self.name, success=True, required=self._required, message='')
        except Exception as e:
            logger.debug(
                'Znail connection check for sut {entity} failed: {error}'.format(
                    entity=self._entity, error=str(e)),
                exc_info=True)
            return ConnectionCheckResult(
                self.name,
                success=False,
                required=self._required,
                message='Znail connection check for sut {entity} failed: {error}'.format(
                    entity=self._entity, error=str(e)))
