import threading
import unittest

from zaf.application import AFTER_COMMAND, APPLICATION_ENDPOINT
from zaf.builtin.unittest.harness import ExtensionTestHarness
from zaf.config.manager import ConfigManager
from zaf.messages.dispatchers import LocalMessageQueue
from zaf.messages.message import EndpointId, MessageId

from .. import BLOCKER_ENABLED, BLOCKER_ENDPOINT, BLOCKING_COMPLETED, BLOCKING_STARTED, \
    BLOCKING_TIMED_OUT, START_BLOCKING_ON_MESSAGE, STOP_BLOCKING_ON_MESSAGE, StartBlockingInfo
from ..blocker import Blocker

TEST_BLOCKER_ENDPOINT = EndpointId('TEST_BLOCKER_ENDPOINT', '')
TEST_BLOCKER_BLOCK = MessageId('TEST_BLOCKER_BLOCK', '')


class BlockerTest(unittest.TestCase):

    def test_enabling_using_config(self):
        config = ConfigManager()
        config.set(BLOCKER_ENABLED, True)

        with ExtensionTestHarness(Blocker, endpoints_and_messages={APPLICATION_ENDPOINT:
                                                                   [AFTER_COMMAND]},
                                  config=config) as harness:
            self.assertTrue(harness.extension._enabled)

        with ExtensionTestHarness(
                Blocker, endpoints_and_messages={TEST_BLOCKER_ENDPOINT: [TEST_BLOCKER_BLOCK],
                                                 APPLICATION_ENDPOINT: [AFTER_COMMAND]}) as harness:
            self.assertFalse(harness.extension._enabled)

    def test_blocking_until_stop_blocking_is_sent(self):
        config = ConfigManager()
        config.set(BLOCKER_ENABLED, True)

        with ExtensionTestHarness(Blocker, endpoints_and_messages={
                TEST_BLOCKER_ENDPOINT: [TEST_BLOCKER_BLOCK], APPLICATION_ENDPOINT: [AFTER_COMMAND]
        }, config=config) as harness:

            id_futures = harness.send_request(
                START_BLOCKING_ON_MESSAGE,
                BLOCKER_ENDPOINT,
                data=StartBlockingInfo(
                    message_id=TEST_BLOCKER_BLOCK,
                    endpoint_id=TEST_BLOCKER_ENDPOINT,
                    entity=None,
                    timeout=3))
            id = id_futures.wait(timeout=1)[0].result(timeout=1)
            with LocalMessageQueue(harness.messagebus,
                                   [BLOCKING_STARTED, BLOCKING_COMPLETED]) as queue:
                thread = threading.Thread(
                    target=harness.send_request, args=[TEST_BLOCKER_BLOCK, TEST_BLOCKER_ENDPOINT])
                thread.start()

                self.assertEqual(queue.get(timeout=1).entity, id)
                self.assertTrue(thread.is_alive())

                harness.send_request(
                    STOP_BLOCKING_ON_MESSAGE, BLOCKER_ENDPOINT, entity=id).wait(timeout=1)
                thread.join()
                self.assertFalse(thread.is_alive())
                self.assertEqual(queue.get(timeout=1).entity, id)

    def test_blocking_timeout_send_timeout_event(self):
        config = ConfigManager()
        config.set(BLOCKER_ENABLED, True)

        with ExtensionTestHarness(Blocker, endpoints_and_messages={
                TEST_BLOCKER_ENDPOINT: [TEST_BLOCKER_BLOCK], APPLICATION_ENDPOINT: [AFTER_COMMAND]
        }, config=config) as harness:

            id_futures = harness.send_request(
                START_BLOCKING_ON_MESSAGE,
                BLOCKER_ENDPOINT,
                data=StartBlockingInfo(
                    message_id=TEST_BLOCKER_BLOCK,
                    endpoint_id=TEST_BLOCKER_ENDPOINT,
                    entity=None,
                    timeout=0))
            id = id_futures.wait(timeout=1)[0].result(timeout=1)
            with LocalMessageQueue(harness.messagebus, [BLOCKING_TIMED_OUT]) as queue:
                harness.send_request(TEST_BLOCKER_BLOCK, TEST_BLOCKER_ENDPOINT)
                self.assertEqual(queue.get(timeout=1).entity, id)

    def test_ongoing_blockers_are_stopped_by_destroy(self):
        config = ConfigManager()
        config.set(BLOCKER_ENABLED, True)

        harness = ExtensionTestHarness(
            Blocker,
            endpoints_and_messages={
                TEST_BLOCKER_ENDPOINT: [TEST_BLOCKER_BLOCK],
                APPLICATION_ENDPOINT: [AFTER_COMMAND]
            },
            config=config)
        try:
            harness.__enter__()
            with LocalMessageQueue(harness.messagebus, [BLOCKING_COMPLETED]) as queue:
                id_futures = harness.send_request(
                    START_BLOCKING_ON_MESSAGE,
                    BLOCKER_ENDPOINT,
                    data=StartBlockingInfo(
                        message_id=TEST_BLOCKER_BLOCK,
                        endpoint_id=TEST_BLOCKER_ENDPOINT,
                        entity=None,
                        timeout=1))
                id = id_futures.wait(timeout=1)[0].result(timeout=1)

                thread = threading.Thread(
                    target=harness.send_request, args=[TEST_BLOCKER_BLOCK, TEST_BLOCKER_ENDPOINT])
                thread.start()

                harness.extension.destroy()
                self.assertEqual(queue.get(timeout=1).entity, id)
                thread.join()
        except AssertionError:
            raise
        except Exception:
            harness.extension.destroy()
