import unittest

from zaf.messages.message import MessageId
from zaf.messages.messagebus import MessageBus

import k2.runner

from .. import messages


class TestMessages(unittest.TestCase):

    def test_all_defined_messages_are_registered(self):
        """
        Test that all message_ids are registered.

        This assumes that all defined message_ids in the module should be registered.
        If this is no longer the case this test case is no longer valid and should be replaced.
        """
        all_message_ids = [
            message_id for message_id in dir(messages) if isinstance(message_id, MessageId)
        ]

        messagebus = MessageBus(component_factory=None)
        messagebus.define_endpoints_and_messages(messages.runner_endpoint_with_messages())

        assert messagebus.is_endpoint_defined(k2.runner.RUNNER_ENDPOINT)
        for message_id in all_message_ids:
            assert messagebus.is_message_defined_for_endpoint(message_id, k2.runner.RUNNER_ENDPOINT)
