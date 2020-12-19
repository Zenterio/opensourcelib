from unittest import TestCase
from unittest.mock import MagicMock, Mock, patch

from zaf.builtin.unittest.harness import ExtensionTestHarness
from zaf.config.manager import ConfigManager

from connectioncheck import CONNECTIONCHECK_RUN_CHECK
from k2.sut import SUT

from .. import SERIAL_CONNECTION_CHECK_ENABLED, SERIAL_CONNECTION_CHECK_ENDPOINT, \
    SERIAL_CONNECTION_CHECK_REQUIRED, SERIAL_ENABLED, SERIAL_TIMEOUT
from ..serialcc import SerialConnectionCheck


class TestSerialConnectionCheck(TestCase):

    def test_extension_is_enabled(self):
        with create_harness() as harness:
            assert harness.extension._enabled

    def test_extension_registers_dispatchers(self):
        with create_harness() as harness:
            assert harness.messagebus.has_registered_dispatchers(
                CONNECTIONCHECK_RUN_CHECK, SERIAL_CONNECTION_CHECK_ENDPOINT, 'entity')

    def test_run_check_triggers_serial_write_line(self):
        with patch('zserial.serialcc.SerialClient', new=MagicMock()):
            with create_harness() as harness:
                result = harness.messagebus.send_request(
                    CONNECTIONCHECK_RUN_CHECK, SERIAL_CONNECTION_CHECK_ENDPOINT,
                    entity='entity').wait(timeout=1)[0].result(timeout=0)
                assert result.success

    def test_run_check_fails_if_serial_write_line_gives_exception(self):
        client = MagicMock()
        mock = Mock()
        mock.side_effect = Exception('fail')
        client.send_line = mock
        with patch('zserial.serialcc.SerialClient', return_value=client):
            with create_harness() as harness:
                result = harness.messagebus.send_request(
                    CONNECTIONCHECK_RUN_CHECK, SERIAL_CONNECTION_CHECK_ENDPOINT,
                    entity='entity').wait(timeout=1)[0].result(timeout=0)
                assert not result.success

    def test_run_check_reports_required_according_to_config(self):
        with patch('zserial.serialcc.SerialClient', new=MagicMock()):
            with create_harness(serial_cc_required=True) as harness:
                result = harness.messagebus.send_request(
                    CONNECTIONCHECK_RUN_CHECK, SERIAL_CONNECTION_CHECK_ENDPOINT,
                    entity='entity').wait(timeout=1)[0].result(timeout=0)
                assert result.required
            with create_harness(serial_cc_required=False) as harness:
                result = harness.messagebus.send_request(
                    CONNECTIONCHECK_RUN_CHECK, SERIAL_CONNECTION_CHECK_ENDPOINT,
                    entity='entity').wait(timeout=1)[0].result(timeout=0)
                assert not result.required

    def test_a_failed_connection_check_also_checks_the_current_users_group_belongings(self):
        client = MagicMock()
        mock = Mock()
        mock.side_effect = Exception('fail')
        client.send_line = mock
        with patch('zserial.serialcc.SerialClient', return_value=client):
            with create_harness() as harness:
                harness.extension._check_if_member_of_dialout_group = MagicMock()
                harness.messagebus.send_request(
                    CONNECTIONCHECK_RUN_CHECK, SERIAL_CONNECTION_CHECK_ENDPOINT,
                    entity='entity').wait(timeout=1)[0].result(timeout=0)
        harness.extension._check_if_member_of_dialout_group.assert_called_once_with()

    def test_check_the_current_users_group_belongings_logs_nothing_if_dailout_does_not_exist(self):
        with patch('zserial.serialcc.logger') as logger, patch('grp.getgrnam',
                                                               new=Mock(side_effect=KeyError())):
            with create_harness() as harness:
                harness.extension._check_if_member_of_dialout_group()
                assert not logger.warning.called

    def test_check_the_current_user_group_belongings_where_user_is_not_a_member_of_dailout(self):
        group_mock = Mock()
        group_mock.gr_gid = 1
        with patch('zserial.serialcc.logger') as logger, patch(
                'grp.getgrnam', new=Mock(return_value=group_mock)), patch(
                    'os.getgroups', new=Mock(return_value=[2])):
            with create_harness() as harness:
                harness.extension._check_if_member_of_dialout_group()
                assert logger.warning.called

    def test_check_the_current_user_group_belongings_where_user_is_a_member_of_dailout(self):
        group_mock = Mock()
        group_mock.gr_gid = 1
        with patch('zserial.serialcc.logger') as logger, patch(
                'grp.getgrnam', new=Mock(return_value=group_mock)), patch(
                    'os.getgroups', new=Mock(return_value=[1])):
            with create_harness() as harness:
                harness.extension._check_if_member_of_dialout_group()
                assert not logger.warning.called


def create_harness(
        serial_enabled=True, serial_cc_enabled=True, serial_cc_required=True, sut=['entity']):
    config = ConfigManager()
    entity = sut[0]
    config.set(SUT, sut)
    config.set(SERIAL_ENABLED, serial_enabled, entity=entity)
    config.set(SERIAL_CONNECTION_CHECK_ENABLED, serial_cc_enabled, entity=entity)
    config.set(SERIAL_CONNECTION_CHECK_REQUIRED, serial_cc_required, entity=entity)
    config.set(SERIAL_TIMEOUT, 0.1, entity=entity)

    return ExtensionTestHarness(SerialConnectionCheck, config=config)
