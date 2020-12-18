from unittest import TestCase
from unittest.mock import patch

from zaf.builtin.unittest.harness import ExtensionTestHarness
from zaf.config.manager import ConfigManager

from connectioncheck import CONNECTIONCHECK_RUN_CHECK
from k2.sut import SUT, SUT_IP

from ..telnetcc import TELNET_CONNECTION_CHECK_ENABLED, TELNET_CONNECTION_CHECK_ENDPOINT, \
    TELNET_CONNECTION_CHECK_REQUIRED, TELNET_ENABLED, TELNET_PORT, TelnetConnectionCheck
from .mock.mockpexpect import MockPexpect


class TestTelnetConnectionCheck(TestCase):

    def test_extension_registers_dispatchers(self):
        with create_harness() as harness:
            assert harness.messagebus.has_registered_dispatchers(
                CONNECTIONCHECK_RUN_CHECK, TELNET_CONNECTION_CHECK_ENDPOINT, 'entity')

    def test_run_check_triggers_telnet_client_to_be_created_and_test_command_send(self):
        with patch('telnet.client.pexpect', new_callable=MockPexpect) as pexpect:
            pexpect.process.expect_results.append(' # ')
            pexpect.process.expect_results.append('TEST')
            pexpect.process.expect_results.append(' # ')
            pexpect.process.expect_results.append('true')
            pexpect.process.expect_results.append(' # ')
            pexpect.process.expect_results.append('0')
            pexpect.process.expect_results.append(' # ')
            with create_harness() as harness:
                result = harness.messagebus.send_request(
                    CONNECTIONCHECK_RUN_CHECK, TELNET_CONNECTION_CHECK_ENDPOINT,
                    entity='entity').wait(timeout=1)[0].result(timeout=0)
                assert result.success

    def test_run_check_fails_if_telnet_client_raises_exception(self):
        with patch('telnet.client.pexpect', new_callable=MockPexpect):
            with create_harness() as harness:
                result = harness.messagebus.send_request(
                    CONNECTIONCHECK_RUN_CHECK, TELNET_CONNECTION_CHECK_ENDPOINT,
                    entity='entity').wait(timeout=1)[0].result(timeout=0)
                assert not result.success

    def test_run_check_reports_not_required_if_configured(self):
        with patch('telnet.client.pexpect', new_callable=MockPexpect):
            with create_harness(telnet_cc_required=False) as harness:
                result = harness.messagebus.send_request(
                    CONNECTIONCHECK_RUN_CHECK, TELNET_CONNECTION_CHECK_ENDPOINT,
                    entity='entity').wait(timeout=1)[0].result(timeout=0)
                assert not result.required


def create_harness(
        telnet_enabled=True, telnet_cc_enabled=True, telnet_cc_required=True, sut=['entity']):

    config = ConfigManager()
    entity = sut[0]
    config.set(SUT, sut)
    config.set(SUT_IP, 'localhost', entity=entity)
    config.set(TELNET_ENABLED, telnet_enabled, entity=entity)
    config.set(TELNET_CONNECTION_CHECK_ENABLED, telnet_cc_enabled, entity=entity)
    config.set(TELNET_CONNECTION_CHECK_REQUIRED, telnet_cc_required, entity=entity)
    config.set(TELNET_PORT, 9173, entity=entity)

    return ExtensionTestHarness(TelnetConnectionCheck, config=config)
