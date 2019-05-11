import unittest
from unittest.mock import MagicMock, call, patch

from zaf.builtin.unittest.harness import ExtensionTestHarness
from zaf.component.manager import ComponentManager
from zaf.config.manager import ConfigManager

from .. import REMOTE_CLIENT_ENABLED
from ..client import RemoteClient, RemoteClientExtension, RemoteError
from .utils import DATA, ENDPOINT, ENTITY, MESSAGE, PICKLED_DATA, PICKLED_ENDPOINT, \
    PICKLED_ENDPOINTS, PICKLED_ENTITIES, PICKLED_ENTITY, PICKLED_MESSAGE, PICKLED_MESSAGES


class RemoteClientExtensionTest(unittest.TestCase):

    def test_enabling_remote_client_registers_component(self):
        component_manager = ComponentManager()
        component_manager.clear_component_registry()

        config = ConfigManager()
        config.set(REMOTE_CLIENT_ENABLED, True)

        with ExtensionTestHarness(RemoteClientExtension, config=config):
            self.assertIn('RemoteClient', component_manager.COMPONENT_REGISTRY)


class RemoteClientTest(unittest.TestCase):

    def test_connect_retries_to_connect(self):
        with patch('rpyc.connect', side_effect=[Exception, Exception, 'hej']) as m, \
                patch('time.sleep'):
            client = RemoteClient()
            client.connect()

            self.assertIsNotNone(client.connection)
            m.assert_has_calls(
                [
                    call('localhost', 18861, config={
                        'allow_all_attrs': True
                    }),
                    call('localhost', 18861, config={
                        'allow_all_attrs': True
                    }),
                    call('localhost', 18861, config={
                        'allow_all_attrs': True
                    }),
                ])

    def test_connect_fails_after_multiple_tries(self):
        with patch('rpyc.connect', side_effect=Exception), \
                patch('time.sleep'):
            client = RemoteClient()

            self.assertRaises(RemoteError, client.connect)

    def test_trigger_event_calls_proxy_object_with_pickled_arguments(self):
        client = RemoteClient()
        client.connection = MagicMock()

        client.trigger_event(MESSAGE, ENDPOINT, ENTITY, DATA)
        client.connection.root.trigger_event(
            PICKLED_MESSAGE, PICKLED_ENDPOINT, PICKLED_ENTITY, PICKLED_DATA)

    def test_send_request_calls_proxy_object_with_pickled_arguments(self):
        client = RemoteClient()
        client.connection = MagicMock()

        client.send_request(MESSAGE, ENDPOINT, ENTITY, DATA)
        client.connection.root.send_request(
            PICKLED_MESSAGE, PICKLED_ENDPOINT, PICKLED_ENTITY, PICKLED_DATA)

    def test_local_message_queue_calls_proxy_object_with_pickled_arguments(self):
        client = RemoteClient()
        client.connection = MagicMock()

        client.local_message_queue([MESSAGE], [ENDPOINT], [ENTITY])
        client.connection.root.local_message_queue(
            PICKLED_MESSAGES, PICKLED_ENDPOINTS, PICKLED_ENTITIES)
