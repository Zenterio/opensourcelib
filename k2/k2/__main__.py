import logging
import os
import sys

from zaf.application import ApplicationContext
from zaf.application.application import Application, ApplicationConfiguration

from k2 import __version__
from k2.signal.signalhandler import ApplicationSignalHandler
from k2.utils.interruptable import apply_all_patches

apply_all_patches()  # noqa

logger = logging.getLogger()


def main():

    def _main():
        exit_code = 1
        try:
            configuration = ApplicationConfiguration(
                'k2',
                entrypoint='zk2',
                cli=True,
                version=__version__,
                root_package='k2',
                application_context=ApplicationContext.EXTENDABLE)
            signalhandler = ApplicationSignalHandler()
            exit_code = Application(
                configuration,
                entry_points=['zaf.addons', 'k2.addons', 'k2.local_addons'],
                signalhandler=signalhandler).run()
        except Exception as e:
            if logger.hasHandlers():
                logger.debug(str(e), exc_info=True)
                logger.error(str(e))
            else:
                logger.error(str(e), exc_info=True)
        sys.exit(exit_code)

    if os.getenv('K2_ENABLE_TRACE_PROFILER', False):
        from pytracing import TraceProfiler
        tp = TraceProfiler(output=open('./trace.out', 'w'))
        with tp.traced():
            _main()
    else:
        _main()


if __name__ == '__main__':
    main()
