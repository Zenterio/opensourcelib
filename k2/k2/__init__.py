# First thing that happens, so other modules can use perf_counter and process_time
# relative to starting point.

try:
    from .version import __version__
except Exception:
    __version__ = None
__version__ = '0.0.0' if not __version__ else __version__

try:
    from time import perf_counter, process_time
    from zaf.messages.message import EndpointId, MessageId

    PERF_COUNTER_K2_START = perf_counter()
    PROCESS_TIME_K2_START = process_time()

    ABORT = MessageId(
        'ABORT', """
        Triggered when K2 core receives a SIGINT.
        Informs all extensions to shut down.

        data: None
        """)

    CRITICAL_ABORT = MessageId(
        'CRITICAL_ABORT', """
        Triggered when K2 receives a second SIGINT or a SIGABRT.
        Informs all extensions to shut down right now.

        data: None
        """)

    CRITICAL_EXTENSION_ERROR = MessageId(
        'CRITICAL_EXTENSION_ERROR', """
        Triggered by extensions to indicate that a critical error has occurred.

        data: message
        """)

    K2_APPLICATION_ENDPOINT = EndpointId(
        'k2application', """
        The K2 application endpoint
        """)

except ImportError:
    pass
