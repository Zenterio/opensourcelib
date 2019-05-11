import unittest

from k2.builtin.waitfor.common import wait_for


class TestCommon(unittest.TestCase):

    def test_wait_for_times_out(self):

        def return_false():
            return False

        with self.assertRaises(TimeoutError):
            wait_for(return_false, timeout=0)

    def test_wait_for_polls_multiple_times(self):
        calls = 0

        def return_calls():
            nonlocal calls
            calls += 1

            if calls < 4:
                return False
            else:
                return calls

        calls = wait_for(return_calls, timeout=1, poll_interval=0)
        self.assertEqual(calls, 4)
