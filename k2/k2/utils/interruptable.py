"""
Provides interruptable replacements for some Python uninterruptable built-ins.

Python has a limitation where function calls to the C API can not be interrupted
without using signals. For example, a call to time.sleep() can be interrupted by
SIGINT but not by an exception being raised.

K2 uses exceptions to abort on-going test runs. As per the above, this is not
going to work well if a test case is in the process of performing a blocking
call to an uninterruptable function.

To remedy this issue, this module provides some interruptable replacements that
provides a mechanism to return control to the Python intepreter, so that
exceptions may be handled.

This module is applied by importing and monkey-patching the appropriate packages.
As such, it is important that this imported and applied as early in the start-up
process as possible.
"""

import functools
import weakref
from collections import defaultdict

_SLEEP_INTERVAL = 0.5


@functools.lru_cache(maxsize=1)
def _patch_sleep():
    """
    Replace time.sleep() with an interruptable equivalent.

    Control is returned to the Python interpreter at a regular interval by
    dividing the total time to sleep up into smaller intervals.
    """
    from time import sleep as python_sleep
    import time

    def interruptable_sleep(secs):
        while secs > 0:
            python_sleep(min(secs, _SLEEP_INTERVAL))
            secs = secs - _SLEEP_INTERVAL

    time.sleep = interruptable_sleep


_THREAD_ID_TO_CONDITION_REFERENCE_MAP = defaultdict(set)


@functools.lru_cache(maxsize=1)
def _patch_threading_condition_wait():
    """
    Replace threading.Condition with an interruptable equivalent.

    Most of the blocking mechanisms in threading.Condition are implemented in
    the C layer. Control is not returned to the Python intepreter until the
    condition is fulfilled.

    To remedy this, a reference to each threading.Condition instance created
    is stored and may later be used to induce a suprious wakeup in all
    conditions that was created by a specific thread. In doing so, control
    of that thread is returned to the Python intepreter.
    """
    import threading
    PythonCondition = threading.Condition

    class InterruptableCondition(PythonCondition):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            thread_id = threading.get_ident()
            _THREAD_ID_TO_CONDITION_REFERENCE_MAP[thread_id].add(weakref.ref(self))
            weakref.finalize(self, _THREAD_ID_TO_CONDITION_REFERENCE_MAP[thread_id].discard, self)

    threading.Condition = InterruptableCondition


@functools.lru_cache(maxsize=1)
def _patch_log_handler_lock():
    """
    Replace logging.Handler.handle to always clean up locks.

    When injecting exceptions in the test case thread it's not uncommon
    that the execution is somewhere in the logging.
    If the thread is in middle of acquiring a lock when the exception occurs
    the lock might be taken without ever being released again.
    This makes K2 hang forever.

    To remedy this a special version of handle is used that always tries
    to release the lock to make sure that it's not left behind.
    """

    from logging import Handler

    def handle(self, record):
        # Special version of logging.Handler.handle
        rv = self.filter(record)
        if rv:
            try:
                self.acquire()
                self.emit(record)
            finally:
                try:
                    self.release()
                except RuntimeError:
                    pass
        return rv

    Handler.handle = handle


def induce_spurious_wakeup_for_all_conditions_associated_with_thread(thread_id):
    for condition_reference in _THREAD_ID_TO_CONDITION_REFERENCE_MAP[thread_id]:
        condition = condition_reference()
        if condition is not None:
            with condition:
                condition.notify_all()


def apply_all_patches():
    _patch_sleep()
    _patch_threading_condition_wait()
    _patch_log_handler_lock()
