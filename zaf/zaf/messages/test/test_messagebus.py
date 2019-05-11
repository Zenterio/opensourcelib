import re
import unittest
from textwrap import dedent
from unittest.mock import Mock, call

from zaf.component.factory import Factory
from zaf.component.manager import ComponentManager

from ..message import EndpointId, Message, MessageId
from ..messagebus import DispatcherState, EndpointAlreadyDefined, EndpointState, MessageBus, \
    MessageBusTimeout, NoSuchDispatcher, NoSuchEndpoint, NoSuchMessage
from .utils import create_dispatcher, create_messagebus, data, defined_endpoint, \
    defined_endpoint2, defined_message, defined_message2, defined_message3, entity, entity2, \
    notdefined_endpoint, notdefined_message


class TestMessageAndEndpointDefinitions(unittest.TestCase):

    def setUp(self):
        self.messagebus = create_messagebus()

    def test_define_endpoint_succeeds(self):
        self.messagebus.define_endpoint(notdefined_endpoint)

    def test_define_endpoint_fails_is_endpoint_is_already_defined(self):
        self.assertRaises(EndpointAlreadyDefined, self.messagebus.define_endpoint, defined_endpoint)

    def test_define_message_fails_if_endpoint_is_not_defined(self):
        self.assertRaises(
            NoSuchEndpoint, self.messagebus.define_message, notdefined_message, notdefined_endpoint)

    def test_define_message_succeeds_if_endpoint_is_defined(self):
        self.messagebus.define_message(notdefined_message, defined_endpoint)

    def test_define_message_fails_if_endpoint_is_already_defined_for_message(self):
        self.assertRaises(
            EndpointAlreadyDefined, self.messagebus.define_message, defined_message,
            defined_endpoint)

    def test_get_message_with_endpoints(self):
        actual = self.messagebus.get_defined_messages_and_endpoints()
        self.assertEqual(
            actual, {
                defined_message: [defined_endpoint, defined_endpoint2],
                defined_message2: [defined_endpoint2],
                defined_message3: [defined_endpoint2]
            })

    def test_get_endpoints_with_messages(self):
        actual = self.messagebus.get_defined_endpoints_and_messages()
        self.assertEqual(
            actual, {
                defined_endpoint: [defined_message],
                defined_endpoint2: [defined_message, defined_message2, defined_message3],
            })


class TestMessageRegistration(unittest.TestCase):

    def setUp(self):
        self.messagebus = create_messagebus()

    def test_register_dispatcher_fails_if_message_is_not_defined(self):
        self.assertRaises(
            NoSuchMessage, self.messagebus.register_dispatcher, create_dispatcher(),
            [notdefined_message])

    def test_register_dispatcher_fails_if_endpoint_is_not_defined(self):
        self.assertRaises(
            NoSuchEndpoint, self.messagebus.register_dispatcher, create_dispatcher(),
            [defined_message], [notdefined_endpoint])

    def test_register_dispatcher_succeeds_if_message_is_defined(self):
        self.messagebus.register_dispatcher(create_dispatcher(), [defined_message])

    def test_register_dispatcher_succeeds_if_endpoint_is_defined(self):
        self.messagebus.register_dispatcher(
            create_dispatcher(), [defined_message], [defined_endpoint])

    def test_deregister_dispatcher_fails_if_message_is_not_defined(self):
        self.assertRaises(
            NoSuchMessage, self.messagebus.deregister_dispatcher, create_dispatcher(),
            [notdefined_message])

    def test_deregister_dispatcher_fails_if_dispatcher_is_not_registered(self):
        self.messagebus.register_dispatcher(create_dispatcher(), [defined_message])
        self.assertRaises(
            NoSuchDispatcher, self.messagebus.deregister_dispatcher, create_dispatcher(),
            [defined_message])

    def test_deregister_dispatcher_fails_if_message_ids_is_empty(self):
        self.messagebus.register_dispatcher(create_dispatcher(), [defined_message])
        self.assertRaises(
            ValueError, self.messagebus.deregister_dispatcher, create_dispatcher(), [])

    def test_deregister_part_of_registrations(self):
        dispatcher = create_dispatcher()
        self.messagebus.register_dispatcher(dispatcher, [defined_message, defined_message2])
        dispatcher_still_registered = self.messagebus.deregister_dispatcher(
            dispatcher, [defined_message])
        self.assertTrue(dispatcher_still_registered)
        self.assertTrue(
            self.messagebus.has_registered_dispatchers(defined_message2, defined_endpoint2))
        self.assertFalse(self.messagebus.deregister_dispatcher(dispatcher, [defined_message2]))

    def test_deregister_with_multiple_entities_specified(self):
        dispatcher = create_dispatcher()
        self.messagebus.register_dispatcher(
            dispatcher, [defined_message], [defined_endpoint], [entity, entity2])
        self.messagebus.deregister_dispatcher(
            dispatcher, [defined_message], [defined_endpoint], [entity])
        self.assertTrue(self.messagebus.dispatcher_is_registered(dispatcher))
        self.messagebus.deregister_dispatcher(
            dispatcher, [defined_message], [defined_endpoint], [entity2])
        self.assertFalse(self.messagebus.dispatcher_is_registered(dispatcher))

    def test_deregister_with_entity_specified(self):
        dispatcher = create_dispatcher()
        self.messagebus.register_dispatcher(
            dispatcher, [defined_message], [defined_endpoint], [entity])
        self.messagebus.deregister_dispatcher(
            dispatcher, [defined_message], [defined_endpoint], [entity])
        self.assertFalse(self.messagebus.dispatcher_is_registered(dispatcher))

    def test_deregister_with_no_entities_specified(self):
        dispatcher = create_dispatcher()
        self.messagebus.register_dispatcher(
            dispatcher, [defined_message], [defined_endpoint], [entity])
        self.messagebus.deregister_dispatcher(dispatcher, [defined_message], [defined_endpoint])
        self.assertFalse(self.messagebus.dispatcher_is_registered(dispatcher))


