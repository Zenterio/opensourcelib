import threading
import unittest
from unittest.mock import ANY, Mock, patch

from ..threading import ExtendableTimer, LockableDict, LockableList, ResetableTimer

TIMEOUT = 5


class TestLockableList(unittest.TestCase):

    def test_initialize_empty(self):
        lock = LockableList()
        assert len(lock) == 0

    def test_initialize_with_data(self):
        lock = LockableList([1, 2, 3])
        assert lock == [1, 2, 3]

    def test_reading_the_data_property_acquires_the_lock(self):
        with patch('k2.utils.threading.RLock') as lock:
            LockableList().data
            lock().__enter__.assert_called_with()
            lock().__exit__.assert_called_with(ANY, ANY, ANY)

    def test_setting_the_data_property_releases_the_lock(self):
        with patch('k2.utils.threading.RLock') as lock:
            LockableList().data = [1, 2, 3]
            lock().__enter__.assert_called_with()
            lock().__exit__.assert_called_with(ANY, ANY, ANY)


class TestLockableDict(unittest.TestCase):

    def test_initialize_empty(self):
        d = LockableDict()
        self.assertFalse(d)

    def test_initialize_with_data(self):
        d = LockableDict({'k': 'v'})
        self.assertEqual(d, {'k': 'v'})

    def test_reading_data_aquires_the_lock(self):
        with patch('k2.utils.threading.RLock') as lock:
            d = LockableDict()
            lock.reset_mock()
            for k, v in d.items():
                self.assertEqual(lock().__enter__.call_count, 1)
                self.assertEqual(lock().__exit__.call_count, 0)
            self.assertEqual(lock().__exit__.call_count, 1)

    def test_adding_data_aquires_the_lock(self):
        with patch('k2.utils.threading.RLock') as lock:
            d = LockableDict()
            lock.reset_mock()
            d['k'] = 'v'
            self.assertEqual(lock().__enter__.call_count, 1)
            self.assertEqual(lock().__exit__.call_count, 1)

    def test_lock_with_lock(self):
        with patch('k2.utils.threading.RLock') as lock:
            d = LockableDict()
            lock.reset_mock()
            with d.lock:
                self.assertEqual(lock().__enter__.call_count, 1)
                self.assertEqual(lock().__exit__.call_count, 0)
            self.assertEqual(lock().__exit__.call_count, 1)

    def test_same_thread_can_do_atomic_transaction(self):
        with patch('k2.utils.threading.RLock') as lock:
            d = LockableDict()
            lock.reset_mock()
            with d.lock:
                d['k'] = 'v'
                del d['k']
                self.assertEqual(lock().__enter__.call_count, 3)
                self.assertEqual(lock().__exit__.call_count, 2)
            self.assertEqual(lock().__exit__.call_count, 3)


class TestResetableTimer(unittest.TestCase):

    def setUp(self):
        self._triggered = threading.Event()
        self.args = {}
        self.t = ResetableTimer(0, self._f, args=[1], kwargs={'y': 2})

    def tearDown(self):
        self.t.cancel()

    def wait_f(self, timeout=TIMEOUT):
        self._triggered.wait(timeout)

    def _f(self, x=None, y=None):
        self.args['x'] = x
        self.args['y'] = y
        self._triggered.set()

    def test_starts_and_executes_function_with_init_args_and_kwargs(self):
        self.t.start()
        self.wait_f()
        self.assertEqual(self.args['x'], 1)
        self.assertEqual(self.args['y'], 2)

    def test_args_and_kwargs_to_start_overrides_inits(self):
        self.t.start(args=['x'], kwargs={'y': 'y'})
        self.wait_f()
        self.assertEqual(self.args['x'], 'x')
        self.assertEqual(self.args['y'], 'y')

    def test_timer_can_be_restarted(self):
        self.t.start()
        self.wait_f()
        self.assertEqual(self.args['x'], 1)
        self.assertEqual(self.args['y'], 2)

        self._triggered.clear()
        self.t.start(args=['x'], kwargs={'y': 'y'})
        self.wait_f()
        self.assertEqual(self.args['x'], 'x')
        self.assertEqual(self.args['y'], 'y')

    def test_cancel_multiple_times_in_a_row_has_no_side_effect(self):
        self.t = ResetableTimer(TIMEOUT, self._f)
        self.t.start()
        self.t.cancel()
        self.t.cancel()

    def test_cancel_can_be_called_without_start(self):
        self.t = ResetableTimer(TIMEOUT, self._f)
        self.t.cancel()

    def test_is_started_returns_false_if_not_started(self):
        self.assertFalse(self.t.is_started)

    def test_is_started_returns_false_if_cancelled(self):
        self.t.start()
        self.t.cancel()
        self.assertFalse(self.t.is_started)

    def test_is_started_returns_true_if_started(self):
        self.t = ResetableTimer(TIMEOUT, self._f)
        self.t.start()
        self.assertTrue(self.t.is_started)


