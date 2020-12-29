from unittest import TestCase

from zaf.builtin.unittest.harness import ExtensionTestHarness
from zaf.config.manager import ConfigManager
from zaf.messages.dispatchers import LocalMessageQueue

from k2.cmd.run import RUN_COMMAND_ENDPOINT, TEST_RUN
from k2.runner import TEST_RUN_FINISHED, TEST_RUN_STARTED

from ..multirunner import MULTI_RUNNER_ENABLED, MultiRunner


class TestGtestRunner(TestCase):

    @staticmethod
    def create_harness():
        config = ConfigManager()
        config.set(MULTI_RUNNER_ENABLED, True)

        return ExtensionTestHarness(
            MultiRunner, config=config, endpoints_and_messages={
                RUN_COMMAND_ENDPOINT: [TEST_RUN],
            })

    def test_triggers_test_run_started_and_finished_on_test_run(self):
        with TestGtestRunner.create_harness() as harness:
            events = [TEST_RUN_STARTED, TEST_RUN_FINISHED]
            with LocalMessageQueue(harness.messagebus, events) as queue:
                harness.messagebus.trigger_event(TEST_RUN, RUN_COMMAND_ENDPOINT, None)
                self.assertEqual(queue.get(timeout=1).message_id, TEST_RUN_STARTED)
                self.assertEqual(queue.get(timeout=1).message_id, TEST_RUN_FINISHED)
