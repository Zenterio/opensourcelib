from zaf.builtin.unittest.harness import ExtensionTestHarness
from zaf.config.manager import ConfigManager

from k2.runner import TEST_RUN_STARTED
from k2.scheduler import ADD_TEST_CASES, RUN_QUEUE_EMPTY, RUN_QUEUE_INITIALIZED, SCHEDULER_ENDPOINT
from looper import LOOP_DURATION, LOOP_REPEATS
from looper.looper import Looper


def create_harness(duration=None, repeats=None):
    config = ConfigManager()
    config.set(LOOP_DURATION, duration)
    config.set(LOOP_REPEATS, repeats)

    return ExtensionTestHarness(
        Looper,
        config=config,
        endpoints_and_messages={
            SCHEDULER_ENDPOINT:
            [RUN_QUEUE_EMPTY, RUN_QUEUE_INITIALIZED, ADD_TEST_CASES, TEST_RUN_STARTED]
        })
