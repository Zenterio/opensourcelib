import logging
import signal
import time

from zaf.application import ApplicationContext
from zaf.application.application import Application, ApplicationConfiguration
from zaf.application.signalhandler import SignalHandler
from zaf.builtin.changelog import ChangeLogType
from zaf.commands.command import CommandId
from zaf.extensions.extension import AbstractExtension, FrameworkExtension, get_logger_name

logger = logging.getLogger(get_logger_name('zaf', 'zafapp'))
logger.addHandler(logging.NullHandler())


class ZafAppStandalone(Application):

    def __init__(self):
        super().__init__(
            ApplicationConfiguration(
                'zafappstandalone',
                version='4.56',
                root_package='zaf',
                application_context=ApplicationContext.STANDALONE,
                changelog_type=ChangeLogType.CONFIGURABLE),
            signalhandler=TestSignalHandler())
        self.extension_manager.add_extension(ZafTestAppExtension)
        self.extension_manager.enable_extension(ZafTestAppExtension)


class ZafAppExtendable(Application):

    def __init__(self):
        super().__init__(
            ApplicationConfiguration(
                'zafapp',
                version='1.23',
                root_package='zaf',
                application_context=ApplicationContext.EXTENDABLE,
                changelog_type=ChangeLogType.ZNAKE),
            signalhandler=TestSignalHandler())
        self.extension_manager.add_extension(ZafTestAppExtension)
        self.extension_manager.enable_extension(ZafTestAppExtension)


class TestSignalHandler(SignalHandler):

    def __init__(self):
        super().__init__()
        self.register_handler(signal.SIGINT, self.handler)
        self.register_handler(signal.SIGABRT, self.handler)
        self.register_handler(signal.SIGTERM, self.handler)

    def handler(self, sig, frame):
        print('Handles sig={sig} (frame={frame})'.format(sig=sig, frame=frame), flush=True)


def busy_sleep(core):
    """Sleep for 2 seconds."""
    print('starting to sleep', flush=True)
    sec = 2
    deadline = time.time() + sec
    while deadline > time.time():
        time.sleep(0.01)
    print('done sleeping', flush=True)


def test_command(core):
    pass


ZAF_TEST_APP_SLEEP_COMMAND = CommandId('sleep', busy_sleep.__doc__, busy_sleep, [])
ZAF_TEST_APP_TESTCMD_COMMAND = CommandId('testcmd', 'Test command', test_command, [])


@FrameworkExtension(
    name='zaftestappextension', commands=[ZAF_TEST_APP_SLEEP_COMMAND, ZAF_TEST_APP_TESTCMD_COMMAND])
class ZafTestAppExtension(AbstractExtension):
    """Extends the ZAF Test Application."""

    def __init__(self, config, instances):
        pass
