import unittest
from unittest.mock import patch

from zaf.application import AFTER_COMMAND, BEFORE_COMMAND
from zaf.builtin.unittest.harness import ExtensionTestHarness
from zaf.config.manager import ConfigManager

from k2 import CRITICAL_ABORT
from k2.builtin.commandtimeout import COMMAND_TIMEOUT, COMMAND_TIMEOUT_ENDPOINT
from k2.builtin.commandtimeout.commandtimeout import CommandTimeout
from k2.cmd.run import RUN_COMMAND_ENDPOINT


class TestCommandTimeout(unittest.TestCase):

    def test_critical_abort_is_triggered_on_timeout(self):
        with _create_harness(timeout='0') as h, \
                patch('k2.builtin.commandtimeout.commandtimeout._ensure_exit') as ensure_exit:
            with h.message_queue([CRITICAL_ABORT], [COMMAND_TIMEOUT_ENDPOINT]) as queue:
                h.trigger_event(BEFORE_COMMAND, RUN_COMMAND_ENDPOINT)
                queue.get(timeout=1)
                ensure_exit.assert_called_with(60)

    def test_after_command_stops_the_dispatcher(self):
        with _create_harness() as h:
            with h.message_queue([CRITICAL_ABORT], [COMMAND_TIMEOUT_ENDPOINT]) as queue:
                h.trigger_event(BEFORE_COMMAND, RUN_COMMAND_ENDPOINT)
                h.trigger_event(AFTER_COMMAND, RUN_COMMAND_ENDPOINT)
                h.messagebus.wait_for_not_active(timeout=1)
                self.assertTrue(queue.empty())

    def test_destroy_stops_the_dispatcher(self):
        with _create_harness() as h:
            with h.message_queue([CRITICAL_ABORT], [COMMAND_TIMEOUT_ENDPOINT]) as queue:
                h.trigger_event(BEFORE_COMMAND, RUN_COMMAND_ENDPOINT)

        h.messagebus.wait_for_not_active(timeout=1)
        self.assertTrue(queue.empty())


def _create_harness(timeout='10'):
    config = ConfigManager()
    config.set(COMMAND_TIMEOUT, timeout)

    return ExtensionTestHarness(
        CommandTimeout,
        config=config,
        endpoints_and_messages={
            RUN_COMMAND_ENDPOINT: [BEFORE_COMMAND, AFTER_COMMAND]
        })