class TestMessageTriggering(unittest.TestCase):

    def setUp(self):
        self.messagebus = create_messagebus()

    def test_trigger_failed_message_id_is_not_defined(self):
        dispatcher = create_dispatcher()
        self.messagebus.register_dispatcher(dispatcher, [defined_message], [defined_endpoint])
        self.assertRaises(
            NoSuchMessage,
            self.messagebus.trigger_event,
            notdefined_message,
            defined_endpoint,
            data=data)

    def test_dispatcher_triggered_for_matching_endpoint(self):
        dispatcher = create_dispatcher()
        self.messagebus.register_dispatcher(dispatcher, [defined_message], [defined_endpoint])
        self.messagebus.trigger_event(defined_message, defined_endpoint, data=data)
        dispatcher.dispatch.assert_called_with(
            Message(defined_message, defined_endpoint, data=data))

    def test_dispatcher_triggered_in_order_by_priority(self):
        dispatcher1 = create_dispatcher(priority=3)
        dispatcher2 = create_dispatcher(priority=-4)
        dispatcher3 = create_dispatcher()

        manager = Mock()
        manager.attach_mock(dispatcher1, 'a')
        manager.attach_mock(dispatcher2, 'b')
        manager.attach_mock(dispatcher3, 'c')

        self.messagebus.register_dispatcher(dispatcher1, [defined_message])
        self.messagebus.register_dispatcher(dispatcher2, [defined_message])
        self.messagebus.register_dispatcher(dispatcher3, [defined_message])
        self.messagebus.trigger_event(defined_message, defined_endpoint, data=data)

        expected_message = Message(defined_message, defined_endpoint, data=data)
        expected_calls = [
            call.a.dispatch(expected_message),
            call.c.dispatch(expected_message),
            call.b.dispatch(expected_message),
        ]
        self.assertEqual(manager.mock_calls, expected_calls)

    def test_dispatcher_triggered_for_all_endpoints(self):
        dispatcher1 = create_dispatcher()
        dispatcher2 = create_dispatcher()

        self.messagebus.register_dispatcher(dispatcher1, [defined_message])
        self.messagebus.register_dispatcher(dispatcher2, [defined_message])
        self.messagebus.trigger_event(defined_message, defined_endpoint, data=data)

        expected_message = Message(defined_message, defined_endpoint, data=data)
        dispatcher1.dispatch.assert_called_with(expected_message)
        dispatcher2.dispatch.assert_called_with(expected_message)

    def test_dispatcher_not_triggered_for_non_matching_endpoint(self):
        dispatcher = create_dispatcher()
        self.messagebus.register_dispatcher(dispatcher, [defined_message], [defined_endpoint])
        self.messagebus.trigger_event(defined_message, defined_endpoint2, data=data)
        dispatcher.dispatch.assert_not_called()

    def test_dispatcher_not_triggered_for_deregistered_endpoint(self):
        dispatcher = create_dispatcher()
        dispatcher2 = create_dispatcher()
        self.messagebus.register_dispatcher(dispatcher, [defined_message], [defined_endpoint])
        self.messagebus.register_dispatcher(dispatcher2, [defined_message], [defined_endpoint2])
        self.messagebus.deregister_dispatcher(dispatcher2, [defined_message], [defined_endpoint2])
        self.messagebus.trigger_event(defined_message, defined_endpoint, data=data)
        self.messagebus.trigger_event(defined_message, defined_endpoint2, data=data)
        dispatcher.dispatch.assert_called_with(
            Message(defined_message, defined_endpoint, data=data))
        dispatcher2.dispatch.assert_not_called()

    def test_deregistered_dispatcher_not_triggered(self):
        dispatcher1 = create_dispatcher()
        dispatcher2 = create_dispatcher()

        self.messagebus.register_dispatcher(dispatcher1, [defined_message])
        self.messagebus.register_dispatcher(dispatcher2, [defined_message])
        self.messagebus.deregister_dispatcher(dispatcher2, [defined_message])
        self.messagebus.trigger_event(defined_message, defined_endpoint, data=data)

        dispatcher1.dispatch.assert_called_with(
            Message(defined_message, defined_endpoint, data=data))
        dispatcher2.dispatch.assert_not_called()

    def test_messagebus_is_active_true_if_dispatcher_has_active_count_1(self):
        dispatcher1 = create_dispatcher()
        dispatcher1.get_active_count = lambda: 1
        dispatcher1.get_queue_count = lambda: 0

        self.messagebus.register_dispatcher(dispatcher1, [defined_message])
        self.assertTrue(self.messagebus.is_active())

    def test_messagebus_is_active_false_if_dispatcher_has_active_count_0(self):
        dispatcher1 = create_dispatcher()
        dispatcher1.get_active_count = lambda: 0
        dispatcher1.get_queue_count = lambda: 0

        self.messagebus.register_dispatcher(dispatcher1, [defined_message])
        self.assertFalse(self.messagebus.is_active())

    def test_messagebus_is_active_can_take_endpoint(self):
        dispatcher1 = create_dispatcher()
        dispatcher1.get_active_count = lambda: 1
        dispatcher1.get_queue_count = lambda: 0
        dispatcher2 = create_dispatcher()
        dispatcher2.get_active_count = lambda: 0
        dispatcher2.get_queue_count = lambda: 0

        self.messagebus.register_dispatcher(dispatcher1, [defined_message], [defined_endpoint])
        self.messagebus.register_dispatcher(dispatcher2, [defined_message], [defined_endpoint2])

        self.assertTrue(self.messagebus.is_active(defined_endpoint))
        self.assertFalse(self.messagebus.is_active(defined_endpoint2))

    def test_messagebus_is_active_true_if_dispatcher_has_nonempty_queue(self):
        dispatcher1 = create_dispatcher()
        dispatcher1.get_active_count = lambda: 0
        dispatcher1.get_queue_count = lambda: 1

        self.messagebus.register_dispatcher(dispatcher1, [defined_message])
        self.assertTrue(self.messagebus.is_active())

    def test_messagebus_is_active_false_if_dispatcher_has_empty_queue(self):
        dispatcher1 = create_dispatcher()
        dispatcher1.get_active_count = lambda: 0
        dispatcher1.get_queue_count = lambda: 0

        self.messagebus.register_dispatcher(dispatcher1, [defined_message])
        self.assertFalse(self.messagebus.is_active())

    def test_messagebus_wait_waits_until_not_active(self):
        self.messagebus.is_active = Mock()
        self.messagebus.is_active.side_effect = [True, True, False]
        self.messagebus.wait_for_not_active()
        self.assertEqual(self.messagebus.is_active.call_count, 3)

    def test_messagebus_wait_throws_exception_on_timeout(self):
        self.messagebus.is_active = Mock()
        self.messagebus.is_active.side_effect = [True]

        dispatcher1 = create_dispatcher(log_repr='dispatcher1')
        dispatcher1.get_active_count = lambda: 3
        dispatcher1.get_queue_count = lambda: 4
        dispatcher2 = create_dispatcher(log_repr='dispatcher2')
        dispatcher2.get_active_count = lambda: 0
        dispatcher2.get_queue_count = lambda: 0
        self.messagebus.register_dispatcher(dispatcher1, [defined_message], [defined_endpoint])
        self.messagebus.register_dispatcher(dispatcher2, [defined_message], [defined_endpoint2])

        with self.assertRaisesRegex(MessageBusTimeout, re.escape(dedent("""\
                    Waiting for MessageBus activity to stop timed out:
                      defined_endpoint:
                        dispatcher1: queue_count=4, active_count=3"""))):
            self.messagebus.wait_for_not_active(timeout=0)

    def test_messagebus_get_state_returns_state_for_all_endpoints(self):
        dispatcher1 = create_dispatcher()
        dispatcher1.get_active_count = lambda: 3
        dispatcher1.get_queue_count = lambda: 4
        dispatcher2 = create_dispatcher()
        dispatcher2.get_active_count = lambda: 7
        dispatcher2.get_queue_count = lambda: 8
        self.messagebus.register_dispatcher(dispatcher1, [defined_message], [defined_endpoint])
        self.messagebus.register_dispatcher(dispatcher2, [defined_message], [defined_endpoint2])
        state = self.messagebus.get_state()
        self.assertEqual(len(state), 2)
        expected_state_endpoint1 = EndpointState(
            defined_endpoint, [DispatcherState(dispatcher1.log_repr(), 3, 4)])
        expected_state_endpoint2 = EndpointState(
            defined_endpoint2, [DispatcherState(dispatcher2.log_repr(), 7, 8)])
        self.assertIn(expected_state_endpoint1, state)
        self.assertIn(expected_state_endpoint2, state)

    def test_messagebus_get_state_returns_state_for_specified_endpoint(self):
        dispatcher1 = create_dispatcher()
        dispatcher1.get_active_count = lambda: 3
        dispatcher1.get_queue_count = lambda: 4
        dispatcher2 = create_dispatcher()
        dispatcher2.get_active_count = lambda: 7
        dispatcher2.get_queue_count = lambda: 8
        self.messagebus.register_dispatcher(dispatcher1, [defined_message], [defined_endpoint])
        self.messagebus.register_dispatcher(dispatcher1, [defined_message], [defined_endpoint2])
        state = self.messagebus.get_state(defined_endpoint)
        self.assertEqual(len(state), 1)
        expected_state_endpoint1 = EndpointState(
            defined_endpoint, [DispatcherState(dispatcher1.log_repr(), 3, 4)])
        expected_state_endpoint2 = EndpointState(
            defined_endpoint2, [DispatcherState(dispatcher2.log_repr(), 7, 8)])
        self.assertIn(expected_state_endpoint1, state)
        self.assertNotIn(expected_state_endpoint2, state)

    def test_messagebus_get_state_raises_exception_for_undefined_endpoint(self):
        with self.assertRaises(NoSuchEndpoint):
            self.messagebus.get_state(notdefined_endpoint)

    def test_messagebus_is_active_raises_exception_for_undefined_endpoint(self):
        with self.assertRaises(NoSuchEndpoint):
            self.messagebus.is_active(notdefined_endpoint)

    def test_messagebus_wait_for_not_active_raises_exception_for_undefined_endpoint(self):
        with self.assertRaises(NoSuchEndpoint):
            self.messagebus.wait_for_not_active(notdefined_endpoint)


