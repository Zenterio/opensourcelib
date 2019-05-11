import queue

from k2.runner.timeout import TimeoutError, timeout


@timeout(0.5)
def test_that_times_out_blocked_on_a_queue():
    try:
        queue.Queue().get(timeout=2)
    except TimeoutError:
        print('test_that_times_out_blocked_on_a_queue aborted')


@timeout(0.5)
def test_that_times_out_while_sleeping():
    try:
        queue.Queue().get(timeout=2)
    except TimeoutError:
        print('test_that_times_out_while_sleeping aborted')
