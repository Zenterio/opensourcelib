import queue
import unittest
from unittest.mock import Mock, patch

from zaf.application import AFTER_COMMAND, APPLICATION_ENDPOINT
from zaf.builtin.unittest.harness import ExtensionTestHarness
from zaf.config.manager import ConfigManager
from zaf.messages.dispatchers import LocalMessageQueue

from .. import REMOTE_ENABLED, REMOTE_PORT
from ..remote import RemoteServer, create_service
from .utils import DATA, ENDPOINT, ENTITY, MESSAGE, PICKLED_DATA, PICKLED_ENDPOINT, \
    PICKLED_ENDPOINTS, PICKLED_ENTITIES, PICKLED_ENTITY, PICKLED_MESSAGE, PICKLED_MESSAGES


class MockThreadedServer(object):

    def __init__(self, *args, **kwargs):
        self.queue = queue.Queue()
        self.clients = []

    def start(self):
        self.queue.get(timeout=1)

    def close(self):
        self.queue.put('stop')


class RemoteExtensionTest(unittest.TestCase):

    def test_enabling_using_config(self):
        with patch('zaf.builtin.remote.remote.ThreadedServer', new=MockThreadedServer):
            with create_harness(endpoints_and_messages={APPLICATION_ENDPOINT: [AFTER_COMMAND]},
                                config={REMOTE_ENABLED: True, REMOTE_PORT:
                                        REMOTE_PORT.default}) as harness:
                self.assertTrue(harness.extension._enabled)

        with create_harness(endpoints_and_messages={APPLICATION_ENDPOINT: [AFTER_COMMAND]},
                            config={REMOTE_ENABLED: False, REMOTE_PORT:
                                    REMOTE_PORT.default}) as harness:
            self.assertFalse(harness.extension._enabled)

    def test_server_is_closed_when_after_command_is_received(self):
        with patch('zaf.builtin.remote.remote.ThreadedServer', new=MockThreadedServer):
            with create_harness(endpoints_and_messages={APPLICATION_ENDPOINT: [AFTER_COMMAND]},
                                config={REMOTE_ENABLED: True, REMOTE_PORT:
                                        REMOTE_PORT.default}) as harness:
                harness.trigger_event(AFTER_COMMAND, APPLICATION_ENDPOINT)
                self.assertFalse(harness.extension.is_running())

    def test_server_is_force_closed_in_destroy_if_after_command_was_not_received(self):
        with patch('zaf.builtin.remote.remote.ThreadedServer', new=MockThreadedServer):
            harness = create_harness(
                endpoints_and_messages={APPLICATION_ENDPOINT: [AFTER_COMMAND]},
                config={
                    REMOTE_ENABLED: True,
                    REMOTE_PORT: REMOTE_PORT.default
                })

            harness.__enter__()
            harness.__exit__()

            self.assertFalse(harness.extension.is_running())


def create_harness(endpoints_and_messages, config):
    config_manager = ConfigManager()
    for id, value in config.items():
        config_manager.set(id, value)

    return ExtensionTestHarness(
        RemoteServer, endpoints_and_messages=endpoints_and_messages, config=config_manager)


class RemoteServiceTest(unittest.TestCase):

    def test_exposed_trigger_event_depickles_message_info_and_forwards_event(self):
        messagebus = Mock()
        service = create_service(messagebus)
        service.exposed_trigger_event(
            PICKLED_MESSAGE, PICKLED_ENDPOINT, PICKLED_ENTITY, PICKLED_DATA)
        messagebus.trigger_event.assert_called_with(MESSAGE, ENDPOINT, ENTITY, DATA)

    def test_exposed_send_request_depickles_message_info_and_forwards_request(self):
        messagebus = Mock()
        service = create_service(messagebus)
        service.exposed_send_request(
            PICKLED_MESSAGE, PICKLED_ENDPOINT, PICKLED_ENTITY, PICKLED_DATA)
        messagebus.send_request.assert_called_with(MESSAGE, ENDPOINT, ENTITY, DATA)

    def test_exposed_local_message_queue_depickles_message_info_and_returns_a_queue(self):
        messagebus = Mock()
        service = create_service(messagebus)
        queue = service.exposed_local_message_queue(
            PICKLED_MESSAGES, PICKLED_ENDPOINTS, PICKLED_ENTITIES)
        self.assertEqual(type(queue), LocalMessageQueue)
        self.assertEqual(queue._message_ids, [MESSAGE])
        self.assertEqual(queue._endpoint_ids, [ENDPOINT])
        self.assertEqual(queue._entities, [ENTITY])