class TestEntities(unittest.TestCase):

    def setUp(self):
        self.messagebus = create_messagebus()

    def test_register_dispatcher_for_entity(self):
        dispatcher = create_dispatcher()
        self.messagebus.register_dispatcher(
            dispatcher, [defined_message], [defined_endpoint], [entity])

    def test_dispatcher_registered_on_entity_not_triggered_by_message_from_endpoint(self):
        dispatcher = create_dispatcher()
        self.messagebus.register_dispatcher(
            dispatcher, [defined_message], [defined_endpoint], [entity])
        self.messagebus.trigger_event(defined_message, defined_endpoint, data=data)
        dispatcher.assert_not_called()

    def test_dispatcher_registered_for_entity_triggered_by_message_for_entity(self):
        dispatcher = create_dispatcher()
        self.messagebus.register_dispatcher(
            dispatcher, [defined_message], [defined_endpoint], [entity])
        self.messagebus.trigger_event(defined_message, defined_endpoint, entity, data=data)
        dispatcher.dispatch.assert_called_with(
            Message(defined_message, defined_endpoint, entity, data=data))

    def test_dispatcher_registered_for_endpoint_triggered_by_message_for_entity(self):
        dispatcher = create_dispatcher()
        self.messagebus.register_dispatcher(dispatcher, [defined_message], [defined_endpoint])
        self.messagebus.trigger_event(defined_message, defined_endpoint, entity, data=data)
        dispatcher.dispatch.assert_called_with(
            Message(defined_message, defined_endpoint, entity, data=data))

    def test_dispatcher_registered_for_entity_not_triggered_by_message_for_another_entity(self):
        dispatcher = create_dispatcher()
        self.messagebus.register_dispatcher(
            dispatcher, [defined_message], [defined_endpoint], [entity])
        self.messagebus.trigger_event(defined_message, defined_endpoint, entity2, data=data)
        dispatcher.assert_not_called()

    def test_dispatcher_registered_on_entity_triggered_by_request_to_endpoint(self):
        dispatcher = create_dispatcher()
        self.messagebus.register_dispatcher(
            dispatcher, [defined_message], [defined_endpoint], [entity])
        fs = self.messagebus.send_request(defined_message, defined_endpoint, data=data)
        dispatcher.dispatch.assert_called_with(
            Message(defined_message, defined_endpoint, entity, future=fs[0], data=data))

    def test_dispatcher_registered_for_entity_triggered_by_request_to_entity(self):
        dispatcher = create_dispatcher()
        self.messagebus.register_dispatcher(
            dispatcher, [defined_message], [defined_endpoint], [entity])
        fs = self.messagebus.send_request(defined_message, defined_endpoint, entity, data=data)
        dispatcher.dispatch.assert_called_with(
            Message(defined_message, defined_endpoint, entity, future=fs[0], data=data))

    def test_dispatcher_registered_for_endpoint_not_triggered_by_request_to_entity(self):
        dispatcher = create_dispatcher()
        self.messagebus.register_dispatcher(dispatcher, [defined_message], [defined_endpoint])
        self.messagebus.trigger_event(defined_message, defined_endpoint, entity, data=data)
        dispatcher.assert_not_called()

    def test_dispatcher_registered_for_entity_not_triggered_by_request_to_another_entity(self):
        dispatcher = create_dispatcher()
        self.messagebus.register_dispatcher(
            dispatcher, [defined_message], [defined_endpoint], [entity])
        self.messagebus.trigger_event(defined_message, defined_endpoint, entity2, data=data)
        dispatcher.assert_not_called()


