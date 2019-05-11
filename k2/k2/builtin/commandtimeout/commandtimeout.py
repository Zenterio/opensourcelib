import os
import threading
import time

from zaf.application import AFTER_COMMAND, BEFORE_COMMAND
from zaf.component.decorator import requires
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, FrameworkExtension
from zaf.messages.decorator import callback_dispatcher, concurrent_dispatcher

from k2 import CRITICAL_ABORT
from k2.builtin.commandtimeout import COMMAND_TIMEOUT, COMMAND_TIMEOUT_ENDPOINT, \
    COMMAND_TIMEOUT_EXIT_DELAY
from k2.utils.timestring import parse_time


@FrameworkExtension(
    name='commandtimeout',
    config_options=[
        ConfigOption(COMMAND_TIMEOUT, required=False),
        ConfigOption(COMMAND_TIMEOUT_EXIT_DELAY, required=True),
    ],
    endpoints_and_messages={
        COMMAND_TIMEOUT_ENDPOINT: [CRITICAL_ABORT],
    },
    activate_on=[COMMAND_TIMEOUT])
class CommandTimeout(AbstractExtension):
    """
    Adds the possibility to timeout the execution of a K2 command if takes too long.

    The timeout is accomplished by triggering a CRITICAL_ABORT event that should
    result in an urgent but normal termination of the command, including writing
    reports and logs.
    If CRITICAL_ABORT is not enough the K2 process will be terminated with
    os._exit.
    """

    def __init__(self, config, instances):
        self._timeout = parse_time(config.get(COMMAND_TIMEOUT))
        self._hard_exit_timeout = config.get(COMMAND_TIMEOUT_EXIT_DELAY)
        self._command_complete_event = threading.Event()

    @concurrent_dispatcher([BEFORE_COMMAND])
    @requires(messagebus='MessageBus')
    def before_command(self, message, messagebus):
        if not self._command_complete_event.wait(timeout=self._timeout):
            try:
                messagebus.trigger_event(CRITICAL_ABORT, COMMAND_TIMEOUT_ENDPOINT)
            finally:
                _ensure_exit(self._hard_exit_timeout)

    @callback_dispatcher([AFTER_COMMAND])
    def after_command(self, message):
        self._command_complete_event.set()

    def destroy(self):
        self._command_complete_event.set()


def _ensure_exit(hard_exit_timeout):

    def _internal_ensure_exit():
        time.sleep(hard_exit_timeout)
        os._exit(3)

    t = threading.Thread(target=_internal_ensure_exit, daemon=True)
    t.start()
