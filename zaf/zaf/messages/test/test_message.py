import unittest

from ..message import Message
from .utils import defined_endpoint, defined_endpoint2, defined_message, defined_message2, entity, \
    entity2


class TestMessage(unittest.TestCase):

    def test_messages_are_equal_if_message_id_endpoint_entity_and_data_are_equal(self):
        self.assertEqual(
            Message(defined_message, defined_endpoint, entity, data={
                'k': 'v',
                'zaf': 'v2'
            }), Message(defined_message, defined_endpoint, entity, data={
                'k': 'v',
                'zaf': 'v2'
            }))

    def test_messages_are_not_equal_if_message_id_is_not_equal(self):
        self.assertNotEqual(
            Message(defined_message, defined_endpoint, data={
                'k': 'v',
                'zaf': 'v2'
            }), Message(defined_message2, defined_endpoint, data={
                'k': 'v',
                'zaf': 'v2'
            }))

    def test_messages_are_not_equal_if_entity_is_not_equal(self):
        self.assertNotEqual(
            Message(defined_message, defined_endpoint, entity, data={
                'k': 'v',
                'zaf': 'v2'
            }), Message(defined_message, defined_endpoint, entity2, data={
                'k': 'v',
                'zaf': 'v2'
            }))

    def test_messages_are_not_equal_if_endpoint_is_not_equal(self):
        self.assertNotEqual(
            Message(defined_message, defined_endpoint, data={
                'k': 'v',
                'zaf': 'v2'
            }), Message(defined_message, defined_endpoint2, data={
                'k': 'v',
                'zaf': 'v2'
            }))

    def test_messages_are_not_equal_if_data_is_not_equals(self):
        self.assertNotEqual(
            Message(defined_message, defined_endpoint, data={
                'k': 'v',
                'zaf': 'v2'
            }), Message(defined_message, defined_endpoint, data={
                'k': 'v',
                'zaf': 'v3'
            }))
