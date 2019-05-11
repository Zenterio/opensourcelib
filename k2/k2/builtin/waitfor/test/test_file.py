import unittest
from unittest.mock import Mock

from k2.builtin.waitfor.file import WaitForFile


class TestFile(unittest.TestCase):

    def test_wait_for_match_times_out(self):
        exec_mock = Mock()
        exec_mock.send_line.return_value = 'content'
        wait_file = WaitForFile(exec_mock)

        with self.assertRaises(TimeoutError):
            wait_file.wait_for_match('file1', 'pattern', timeout=0)

    def test_wait_for_match_returns_match_object(self):
        exec_mock = Mock()
        exec_mock.send_line.return_value = 'content'
        wait_file = WaitForFile(exec_mock)

        m = wait_file.wait_for_match('file1', r'con(\w+)', poll_interval=0)
        self.assertEqual(m.group(1), 'tent')
        exec_mock.send_line.assert_called_once()

    def test_wait_for_match_polls_multiple_times(self):
        exec_mock = Mock()
        exec_mock.send_line.side_effect = ['1', '2', '3']
        wait_file = WaitForFile(exec_mock)

        m = wait_file.wait_for_match('file1', r'(3)', poll_interval=0)
        self.assertEqual(m.group(1), '3')
        self.assertEqual(exec_mock.send_line.call_count, 3)

    def test_wait_for_match_non_zero_exit_code_treated_as_non_match(self):
        exec_mock = Mock()
        exec_mock.send_line.side_effect = [Exception, 'content']
        wait_file = WaitForFile(exec_mock)

        m = wait_file.wait_for_match('file1', r'content', poll_interval=0)
        self.assertEqual(m.group(0), 'content')
        self.assertEqual(exec_mock.send_line.call_count, 2)
