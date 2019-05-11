import unittest
from unittest.mock import MagicMock

from ..future import Future, FuturesCollection


class TestFuture(unittest.TestCase):

    def setUp(self):
        self.f = Future()

    def test_raises_exception_if_run_is_called_multiple_times(self):
        self.f.run(MagicMock())
        with self.assertRaises(Exception):
            self.f.run(MagicMock())

    def test_run_with_only_args(self):
        m = MagicMock()
        self.f.run(m, 1, 2, 3)
        m.assert_called_once_with(1, 2, 3)

    def test_run_with_only_kwargs(self):
        m = MagicMock()
        self.f.run(m, a=1, b=2, c=3)
        m.assert_called_once_with(a=1, b=2, c=3)

    def test_run_with_args_and_kwargs(self):
        m = MagicMock()
        self.f.run(m, 1, a=2)
        m.assert_called_once_with(1, a=2)

    def test_return_value_is_stored(self):
        my_return_value = object()
        m = MagicMock(return_value=my_return_value)
        self.f.run(m)
        self.assertEqual(self.f.result(timeout=0.1), my_return_value)

    def test_exception_is_stored(self):
        my_exception = Exception()
        m = MagicMock(side_effect=my_exception)
        self.f.run(m)
        self.assertEqual(self.f.exception(timeout=0.1), my_exception)

    def test_exception_may_be_raised_when_getting_results(self):
        my_exception = Exception()
        m = MagicMock(side_effect=my_exception)
        self.f.run(m)
        with self.assertRaises(Exception):
            self.f.results(timeout=0.1)

    def test_future_can_have_a_done_callback(self):
        m = MagicMock()
        self.f.add_done_callback(m)
        self.f.run(MagicMock())
        m.assert_called_once_with(self.f)

    def test_future_can_have_multiple_done_callbacks(self):
        m1 = MagicMock()
        m2 = MagicMock()
        self.f.add_done_callback(m1)
        self.f.add_done_callback(m2)
        self.f.run(MagicMock())
        m1.assert_called_once_with(self.f)
        m2.assert_called_once_with(self.f)


class TestFuturesCollection(unittest.TestCase):

    def test_as_completed_with_single_future(self):
        f1 = Future()
        fc = FuturesCollection((f1, ))
        f1.run(MagicMock())
        completed = fc.as_completed(timeout=0.1)
        self.assertEqual(next(completed), f1)

    def test_as_completed_with_mutiple_futures(self):
        f1 = Future()
        f2 = Future()
        fc = FuturesCollection((f1, f2))
        f1.run(MagicMock())
        completed = fc.as_completed(timeout=0.1)
        self.assertEqual(next(completed), f1)
        f2.run(MagicMock())
        self.assertEqual(next(completed), f2)

    def test_as_completed_raises_on_timeout(self):
        f1 = Future()
        fc = FuturesCollection((f1, ))
        completed = fc.as_completed(timeout=0.0001)
        with self.assertRaises(Exception):
            next(completed)

    def test_wait_for_future(self):
        f1 = Future()
        fc = FuturesCollection((f1, ))
        f1.run(MagicMock())
        fc.wait()
