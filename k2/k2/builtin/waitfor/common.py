import datetime
import time

from zaf.extensions.extension import AbstractExtension, FrameworkExtension


def wait_for(predicate, timeout, poll_interval=1.0):
    """Wait for predicate function to return a truthy value."""
    start_time = datetime.datetime.now().timestamp()
    end_time = start_time + timeout

    value = predicate()
    if value:
        return value

    while datetime.datetime.now().timestamp() < end_time:
        value = predicate()
        if value:
            return value

        time.sleep(poll_interval)

    raise TimeoutError(
        'wait_for timed out when waiting for {predicate} with timeout {timeout}'.format(
            predicate=str(predicate), timeout=str(timeout)))


@FrameworkExtension('waitfor')
class WaitFor(AbstractExtension):
    pass
