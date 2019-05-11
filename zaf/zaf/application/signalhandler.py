import signal

_ALL_SIGNALS = {v for k, v in signal.__dict__.items() if k.startswith('SIG')}
_SIGNALS_THAT_CAN_BE_HANDLED = _ALL_SIGNALS - {0, signal.SIGKILL, signal.SIGSTOP}


class SignalHandler(object):
    """
    Manage signal handlers.

    Signal handlers are set up when the activate() method is called. The
    original signal handlers are restored when the deactivate() method is
    called.

    To provide custom signal handlers, call the register_handler() method. If a
    signal is caught and no custom signal handler is registered for that
    signal, the original signal handler is called instead.

    When a signal is caught, a flag is set in the Python VM. This flag is used
    to signal to the Python VM to run the signal handler at a later time in the
    main thread.

    Inheriting signal handlers can retrieve the MessageBus from this base class
    to be able to trigger events to the rest of the application.
    """

    def __init__(self):
        self._original_signal_handlers = {}
        self._signal_handlers = {}
        self.messagebus = None

    def activate(self, messagebus):
        """
        Activate signal handling.

        Back up the original handlers and set custom handlers.

        :param messagebus: the application message bus
        """
        self.messagebus = messagebus
        for sig in _SIGNALS_THAT_CAN_BE_HANDLED:
            self._register_handler(sig)

    def deactivate(self):
        """
        Deactivate signal handling.

        Restore original handlers.
        """
        for sig in _SIGNALS_THAT_CAN_BE_HANDLED:
            self._deregister_handler(sig)

    def register_handler(self, sig, handler):
        """Register a custom signal handler."""
        if sig not in _SIGNALS_THAT_CAN_BE_HANDLED:
            raise Exception('Can not register handler for unknown signal {sig}'.format(sig=sig))
        self._signal_handlers[sig] = handler

    def _register_handler(self, sig):
        self._original_signal_handlers[sig] = signal.getsignal(sig)
        signal.signal(sig, self._handle_signal)

    def _deregister_handler(self, sig):
        signal.signal(sig, self._original_signal_handlers[sig])

    def _handle_signal(self, sig, frame):
        handler = self._signal_handlers.get(sig, None)
        if handler is None:
            handler = self._original_signal_handlers[sig]

        if callable(handler):
            return handler(sig, frame)