class TestExtendableTimer(unittest.TestCase):

    def setUp(self):
        self._triggered = threading.Event()
        self._unblock = threading.Event()
        self.unblock_f()
        self.args = {}
        self.t = ExtendableTimer(0, self._f, args=[1], kwargs={'y': 2})

    def tearDown(self):
        self.unblock_f()
        self.t.cancel()
        self.assertTrue(self.t.wait(TIMEOUT))

    def wait_f(self, timeout=TIMEOUT):
        self.assertTrue(self._triggered.wait(timeout))

    def block_f(self):
        self._unblock.clear()

    def unblock_f(self):
        self._unblock.set()

    def _f(self, x=None, y=None):
        self.args['x'] = x
        self.args['y'] = y
        self._triggered.set()
        self._unblock.wait(TIMEOUT)

    def _raise(self):
        try:
            raise Exception()
        finally:
            self._triggered.set()

    def test_starts_and_executes_function_with_init_args_and_kwargs(self):
        self.t.start()
        self.wait_f()
        self.assertEqual(self.args['x'], 1)
        self.assertEqual(self.args['y'], 2)

    def test_args_and_kwargs_to_start_overrides_inits(self):
        self.t.start(args=['x'], kwargs={'y': 'y'})
        self.wait_f()
        self.assertEqual(self.args['x'], 'x')
        self.assertEqual(self.args['y'], 'y')

    def test_can_be_used_without_args_and_kwargs(self):
        self.t = ExtendableTimer(0, self._f)
        self.assertEqual(self.t.args, [])
        self.assertEqual(self.t.kwargs, {})
        self.t.start()
        self.wait_f()

    def test_timer_can_be_restarted(self):
        self.t.start()
        self.wait_f()
        self.assertEqual(self.args['x'], 1)
        self.assertEqual(self.args['y'], 2)

        self._triggered.clear()
        self.t.start(args=['x'], kwargs={'y': 'y'})
        self.wait_f()
        self.assertEqual(self.args['x'], 'x')
        self.assertEqual(self.args['y'], 'y')

    def test_cancel_multiple_times_in_a_row_has_no_side_effect(self):
        self.t = ExtendableTimer(TIMEOUT, self._f)
        self.t.start()
        self.t.cancel()
        self.t.cancel()

    def test_cancel_can_be_called_without_start(self):
        self.t = ExtendableTimer(TIMEOUT, self._f)
        self.t.cancel()

    def test_is_started_returns_false_if_not_started(self):
        self.assertFalse(self.t.is_started)

    def test_is_started_returns_false_if_cancelled(self):
        self.t = ExtendableTimer(TIMEOUT, self._f)
        self.t.start()
        self.t.cancel()
        self.assertFalse(self.t.is_started)

    def test_is_started_returns_true_if_started(self):
        self.t = ExtendableTimer(TIMEOUT, self._f)
        self.t.start()
        self.assertTrue(self.t.is_started)

    def test_is_started_returns_true_if_started_and_completed(self):
        self.t = ExtendableTimer(0, self._f)
        self.t.start()
        self.wait_f()
        self.assertTrue(self.t.is_started)

    def test_is_cancelled_returns_false_if_never_started(self):
        self.assertFalse(self.t.is_cancelled)

    def test_is_cancelled_returns_false_if_not_cancelled_after_start(self):
        self.t = ExtendableTimer(TIMEOUT, self._f)
        self.t.start()
        self.assertFalse(self.t.is_cancelled)

    def test_is_cancelled_returns_true_if_cancelled_after_start(self):
        self.t = ExtendableTimer(TIMEOUT, self._f)
        self.t.start()
        self.t.cancel()
        self.assertTrue(self.t.is_cancelled)

    def test_can_extend_timer(self):
        self.t = ExtendableTimer(TIMEOUT, self._f)
        self.t.start()
        self.t.extend_interval(5)
        self.assertEqual(self.t._extra_interval, 5)

    def test_process(self):

        def mock_wait(timeout):
            if timeout == 2:
                self.t.extend_interval(4)
                return False
            elif timeout == 4:
                return False
            else:
                self.fail('Unexpected timeout value {to}'.format(to=timeout))

        self.t = ExtendableTimer(2, self._f)
        self.t._cancelled.wait = Mock(side_effect=mock_wait)
        self.t.start()
        self.wait_f()
        self.assertEqual(self.t._cancelled.wait.call_count, 2)

    def test_exception_is_stored(self):
        self.t = ExtendableTimer(0, self._raise)
        self.t.start()
        self.wait_f()
        self.assertIsInstance(self.t.exception, Exception)

    def test_wait_returns_true_if_function_completed(self):
        self.t.start()
        self.wait_f()
        self.assertTrue(self.t.wait(TIMEOUT))

    def test_wait_returns_false_if_function_not_completed(self):
        self.block_f()
        self.t.start()
        self._triggered.wait()
        self.assertFalse(self.t.wait(timeout=0))
