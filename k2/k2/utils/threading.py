from collections import UserDict, UserList
from threading import Event, Lock, RLock, Thread, Timer


class LockableList(UserList):

    def __init__(self, initlist=None):
        self.lock = RLock()
        super().__init__(initlist)

    @property
    def data(self):
        with self.lock:
            return self._data

    @data.setter
    def data(self, value):
        with self.lock:
            self._data = value


class LockableDict(UserDict):

    def __init__(self, initialdata=None):
        self.lock = RLock()
        super().__init__(initialdata)

    @property
    def data(self):
        with self.lock:
            return self._data

    @data.setter
    def data(self, value):
        with self.lock:
            self._data = value


class ResetableTimer(object):

    def __init__(self, interval, function, args=None, kwargs=None):
        self._lock = Lock()
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def start(self, args=None, kwargs=None):
        """
        Start the timer thread.

        If the timer is already started, but has not been fired, the previous
        start is cancelled and the timer reset again.

        :param args: if set, used instead of args from constructor
        :param kwargs: if set, used instead of kwargs from constructor
        """
        if args is None:
            args = self.args

        if kwargs is None:
            kwargs = self.kwargs

        with self._lock:
            if self._timer:
                self._timer.cancel()
            self._timer = Timer(self.interval, self.function, args=args, kwargs=kwargs)
            self._timer.start()

    def cancel(self):
        """Cancel the timer if it has not already fired."""
        with self._lock:
            if self._timer:
                self._timer.cancel()
                self._timer = None

    @property
    def is_started(self):
        return bool(self._timer)


class ExtendableTimer(object):

    def __init__(self, interval, function, args=None, kwargs=None):
        """
        Execute function after interval seconds.

        The interval can be extended by calling the extend_interval method.

        The timer can be cancelled, and restarted multiple times.

        :param interval: interval in seconds, before the timer is triggered
        :param function: the function to be executed
        :param args: args to be passed when executing the function
        :param kwargs: kwargs to be passed when executing the function
        """
        self._lock = Lock()
        self._thread = None
        self._cancelled = Event()
        self._extra_interval = 0
        self.exception = None
        self.interval = interval
        self.function = function
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}

    def start(self, args=None, kwargs=None):
        """
        Start the timer.

        If the timer is already started, but has not been fired, the previous
        start is cancelled and the timer reset again.

        :param args: if set, used instead of args from constructor
        :param kwargs: if set, used instead of kwargs from constructor
        """
        if args is None:
            args = self.args
        if kwargs is None:
            kwargs = self.kwargs
        if self.is_started:
            self.cancel()
        with self._lock:
            self._cancelled.clear()
            self.exception = None
            self._extra_interval = 0
            self._thread = Thread(
                target=self._process, args=[self.function, self.interval, args, kwargs])
            self._thread.start()

    def extend_interval(self, interval):
        """
        Extend timer with interval seconds.

        :param interval: interval in seconds
        """
        with self._lock:
            self._extra_interval += interval

    def cancel(self):
        """Cancel the timer if it has not already fired."""
        with self._lock:
            self._cancelled.set()
            self._thread = None

    @property
    def is_started(self):
        """
        Return true if the timer is started.

        Returns true also if the function is done executing.
        """
        with self._lock:
            return not self._cancelled.is_set() and self._thread

    @property
    def is_cancelled(self):
        """Return True if the timer is cancelled."""
        return self._cancelled.is_set()

    def wait(self, timeout=None):
        """
        Wait until the scheduled function has been processed, or cancelled.

        Wait returns True if it was successful.
        Returns False if the wait exceeded the timeout and the timer thread is still
        alive.

        :param timeout: timeout in seconds
        :returns: True or False
        """
        try:
            self._thread.join(timeout=timeout)
            return not self._thread.is_alive()
        except AttributeError:
            # in case thread has been cancelled (none) while waiting
            pass
        return True

    def _process(self, function, interval, args, kwargs):
        """
        Perform waiting and later call function with args and kwargs.

        This should not be called directly. It is intended to be run in a separate
        thread by the class itself.

        It is implemented by using the wait method of a threading.Event().

        It is optimized to have as few event.wait() as possible to reduce the overhead
        of system timers.

        :param function: the function to call
        :param interval: the initial waiting time
        :param args: args to be passed when executing the function
        :param kwargs: kwargs to be passed when executing the function
        """
        try:
            while True:
                timeout = self._get_extra_interval() + interval
                interval = 0  # only used first iteration
                if self.is_started:
                    if timeout > 0:
                        if self._cancelled.wait(timeout=timeout):
                            break  # cancelled
                        else:
                            # not cancelled, loop again to see if interval has
                            # been extended.
                            pass
                    else:
                        function(*args, **kwargs)
                        break
                else:
                    # cancelled
                    break
        except Exception as e:
            self.exception = e

    def _get_extra_interval(self):
        with self._lock:
            interval = self._extra_interval
            self._extra_interval = 0
            return interval