class TestMultipleDispatcher(unittest.TestCase):

    def test_multiple_message_dispatchers_triggered_by_applicable_messages(self):
        messagebus = MessageBus(Factory(ComponentManager()))

        message_endpoint = EndpointId('message_endpoint', '')
        message_endpoint2 = EndpointId('message_endpoint2', '')
        message_endpoint_entity1 = 'endpoint_entity1'
        message_endpoint_entity2 = 'endpoint_entity2'

        sent_from_endpoint = MessageId('sent_from_endpoint', '')
        sent_from_entity1 = MessageId('sent_from_entity1', '')

        messagebus.define_endpoint(message_endpoint)
        messagebus.define_endpoint(message_endpoint2)
        messagebus.define_message(sent_from_endpoint, message_endpoint)
        messagebus.define_message(sent_from_entity1, message_endpoint)
        messagebus.define_message(sent_from_endpoint, message_endpoint2)
        messagebus.define_message(sent_from_entity1, message_endpoint2)

        received = {
            message_endpoint: [],
            message_endpoint2: [],
            message_endpoint_entity1: [],
            message_endpoint_entity2: []
        }

        def endpoint1(message):
            received[message_endpoint].append(message.message_id)

        messagebus.register_dispatcher(
            create_dispatcher(endpoint1), [sent_from_endpoint, sent_from_entity1],
            [message_endpoint])

        def endpoint2(message):
            received[message_endpoint2].append(message.message_id)

        messagebus.register_dispatcher(
            create_dispatcher(endpoint2), [sent_from_endpoint, sent_from_entity1],
            [message_endpoint2])

        def endpoint_entity1(message):
            received[message_endpoint_entity1].append(message.message_id)

        messagebus.register_dispatcher(
            create_dispatcher(endpoint_entity1), [sent_from_endpoint, sent_from_entity1],
            [message_endpoint], [message_endpoint_entity1])

        def endpoint_entity2(message):
            received[message_endpoint_entity2].append(message.message_id)

        messagebus.register_dispatcher(
            create_dispatcher(endpoint_entity2), [sent_from_endpoint, sent_from_entity1],
            [message_endpoint], [message_endpoint_entity2])

        messagebus.trigger_event(sent_from_endpoint, message_endpoint)
        messagebus.trigger_event(sent_from_entity1, message_endpoint, message_endpoint_entity1)

        self.assertEqual(received[message_endpoint], [sent_from_endpoint, sent_from_entity1])
        self.assertEqual(received[message_endpoint2], [])
        self.assertEqual(received[message_endpoint_entity1], [sent_from_entity1])
        self.assertEqual(received[message_endpoint_entity2], [])

    def test_multiple_request_dispatchers_triggered_by_applicable_requests(self):
        messagebus = MessageBus(Factory(ComponentManager()))

        request_target = EndpointId('request_target', '')
        request_target2 = EndpointId('request_target2', '')
        request_target_entity1 = 'target_entity1'
        request_target_entity2 = 'target_entity2'

        sent_to_all = MessageId('request_to_all', '')
        sent_to_target = MessageId('request_to_target', '')
        sent_to_entity1 = MessageId('request_to_entity1', '')

        messagebus.define_endpoint(request_target)
        messagebus.define_endpoint(request_target2)

        messagebus.define_message(sent_to_all, request_target)
        messagebus.define_message(sent_to_target, request_target)
        messagebus.define_message(sent_to_entity1, request_target)

        messagebus.define_message(sent_to_all, request_target2)
        messagebus.define_message(sent_to_target, request_target2)
        messagebus.define_message(sent_to_entity1, request_target2)

        received = {
            request_target: [],
            request_target2: [],
            request_target_entity1: [],
            request_target_entity2: []
        }

        def target1(message):
            received[request_target].append(message.message_id)

        messagebus.register_dispatcher(
            create_dispatcher(target1), [sent_to_all, sent_to_target, sent_to_entity1],
            [request_target])

        def target2(message):
            received[request_target2].append(message.message_id)

        messagebus.register_dispatcher(
            create_dispatcher(target2), [sent_to_all, sent_to_target, sent_to_entity1],
            [request_target2])

        def target_entity1(message):
            received[request_target_entity1].append(message.message_id)

        messagebus.register_dispatcher(
            create_dispatcher(target_entity1), [sent_to_all, sent_to_target, sent_to_entity1],
            [request_target], [request_target_entity1])

        def target_entity2(message):
            received[request_target_entity2].append(message.message_id)

        messagebus.register_dispatcher(
            create_dispatcher(target_entity2), [sent_to_all, sent_to_target, sent_to_entity1],
            [request_target], [request_target_entity2])

        messagebus.send_request(sent_to_all)
        messagebus.send_request(sent_to_target, request_target)
        messagebus.send_request(sent_to_entity1, request_target, request_target_entity1)

        self.assertEqual(received[request_target], [sent_to_all, sent_to_target])
        self.assertEqual(received[request_target2], [sent_to_all])
        self.assertEqual(
            received[request_target_entity1], [sent_to_all, sent_to_target, sent_to_entity1])
        self.assertEqual(received[request_target_entity2], [sent_to_all, sent_to_target])
