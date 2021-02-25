from unittest import TestCase
from unittest.mock import Mock

from zaf.builtin.unittest.harness import ComponentMock, ExtensionTestHarness
from zaf.config.manager import ConfigManager

from connectioncheck import CONNECTIONCHECK_RUN_CHECK
from k2.sut import SUT

from .. import ZNAIL_CONNECTION_CHECK_ENABLED, ZNAIL_CONNECTION_CHECK_ENDPOINT, \
    ZNAIL_CONNECTION_CHECK_REQUIRED, ZNAIL_IP, ZnailError
from ..znailcc import ZnailConnectionCheck


class TestZnailConnectionCheck(TestCase):

    @staticmethod
    def create_harness(
            znail_cc_enabled=True, znail_cc_required=True, sut=['entity'], component_mock=None):
        config = ConfigManager()
        entity = sut[0]
        config.set(SUT, sut)
        config.set(ZNAIL_IP, '1.2.3.4', entity=entity)
        config.set(ZNAIL_CONNECTION_CHECK_ENABLED, znail_cc_enabled, entity=entity)
        config.set(ZNAIL_CONNECTION_CHECK_REQUIRED, znail_cc_required, entity=entity)

        if component_mock is None:
            component_mock = Mock()

        return ExtensionTestHarness(
            ZnailConnectionCheck,
            config=config,
            components=[ComponentMock(name='Znail', mock=component_mock)])

    def test_extension_registers_dispatchers(self):
        with TestZnailConnectionCheck.create_harness() as harness:
            assert harness.messagebus.has_registered_dispatchers(
                CONNECTIONCHECK_RUN_CHECK, ZNAIL_CONNECTION_CHECK_ENDPOINT, 'entity')

    def test_run_check_success_when_health_check_succeeds(self):
        with TestZnailConnectionCheck.create_harness() as harness:
            result = harness.messagebus.send_request(
                CONNECTIONCHECK_RUN_CHECK, ZNAIL_CONNECTION_CHECK_ENDPOINT,
                entity='entity').wait(timeout=1)[0].result(timeout=0)
            assert result.success

    def test_run_check_fails_when_health_check_fails(self):
        mock = Mock()
        mock.health_check.side_effect = ZnailError('fail')
        with TestZnailConnectionCheck.create_harness(component_mock=mock) as harness:
            result = harness.messagebus.send_request(
                CONNECTIONCHECK_RUN_CHECK, ZNAIL_CONNECTION_CHECK_ENDPOINT,
                entity='entity').wait(timeout=1)[0].result(timeout=0)
            assert not result.success

    def test_run_check_reports_required_according_to_config(self):
        with TestZnailConnectionCheck.create_harness(znail_cc_required=True) as harness:
            result = harness.messagebus.send_request(
                CONNECTIONCHECK_RUN_CHECK, ZNAIL_CONNECTION_CHECK_ENDPOINT,
                entity='entity').wait(timeout=1)[0].result(timeout=0)
            assert result.required
        with TestZnailConnectionCheck.create_harness(znail_cc_required=False) as harness:
            result = harness.messagebus.send_request(
                CONNECTIONCHECK_RUN_CHECK, ZNAIL_CONNECTION_CHECK_ENDPOINT,
                entity='entity').wait(timeout=1)[0].result(timeout=0)
            assert not result.required
