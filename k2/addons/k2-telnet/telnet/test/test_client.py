from unittest import TestCase
from unittest.mock import ANY, DEFAULT, MagicMock, call, patch

from ..client import TelnetClient, TelnetError, TelnetTimeout
from .mock.mockpexpect import MockPexpect


class TelnetMockPexpect(MockPexpect):

    def __init__(self):
        super().__init__()
        self.prepare_for_connect()

    def prepare_for_connect(self):
        self.process.expect_results += ['/ # ', 'TEST', '/ # ']


class TestTelnetClient(TestCase):

    def setUp(self):
        super().setUp()
        patcher = patch('telnet.client.pexpect', new_callable=TelnetMockPexpect)
        self.mock_pexpect = patcher.start()
        self.addCleanup(patcher.stop)
        self.telnet = TelnetClient(None)

    def test_context_manager_handles_connect_and_disconnect(self):
        with patch.multiple(self.telnet, connect=DEFAULT, disconnect=DEFAULT) as mocks:
            with self.telnet:
                mocks['connect'].assert_called_once_with()
            mocks['disconnect'].assert_called_once_with()

    def test_calling_connect_spawns_a_process(self):
        with patch('telnet.client.pexpect.spawnu') as spawnu:
            self.telnet.connect()
            self.assertTrue(spawnu.called)

    def test_is_connected_initially_returns_false(self):
        self.assertFalse(self.telnet.is_connected())

    def test_is_connected_returns_true_when_connected(self):
        self.telnet.connect()
        self.assertTrue(self.telnet.is_connected())

    def test_calling_connect_multiple_times_reconnects(self):
        self.telnet.disconnect = MagicMock()
        with patch('telnet.client.pexpect.spawnu') as spawnu:
            self.telnet.connect()
            self.telnet.connect()
            self.telnet.disconnect.assert_called_once_with()
            self.assertEqual(spawnu.call_count, 2)

    def test_connect_raises_a_telnet_error_if_telnet_process_can_not_be_spawned(self):
        with patch('telnet.client.pexpect.spawnu', MagicMock(side_effect=MockPexpect.EOF(None))):
            with self.assertRaises(TelnetError):
                self.telnet.connect()

    def test_calling_send_line_raises_telnet_error_if_not_connected(self):
        with self.assertRaises(TelnetError):
            self.telnet.send_line('', retry_once=False)

    def test_calling_send_line_raises_telnet_error_after_retry_if_not_connected(self):
        with self.assertRaises(TelnetError):
            self.telnet.send_line('', retry_once=True)

    def test_calling_expect_raises_telnet_error_if_not_connected(self):
        with self.assertRaises(TelnetError):
            self.telnet.expect(None)

    def test_send_line_uses_the_default_timeout_if_none_is_provided(self):
        self.telnet.telnet = MagicMock()
        self.telnet.send_line('')
        self.telnet.telnet.expect.assert_called_with(ANY, timeout=self.telnet.timeout)

    def test_send_line_uses_a_specific_timeout_if_one_is_provided(self):
        my_timeout = 123
        self.telnet.telnet = MagicMock()
        self.telnet.send_line('', timeout=my_timeout)
        self.telnet.telnet.expect.assert_called_with(ANY, timeout=my_timeout)

    def test_send_line_uses_the_default_endmark_if_none_is_provided(self):
        self.telnet.telnet = MagicMock()
        self.telnet.expect = MagicMock()
        self.telnet.send_line('command')
        self.telnet.send_line('')
        self.telnet.expect.assert_called_with([self.telnet.endmark], timeout=ANY)

    def test_send_line_uses_a_specific_endmark_if_one_is_provided(self):
        my_endmark = 'my custom endmark'
        self.telnet.telnet = MagicMock()
        self.telnet.expect = MagicMock()
        self.telnet.send_line('', endmark=my_endmark)
        self.telnet.expect.assert_called_with([my_endmark], timeout=ANY)

    def test_send_line_raises_telnet_error_on_communication_failure(self):
        self.telnet.telnet = MagicMock()
        self.telnet.telnet.sendline = MagicMock(side_effect=MockPexpect.EOF(None))
        with self.assertRaises(TelnetError):
            self.telnet.send_line('', retry_once=False)

    def test_send_line_calls_disconnect_and_raises_telnet_error_on_communication_failure(self):
        self.telnet.telnet = MagicMock()
        self.telnet.telnet.sendline = MagicMock(side_effect=MockPexpect.EOF(None))
        self.telnet.disconnect = MagicMock()
        with self.assertRaises(TelnetError):
            self.telnet.send_line('', retry_once=False)
        self.telnet.disconnect.assert_called_once_with()

    def test_send_line_returns_the_before_property_of_the_pexpect_object_on_success(self):
        test_data = 'some test data'
        self.telnet.telnet = MagicMock()
        self.telnet.telnet.before = test_data
        result = self.telnet.send_line(test_data)
        self.assertEqual(result, test_data)

    def test_send_line_retries_once_on_error(self):
        self.telnet.telnet = MagicMock()
        self.telnet.telnet.sendline = MagicMock(side_effect=[
            MockPexpect.EOF(None),
        ])
        self.telnet.expect = MagicMock()
        self.telnet.send_line('')
        self.telnet.expect.assert_called_with([self.telnet.endmark], timeout=ANY)

    def test_send_line_checks_exit_code_if_expected_exit_code_is_provided(self):
        self.telnet.telnet = MagicMock()
        self.telnet.telnet.match.group = MagicMock(return_value='0')
        self.telnet.send_line('', expected_exit_code=0)
        self.telnet.telnet.sendline.assert_has_calls([call(''), call('echo $?')])

    def test_check_exit_code_does_not_raise_if_exit_code_is_as_expected(self):
        self.telnet.connect()
        self.telnet.telnet.expect_results = ['0', '/ #']
        exit_code = self.telnet._get_exit_code('/ #', 10)
        self.telnet._check_exit_code(exit_code, 0)

    def test_check_exit_code_raises_telnet_error_if_exit_code_is_not_as_expected(self):
        self.telnet.connect()
        self.telnet.telnet.expect_results = ['1', '/ #']
        with self.assertRaises(TelnetError):
            exit_code = self.telnet._get_exit_code('/ #', 10)
            self.telnet._check_exit_code(exit_code, 0)

    def test_expect_raises_telnet_timeout_exception_on_timeout(self):
        self.telnet.telnet = MagicMock()
        self.telnet.telnet.expect = MagicMock(side_effect=MockPexpect.TIMEOUT(None))
        with self.assertRaises(TelnetTimeout):
            self.telnet.expect(None)

    def test_expect_calls_disconnect_and_raises_telnet_error_on_communication_failure(self):
        self.telnet.telnet = MagicMock()
        self.telnet.telnet.expect = MagicMock(side_effect=MockPexpect.EOF(None))
        self.telnet.disconnect = MagicMock()
        with self.assertRaises(TelnetError):
            self.telnet.expect(None)
        self.telnet.disconnect.assert_called_once_with()

    def test_extended_process_information(self):
        test_data = 'some test data'
        self.telnet.telnet = MagicMock()
        self.telnet.telnet.match.group = MagicMock(return_value='1')
        self.telnet.telnet.before = test_data
        self.assertEqual(
            self.telnet.send_line(test_data, extended_process_information=True), (test_data, '', 1))
