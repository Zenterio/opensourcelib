import collections
import concurrent.futures
from concurrent.futures.thread import _WorkItem


class Future(concurrent.futures.Future):
    """Encapsulates the asynchronous execution of a callable."""

    def run_and_raise_on_exception(self, callable, *args, **kwargs):
        self.run(callable, *args, **kwargs)
        self.result(timeout=0)

    def run(self, callable, *args, **kwargs):
        """Call the callable and stores the result in this future."""
        if self.done():
            raise Exception('run() called multiple times on the same future.')
        _WorkItem(self, callable, args, kwargs).run()


class FuturesCollection(collections.UserList):
    """Holds a collection of futures."""

    def as_completed(self, timeout=None):
        """Return a generator that yields futures as they are resolved."""
        return concurrent.futures.as_completed(self.data, timeout)

    def wait(self, timeout=None):
        """Block until all futures in the collection are resolved."""
        list(self.as_completed(timeout))
        return self
