import unittest
from queue import Queue

from zaf.component.decorator import component, requires
from zaf.component.manager import ComponentManager
from zaf.messages.dispatchers import QueueUnblockedException

from ..dispatchers import CallbackDispatcher, ConcurrentDispatcher, LocalMessageQueue, \
    MessageFilter, SequentialDispatcher, ThreadPoolDispatcher
from .utils import create_messagebus, defined_endpoint, defined_endpoint2, defined_message, \
    defined_message2, defined_message3, notdefined_endpoint, notdefined_message


class TestSequentialDispatcher(unittest.TestCase):
    """
    Tests for SequentialDispatcher.

    Also covers testing the ThreadPoolDispatcher with limited number of threads.
    """

    def test_priority_is_passed_to_base_class(self):
        messagebus = create_messagebus()

        def handle_message(message):
            pass

        dispatcher = SequentialDispatcher(messagebus, handle_message, priority=-7)
        self.assertEqual(dispatcher.priority, -7)

    def test_destroy_can_be_called_on_a_dispatcher_that_is_not_registered(self):
        messagebus = create_messagebus()

        def handle_message(message):
            pass

        dispatcher = SequentialDispatcher(messagebus, handle_message)
        dispatcher.destroy()

    def test_dispatcher_can_be_registered_and_deregistered_in_messagebus(self):
        messagebus = create_messagebus()

        def handle_message(message):
            pass

        dispatcher = SequentialDispatcher(messagebus, handle_message)
        try:
            dispatcher.register([defined_message])
        finally:
            dispatcher.destroy()

    def test_register_raises_exception_when_called_with_empty_message_ids(self):
        messagebus = create_messagebus()

        def handle_message(message):
            pass

        dispatcher = SequentialDispatcher(messagebus, handle_message)
        self.assertRaises(Exception, dispatcher.register, [])

    def test_that_dispatcher_can_be_created_with_lambda(self):
        messagebus = create_messagebus()
        dispatcher = SequentialDispatcher(messagebus, lambda message: None)
        try:
            dispatcher.register([defined_message])
        finally:
            dispatcher.destroy()

    def test_dispatcher_can_be_started_and_stopped(self):
        messagebus = create_messagebus()

        def handle_message(message):
            pass

        dispatcher = SequentialDispatcher(messagebus, handle_message)
        dispatcher.start()
        self.assertIsNotNone(dispatcher._executor)
        dispatcher.stop(timeout=1)
        self.assertTrue(dispatcher._executor._shutdown)

    def test_message_triggers_handle_message(self):
        messagebus = create_messagebus()
        received_messages = Queue()

        def handle_message(message):
            received_messages.put(message)

        dispatcher = SequentialDispatcher(messagebus, handle_message)
        try:
            dispatcher.register(message_ids=[defined_message])
            messagebus.trigger_event(defined_message, defined_endpoint, data='data')
            self.assertEqual(received_messages.get(timeout=1).data, 'data')
        finally:
            dispatcher.destroy()

    def test_multiple_messages_triggers_handle_message(self):
        messagebus = create_messagebus()
        received_messages = Queue()

        def handle_message(message):
            received_messages.put(message)

        dispatcher = SequentialDispatcher(messagebus, handle_message)
        try:
            dispatcher.register(message_ids=[defined_message])
            messagebus.trigger_event(defined_message, defined_endpoint, data='data1')
            messagebus.trigger_event(defined_message, defined_endpoint, data='data2')
            self.assertIn(received_messages.get(timeout=1).data, 'data1')
            self.assertIn(received_messages.get(timeout=1).data, 'data2')
        finally:
            dispatcher.destroy()

    def test_multiple_messages_can_be_registered_separately(self):
        messagebus = create_messagebus()
        received_messages = Queue()

        def handle_message(message):
            received_messages.put(message)

        dispatcher = SequentialDispatcher(messagebus, handle_message)
        try:
            dispatcher.register(message_ids=[defined_message])
            dispatcher.register(message_ids=[defined_message2])
            messagebus.trigger_event(defined_message, defined_endpoint2, data='data1')
            messagebus.trigger_event(defined_message2, defined_endpoint2, data='data2')
            self.assertEqual(received_messages.get(timeout=1).data, 'data1')
            self.assertEqual(received_messages.get(timeout=1).data, 'data2')
        finally:
            dispatcher.destroy()

    def test_requests_trigger_handle_message(self):
        messagebus = create_messagebus()

        def handle_message(message):
            return message.data

        dispatcher = SequentialDispatcher(messagebus, handle_message)
        try:
            dispatcher.register([defined_message])
            fs = messagebus.send_request(defined_message, defined_endpoint, data='data')
            self.assertEqual(fs[0].result(timeout=1), 'data')
        finally:
            dispatcher.destroy()

    def test_multiple_requests_trigger_handle_message(self):
        messagebus = create_messagebus()

        def handle_message(message):
            return message.data

        dispatcher = SequentialDispatcher(messagebus, handle_message)
        try:
            dispatcher.register([defined_message])
            fs1 = messagebus.send_request(defined_message, defined_endpoint, data='data1')
            fs2 = messagebus.send_request(defined_message, defined_endpoint, data='data2')
            self.assertEqual(fs1[0].result(timeout=1), 'data1')
            self.assertEqual(fs2[0].result(timeout=1), 'data2')
        finally:
            dispatcher.destroy()

    def test_active_count_increased_during_message_handling(self):
        messagebus = create_messagebus()
        active_count = Queue()

        def handle_message(message):
            active_count.put(dispatcher.get_active_count())

        dispatcher = SequentialDispatcher(messagebus, handle_message)
        try:
            dispatcher.register(message_ids=[defined_message])
            self.assertEqual(dispatcher.get_active_count(), 0)
            messagebus.trigger_event(defined_message, defined_endpoint)
            self.assertEqual(active_count.get(timeout=1), 1)
            self.assertEqual(dispatcher.get_active_count(), 0)
        finally:
            dispatcher.destroy()

    def test_optional_dispatcher_is_not_registered_if_message_is_not_defined(self):
        messagebus = create_messagebus()
        active_count = Queue()

        def handle_message(message):
            active_count.put(dispatcher.get_active_count())

        try:
            dispatcher = SequentialDispatcher(messagebus, handle_message)
            dispatcher.register(message_ids=[notdefined_message], optional=True)
            self.assertEqual(dispatcher.get_active_count(), 0)
        finally:
            dispatcher.destroy()

    def test_optional_dispatcher_is_not_registered_if_endpoint_is_not_defined(self):
        messagebus = create_messagebus()
        active_count = Queue()

        def handle_message(message):
            active_count.put(dispatcher.get_active_count())

        try:
            dispatcher = SequentialDispatcher(messagebus, handle_message)
            dispatcher.register(
                message_ids=[defined_message], endpoint_ids=[notdefined_endpoint], optional=True)
            self.assertEqual(dispatcher.get_active_count(), 0)
        finally:
            dispatcher.destroy()

    def test_message_handler_raises_exception_on_triggered_event_does_not_destroy_dispatcher_thread(
            self):
        messagebus = create_messagebus()
        received = Queue()

        def handle_message(message):
            received.put(message.data)
            raise Exception('')

        try:
            dispatcher = SequentialDispatcher(messagebus, handle_message)
            dispatcher.register(message_ids=[defined_message], endpoint_ids=[defined_endpoint])

            messagebus.trigger_event(defined_message, defined_endpoint, data=1)
            self.assertIsNotNone(dispatcher._executor)
            messagebus.trigger_event(defined_message, defined_endpoint, data=2)
            self.assertIsNotNone(dispatcher._executor)
            self.assertEqual(received.get(timeout=1), 1)
            self.assertEqual(received.get(timeout=2), 2)

        finally:
            dispatcher.destroy()


class TestConcurrentDispatcher(unittest.TestCase):

    def test_priority_is_passed_to_base_class(self):
        messagebus = create_messagebus()

        def handle_message(message):
            pass

        dispatcher = ConcurrentDispatcher(messagebus, handle_message, priority=-7)
        self.assertEqual(dispatcher.priority, -7)

    def test_destroy_can_be_called_on_a_dispatcher_that_is_not_registered(self):
        messagebus = create_messagebus()

        def handle_message(message):
            pass

        dispatcher = ConcurrentDispatcher(messagebus, handle_message)
        dispatcher.destroy()

    def test_dispatcher_can_be_registered_and_deregistered_in_messagebus(self):
        messagebus = create_messagebus()

        def handle_message(message):
            pass

        dispatcher = ConcurrentDispatcher(messagebus, handle_message)
        try:
            dispatcher.register(message_ids=[defined_message])
        finally:
            dispatcher.destroy()

    def test_dispatcher_can_be_deregistered_in_multiple_calls(self):
        messagebus = create_messagebus()

        def handle_message(message):
            pass

        dispatcher = ConcurrentDispatcher(messagebus, handle_message)
        try:
            dispatcher.register(message_ids=[defined_message, defined_message2])
            dispatcher.deregister([defined_message])
            dispatcher.deregister([defined_message2])
        finally:
            dispatcher.destroy()

    def test_message_triggers_handle_message(self):
        messagebus = create_messagebus()
        received_messages = Queue()

        def handle_message(message):
            received_messages.put(message)

        dispatcher = ConcurrentDispatcher(messagebus, handle_message)
        try:
            dispatcher.register([defined_message])
            messagebus.trigger_event(defined_message, defined_endpoint, data='data1')
            self.assertEqual(received_messages.get(timeout=1).data, 'data1')
        finally:
            dispatcher.destroy()

    def test_multiple_messages_triggers_handle_message(self):
        messagebus = create_messagebus()
        received_messages = Queue()

        def handle_message(message):
            received_messages.put(message)

        dispatcher = ConcurrentDispatcher(messagebus, handle_message)
        try:
            dispatcher.register([defined_message])
            messagebus.trigger_event(defined_message, defined_endpoint, data='data1')
            messagebus.trigger_event(defined_message, defined_endpoint, data='data2')
            self.assertIn(received_messages.get(timeout=1).data, ['data1', 'data2'])
            self.assertIn(received_messages.get(timeout=1).data, ['data1', 'data2'])
        finally:
            dispatcher.destroy()

    def test_concurrent_dispatcher_is_triggered_asynchronously(self):
        messagebus = create_messagebus()

        queue1 = Queue()
        queue2 = Queue()
        completed_queue = Queue()

        def handle_message(message):
            (put_queue, get_queue, value) = message.data
            put_queue.put(value)
            completed_queue.put(get_queue.get(timeout=1))

        dispatcher = ConcurrentDispatcher(messagebus, handle_message)
        try:
            dispatcher.register([defined_message])
            messagebus.trigger_event(defined_message, defined_endpoint, data=(queue1, queue2, '1'))
            messagebus.trigger_event(defined_message, defined_endpoint, data=(queue2, queue1, '2'))

            results = set()
            results.add(completed_queue.get(timeout=1))
            results.add(completed_queue.get(timeout=2))

            self.assertEqual(results, {'1', '2'})
        finally:
            dispatcher.destroy()

    def test_requests_trigger_handle_message(self):
        messagebus = create_messagebus()

        def handle_message(message):
            return message.data

        dispatcher = ConcurrentDispatcher(messagebus, handle_message)
        try:
            dispatcher.register([defined_message])
            fs = messagebus.send_request(defined_message, defined_endpoint, data='data')
            self.assertEqual(fs[0].result(timeout=1), 'data')
        finally:
            dispatcher.destroy()

    def test_multiple_requests_trigger_handle_message(self):
        messagebus = create_messagebus()

        def handle_message(message):
            return message.data

        dispatcher = ConcurrentDispatcher(messagebus, handle_message)
        try:
            dispatcher.register([defined_message])
            fs1 = messagebus.send_request(defined_message, defined_endpoint, data='data1')
            fs2 = messagebus.send_request(defined_message, defined_endpoint, data='data2')
            self.assertEqual(fs1[0].result(timeout=1), 'data1')
            self.assertEqual(fs2[0].result(timeout=1), 'data2')
        finally:
            dispatcher.destroy()

    def test_concurrent_dispatcher_requests_are_triggered_asynchronously(self):
        messagebus = create_messagebus()

        queue1 = Queue()
        queue2 = Queue()
        completed_queue = Queue()

        def handle_message(message):
            (put_queue, get_queue, value) = message.data
            put_queue.put(value)
            completed_queue.put(get_queue.get(timeout=1))
            return value

        dispatcher = ConcurrentDispatcher(messagebus, handle_message)
        try:
            dispatcher.register([defined_message])
            futures1 = messagebus.send_request(
                defined_message, defined_endpoint, data=(queue1, queue2, '1'))
            futures2 = messagebus.send_request(
                defined_message, defined_endpoint, data=(queue2, queue1, '2'))

            results = set()
            results.add(completed_queue.get(timeout=1))
            results.add(completed_queue.get(timeout=2))

            self.assertEqual(results, {'1', '2'})
            self.assertEqual(futures1[0].result(timeout=1), '1')
            self.assertEqual(futures2[0].result(timeout=1), '2')
        finally:
            dispatcher.destroy()

    def test_active_count_increased_during_message_handling(self):
        messagebus = create_messagebus()
        active_count = Queue()
        thread1_done = Queue()
        thread2_done = Queue()

        def handle_message(message):
            (put_queue, get_queue) = message.data
            active_count.put(dispatcher.get_active_count())
            put_queue.put(True)
            get_queue.get(timeout=1)

        dispatcher = ConcurrentDispatcher(messagebus, handle_message)
        try:
            dispatcher.register(message_ids=[defined_message])
            self.assertEqual(dispatcher.get_active_count(), 0)
            futures1 = messagebus.send_request(
                defined_message, defined_endpoint, data=(thread1_done, thread2_done))
            self.assertEqual(active_count.get(timeout=1), 1)
            futures2 = messagebus.send_request(
                defined_message, defined_endpoint, data=(thread2_done, thread1_done))
            self.assertEqual(active_count.get(timeout=1), 2)

            futures1.wait(timeout=1)[0].result(timeout=1)
            futures2.wait(timeout=1)[0].result(timeout=1)
            self.assertEqual(dispatcher.get_active_count(), 0)
        finally:
            dispatcher.destroy()

    def test_optional_dispatcher_is_not_registered_if_message_is_not_defined(self):
        messagebus = create_messagebus()
        active_count = Queue()

        def handle_message(message):
            active_count.put(dispatcher.get_active_count())

        try:
            dispatcher = ConcurrentDispatcher(messagebus, handle_message)
            dispatcher.register(message_ids=[notdefined_message], optional=True)
            self.assertEqual(dispatcher.get_active_count(), 0)
        finally:
            dispatcher.destroy()

    def test_optional_dispatcher_is_not_registered_if_endpoint_is_not_defined(self):
        messagebus = create_messagebus()
        active_count = Queue()

        def handle_message(message):
            active_count.put(dispatcher.get_active_count())

        try:
            dispatcher = ConcurrentDispatcher(messagebus, handle_message)
            dispatcher.register(
                message_ids=[defined_message], endpoint_ids=[notdefined_endpoint], optional=True)
            self.assertEqual(dispatcher.get_active_count(), 0)
        finally:
            dispatcher.destroy()


class TestCallbackDispatcher(unittest.TestCase):

    def test_priority_is_passed_to_base_class(self):
        messagebus = create_messagebus()

        def handle_message(message):
            pass

        dispatcher = CallbackDispatcher(messagebus, handle_message, priority=-7)
        self.assertEqual(dispatcher.priority, -7)

    def test_destroy_can_be_called_on_a_dispatcher_that_is_not_registered(self):
        messagebus = create_messagebus()

        def handle_message(message):
            pass

        dispatcher = CallbackDispatcher(messagebus, handle_message)
        dispatcher.destroy()

    def test_callback_can_be_registered_and_deregistered(self):
        messagebus = create_messagebus()

        def handle_message(message):
            pass

        dispatcher = CallbackDispatcher(messagebus, handle_message)
        try:
            dispatcher.register(message_ids=[defined_message])
        finally:
            dispatcher.destroy()

    def test_message_triggers_handle_message(self):
        messagebus = create_messagebus()
        received_messages = Queue()

        def handle_message(message):
            received_messages.put(message)

        dispatcher = CallbackDispatcher(messagebus, handle_message)
        try:
            dispatcher.register(message_ids=[defined_message])
            messagebus.trigger_event(defined_message, defined_endpoint, data='data')
            self.assertEqual(received_messages.get(timeout=1).data, 'data')
        finally:
            dispatcher.destroy()

    def test_requests_trigger_handle_message(self):
        messagebus = create_messagebus()

        def handle_message(message):
            return message.data

        dispatcher = CallbackDispatcher(messagebus, handle_message)
        try:
            dispatcher.register([defined_message])
            fs = messagebus.send_request(defined_message, defined_endpoint, data='data')
            self.assertEqual(fs[0].result(timeout=1), 'data')
        finally:
            dispatcher.destroy()

    def test_active_count_increased_during_message_handling(self):
        messagebus = create_messagebus()
        active_count = Queue()

        def handle_message(message):
            active_count.put(dispatcher.get_active_count())

        dispatcher = CallbackDispatcher(messagebus, handle_message)
        try:
            dispatcher.register(message_ids=[defined_message])
            self.assertEqual(dispatcher.get_active_count(), 0)
            messagebus.trigger_event(defined_message, defined_endpoint)
            self.assertEqual(active_count.get(timeout=1), 1)
            self.assertEqual(dispatcher.get_active_count(), 0)
        finally:
            dispatcher.destroy()

    def test_optional_dispatcher_is_not_registered_if_message_is_not_defined(self):
        messagebus = create_messagebus()
        active_count = Queue()

        def handle_message(message):
            active_count.put(dispatcher.get_active_count())

        try:
            dispatcher = CallbackDispatcher(messagebus, handle_message)
            dispatcher.register(message_ids=[notdefined_message], optional=True)
            self.assertEqual(dispatcher.get_active_count(), 0)
        finally:
            dispatcher.destroy()

    def test_optional_dispatcher_is_not_registered_if_endpoint_is_not_defined(self):
        messagebus = create_messagebus()
        active_count = Queue()

        def handle_message(message):
            active_count.put(dispatcher.get_active_count())

        try:
            dispatcher = CallbackDispatcher(messagebus, handle_message)
            dispatcher.register(
                message_ids=[defined_message], endpoint_ids=[notdefined_endpoint], optional=True)
            self.assertEqual(dispatcher.get_active_count(), 0)
        finally:
            dispatcher.destroy()


class TestDispatcherOnMethod(unittest.TestCase):

    def setUp(self):
        self._received_messages = Queue()

    def handle_message(self, message):
        self._received_messages.put(message)

    def test_method_can_be_registered_with_self_as_instance(self):
        messagebus = create_messagebus()
        dispatcher = ConcurrentDispatcher(messagebus, self.handle_message)
        try:
            dispatcher.register([defined_message])
            messagebus.trigger_event(defined_message, defined_endpoint, data='data')
            self.assertEqual(self._received_messages.get(timeout=1).data, 'data')
        finally:
            dispatcher.destroy()


class TestLocalMessageQueue(unittest.TestCase):

    def test_messages_added_after_dispatcher_is_registered_are_available(self):
        messagebus = create_messagebus()

        with LocalMessageQueue(messagebus, [defined_message]) as local_queue:
            messagebus.trigger_event(defined_message, defined_endpoint, data='data')
            message = local_queue.get(timeout=1)
            self.assertEqual(message.data, 'data')

    def test_messages_added_before_dispatcher_is_registered_are_not_available(self):
        messagebus = create_messagebus()
        messagebus.trigger_event(defined_message2, defined_endpoint, data='data')

        with LocalMessageQueue(messagebus, [defined_message, defined_message2]) as local_queue:
            messagebus.trigger_event(defined_message, defined_endpoint, data='data2')
            message = local_queue.get(timeout=1)
            self.assertEqual(message.data, 'data2')

    def test_messages_available_in_order_they_were_added(self):
        messagebus = create_messagebus()

        with LocalMessageQueue(
                messagebus, [defined_message, defined_message2, defined_message3]) as local_queue:
            messagebus.trigger_event(defined_message, defined_endpoint, data='data1')
            messagebus.trigger_event(defined_message2, defined_endpoint2, data='data2')
            messagebus.trigger_event(defined_message3, defined_endpoint2, data='data3')

            message1 = local_queue.get(timeout=1)
            self.assertEqual(message1.data, 'data1')

            message2 = local_queue.get(timeout=1)
            self.assertEqual(message2.data, 'data2')

            message3 = local_queue.get(timeout=1)
            self.assertEqual(message3.data, 'data3')

    def test_messages_added_only_when_matches(self):
        messagebus = create_messagebus()

        def match(message):
            return message.data == 'data2'

        with LocalMessageQueue(messagebus, [defined_message, defined_message2],
                               match=match) as local_queue:
            messagebus.trigger_event(defined_message, defined_endpoint, data='data')
            messagebus.trigger_event(defined_message, defined_endpoint, data='data2')
            message = local_queue.get(timeout=1)
            self.assertEqual(message.data, 'data2')

    def test_empty_returns_true_if_the_queue_is_empty(self):
        messagebus = create_messagebus()

        with LocalMessageQueue(messagebus, [defined_message]) as local_queue:
            self.assertTrue(local_queue.empty())

    def test_empty_returns_false_if_the_queue_is_not_empty(self):
        messagebus = create_messagebus()
        with LocalMessageQueue(messagebus, [defined_message]) as local_queue:

            messagebus.trigger_event(defined_message, defined_endpoint, data='data')
            self.assertFalse(local_queue.empty())

    def test_queue_get_can_be_unblocked_from_another_thread(self):
        messagebus = create_messagebus()
        with LocalMessageQueue(messagebus, [defined_message]) as local_queue:
            with self.assertRaises(QueueUnblockedException):
                local_queue.unblock()
                local_queue.get(timeout=1)


class TestMessageFilter(unittest.TestCase):

    def test_filter_can_be_applied_to_dispatcher(self):
        messagebus = create_messagebus()
        received_messages = Queue()

        def match(message):
            return message.data == 'data2'

        @MessageFilter(match)
        def handle_message(message):
            received_messages.put(message)

        dispatcher = SequentialDispatcher(messagebus, handle_message)
        try:
            dispatcher.register([defined_message])
            messagebus.trigger_event(defined_message, defined_endpoint, data='data1')
            messagebus.trigger_event(defined_message, defined_endpoint, data='data2')
            self.assertEqual(received_messages.get(timeout=1).data, 'data2')
        finally:
            dispatcher.destroy()


class TestComponentsOnHandlers(unittest.TestCase):

    def load_components(self):

        @component(scope='message')
        class MessageScoped(object):

            def __init__(self):
                self.calls = 0

            def __call__(self, *args, **kwargs):
                self.calls += 1
                return self.calls

        @component(scope='dispatcher')
        class DispatcherScoped(object):

            def __init__(self):
                self.calls = 0

            def __call__(self, *args, **kwargs):
                self.calls += 1
                return self.calls

        @component(scope='session')
        class SessionScoped(object):

            def __init__(self):
                self.calls = 0

            def __call__(self, *args, **kwargs):
                self.calls += 1
                return self.calls

    def setUp(self):
        self.component_manager = ComponentManager()
        self.component_manager.clear_component_registry()
        self.load_components()

    def test_sequential_dispatcher_requires_component(self):
        messagebus = create_messagebus()
        comp_counts = Queue()

        @requires(comp='MessageScoped')
        def handle_message(message, comp):
            comp_counts.put(comp())

        dispatcher = SequentialDispatcher(messagebus, handle_message)
        try:
            dispatcher.register([defined_message])
            messagebus.trigger_event(defined_message, defined_endpoint, data='data1')
            self.assertEqual(comp_counts.get(timeout=1), 1)
        finally:
            dispatcher.destroy()

    def test_concurrent_dispatcher_requires_component(self):
        messagebus = create_messagebus()
        comp_counts = Queue()

        @requires(comp='MessageScoped')
        def handle_message(message, comp):
            comp_counts.put(comp())

        dispatcher = ConcurrentDispatcher(messagebus, handle_message)
        try:
            dispatcher.register([defined_message])
            messagebus.trigger_event(defined_message, defined_endpoint, data='data1')
            self.assertEqual(comp_counts.get(timeout=1), 1)
        finally:
            dispatcher.destroy()

    def test_callback_dispatcher_requires_component(self):
        messagebus = create_messagebus()
        comp_counts = Queue()

        @requires(comp='MessageScoped')
        def handle_message(message, comp):
            comp_counts.put(comp())

        dispatcher = CallbackDispatcher(messagebus, handle_message)
        try:
            dispatcher.register([defined_message])
            messagebus.trigger_event(defined_message, defined_endpoint, data='data1')
            self.assertEqual(comp_counts.get(timeout=1), 1)
        finally:
            dispatcher.destroy()

    def test_multiple_calls_give_different_message_scoped_components(self):
        messagebus = create_messagebus()
        comp_counts = Queue()

        @requires(comp='MessageScoped')
        def handle_message(message, comp):
            comp_counts.put(comp())

        dispatcher = CallbackDispatcher(messagebus, handle_message)
        try:
            dispatcher.register([defined_message])
            messagebus.trigger_event(defined_message, defined_endpoint, data='data1')
            messagebus.trigger_event(defined_message, defined_endpoint, data='data2')
            self.assertEqual(comp_counts.get(timeout=1), 1)
            self.assertEqual(comp_counts.get(timeout=1), 1)
        finally:
            dispatcher.destroy()

    def test_multiple_calls_give_same_dispatcher_scoped_component(self):
        messagebus = create_messagebus()
        comp_counts_a = Queue()
        comp_counts_b = Queue()

        @requires(comp='DispatcherScoped')
        def handle_message_a(message, comp):
            comp_counts_a.put(comp())

        @requires(comp='DispatcherScoped')
        def handle_message_b(message, comp):
            comp_counts_b.put(comp())

        dispatcher_a = CallbackDispatcher(messagebus, handle_message_a)
        dispatcher_b = CallbackDispatcher(messagebus, handle_message_b)
        try:
            try:
                dispatcher_a.register([defined_message])
                dispatcher_b.register([defined_message])
                messagebus.trigger_event(defined_message, defined_endpoint, data='data1')
                messagebus.trigger_event(defined_message, defined_endpoint, data='data2')
                self.assertEqual(comp_counts_a.get(timeout=1), 1)
                self.assertEqual(comp_counts_a.get(timeout=1), 2)
                self.assertEqual(comp_counts_b.get(timeout=1), 1)
                self.assertEqual(comp_counts_b.get(timeout=1), 2)
            finally:
                dispatcher_a.destroy()
                messagebus.trigger_event(defined_message, defined_endpoint, data='data2')
                assert comp_counts_a.empty()
                self.assertEqual(comp_counts_b.get(timeout=1), 3)
        finally:
            dispatcher_b.destroy()

    def test_multiple_calls_give_same_session_scoped_component(self):
        messagebus = create_messagebus()
        comp_counts = Queue()

        @requires(comp='SessionScoped')
        def handle_message(message, comp):
            comp_counts.put(comp())

        dispatcher = CallbackDispatcher(messagebus, handle_message)
        try:
            dispatcher.register([defined_message])
            messagebus.trigger_event(defined_message, defined_endpoint, data='data1')
            messagebus.trigger_event(defined_message, defined_endpoint, data='data2')
            self.assertEqual(comp_counts.get(timeout=1), 1)
            self.assertEqual(comp_counts.get(timeout=1), 2)
        finally:
            dispatcher.destroy()

    def test_message_entity_is_used_to_fixate_entities(self):
        messagebus = create_messagebus()
        calls = Queue()

        @component(name='A')
        class a1():
            entity = 'a1'

        @component(name='A')
        class a2():
            entity = 'a2'

        @requires(a='A')
        def handle_message(message, a):
            calls.put(a.entity)

        dispatcher = CallbackDispatcher(messagebus, handle_message)
        try:
            dispatcher.register([defined_message], entities=['a1', 'a2'])
            messagebus.trigger_event(defined_message, defined_endpoint, entity='a2', data='data1')
            self.assertEqual(calls.get(timeout=1), 'a2')
            messagebus.trigger_event(defined_message, defined_endpoint, entity='a1', data='data2')
            self.assertEqual(calls.get(timeout=1), 'a1')
        finally:
            dispatcher.destroy()

    def test_combination_of_fixated_and_not_fixated_entities(self):
        messagebus = create_messagebus()
        calls = Queue()

        @component(name='A')
        class a1():
            entity = 'a1'

        @component(name='A', can=['2'])
        class a2():
            entity = 'a2'

        @requires(a='A')
        @requires(a2='A', can=['2'], fixate_entities=False)
        def handle_message(message, a, a2):
            calls.put(a.entity)
            calls.put(a2.entity)

        dispatcher = CallbackDispatcher(messagebus, handle_message)
        try:
            dispatcher.register([defined_message], entities=['a1', 'a2'])
            messagebus.trigger_event(defined_message, defined_endpoint, entity='a2', data='data1')
            self.assertEqual(calls.get(timeout=1), 'a2')
            self.assertEqual(calls.get(timeout=1), 'a2')
            messagebus.trigger_event(defined_message, defined_endpoint, entity='a1', data='data2')
            self.assertEqual(calls.get(timeout=1), 'a1')
            self.assertEqual(calls.get(timeout=1), 'a2')
        finally:
            dispatcher.destroy()


class TestThreadPoolDispatcherWithMultipleWorkers(unittest.TestCase):

    def test_priority_is_passed_to_base_class(self):
        messagebus = create_messagebus()

        def handle_message(message):
            pass

        dispatcher = ThreadPoolDispatcher(messagebus, handle_message, priority=-7)
        self.assertEqual(dispatcher.priority, -7)

    def test_destroy_can_be_called_on_a_dispatcher_that_is_not_registered(self):
        messagebus = create_messagebus()

        def handle_message(message):
            pass

        dispatcher = ThreadPoolDispatcher(messagebus, handle_message)
        dispatcher.destroy()

    def test_dispatcher_can_be_registered_and_deregistered_in_messagebus(self):
        messagebus = create_messagebus()

        def handle_message(message):
            pass

        dispatcher = ThreadPoolDispatcher(messagebus, handle_message)
        try:
            dispatcher.register(message_ids=[defined_message])
        finally:
            dispatcher.destroy()

    def test_dispatcher_can_be_deregistered_in_multiple_calls(self):
        messagebus = create_messagebus()

        def handle_message(message):
            pass

        dispatcher = ThreadPoolDispatcher(messagebus, handle_message)
        try:
            dispatcher.register(message_ids=[defined_message, defined_message2])
            dispatcher.deregister([defined_message])
            dispatcher.deregister([defined_message2])
        finally:
            dispatcher.destroy()

    def test_message_triggers_handle_message(self):
        messagebus = create_messagebus()
        received_messages = Queue()

        def handle_message(message):
            received_messages.put(message)

        dispatcher = ThreadPoolDispatcher(messagebus, handle_message)
        try:
            dispatcher.register([defined_message])
            messagebus.trigger_event(defined_message, defined_endpoint, data='data1')
            self.assertEqual(received_messages.get(timeout=1).data, 'data1')
        finally:
            dispatcher.destroy()

    def test_multiple_messages_triggers_handle_message(self):
        messagebus = create_messagebus()
        received_messages = Queue()

        def handle_message(message):
            received_messages.put(message)

        dispatcher = ThreadPoolDispatcher(messagebus, handle_message)
        try:
            dispatcher.register([defined_message])
            messagebus.trigger_event(defined_message, defined_endpoint, data='data1')
            messagebus.trigger_event(defined_message, defined_endpoint, data='data2')
            self.assertIn(received_messages.get(timeout=1).data, ['data1', 'data2'])
            self.assertIn(received_messages.get(timeout=1).data, ['data1', 'data2'])
        finally:
            dispatcher.destroy()

    def test_concurrent_dispatcher_is_triggered_asynchronously(self):
        messagebus = create_messagebus()

        queue1 = Queue()
        queue2 = Queue()
        completed_queue = Queue()

        def handle_message(message):
            (put_queue, get_queue, value) = message.data
            put_queue.put(value)
            completed_queue.put(get_queue.get(timeout=1))

        dispatcher = ThreadPoolDispatcher(messagebus, handle_message)
        try:
            dispatcher.register([defined_message])
            messagebus.trigger_event(defined_message, defined_endpoint, data=(queue1, queue2, '1'))
            messagebus.trigger_event(defined_message, defined_endpoint, data=(queue2, queue1, '2'))

            results = set()
            results.add(completed_queue.get(timeout=1))
            results.add(completed_queue.get(timeout=2))

            self.assertEqual(results, {'1', '2'})
        finally:
            dispatcher.destroy()

    def test_requests_trigger_handle_message(self):
        messagebus = create_messagebus()

        def handle_message(message):
            return message.data

        dispatcher = ThreadPoolDispatcher(messagebus, handle_message)
        try:
            dispatcher.register([defined_message])
            fs = messagebus.send_request(defined_message, defined_endpoint, data='data')
            self.assertEqual(fs[0].result(timeout=1), 'data')
        finally:
            dispatcher.destroy()

    def test_multiple_requests_trigger_handle_message(self):
        messagebus = create_messagebus()

        def handle_message(message):
            return message.data

        dispatcher = ThreadPoolDispatcher(messagebus, handle_message)
        try:
            dispatcher.register([defined_message])
            fs1 = messagebus.send_request(defined_message, defined_endpoint, data='data1')
            fs2 = messagebus.send_request(defined_message, defined_endpoint, data='data2')
            self.assertEqual(fs1[0].result(timeout=1), 'data1')
            self.assertEqual(fs2[0].result(timeout=1), 'data2')
        finally:
            dispatcher.destroy()

    def test_concurrent_dispatcher_requests_are_triggered_asynchronously(self):
        messagebus = create_messagebus()

        queue1 = Queue()
        queue2 = Queue()
        completed_queue = Queue()

        def handle_message(message):
            (put_queue, get_queue, value) = message.data
            put_queue.put(value)
            completed_queue.put(get_queue.get(timeout=1))
            return value

        dispatcher = ThreadPoolDispatcher(messagebus, handle_message)
        try:
            dispatcher.register([defined_message])
            futures1 = messagebus.send_request(
                defined_message, defined_endpoint, data=(queue1, queue2, '1'))
            futures2 = messagebus.send_request(
                defined_message, defined_endpoint, data=(queue2, queue1, '2'))

            results = set()
            results.add(completed_queue.get(timeout=1))
            results.add(completed_queue.get(timeout=2))

            self.assertEqual(results, {'1', '2'})
            self.assertEqual(futures1[0].result(timeout=1), '1')
            self.assertEqual(futures2[0].result(timeout=1), '2')
        finally:
            dispatcher.destroy()

    def test_active_count_increased_during_message_handling(self):
        messagebus = create_messagebus()
        active_count = Queue()
        thread1_done = Queue()
        thread2_done = Queue()

        def handle_message(message):
            (put_queue, get_queue) = message.data
            active_count.put(dispatcher.get_active_count())
            put_queue.put(True)
            get_queue.get(timeout=1)

        dispatcher = ThreadPoolDispatcher(messagebus, handle_message)
        try:
            dispatcher.register(message_ids=[defined_message])
            self.assertEqual(dispatcher.get_active_count(), 0)
            futures1 = messagebus.send_request(
                defined_message, defined_endpoint, data=(thread1_done, thread2_done))
            self.assertEqual(active_count.get(timeout=1), 1)
            futures2 = messagebus.send_request(
                defined_message, defined_endpoint, data=(thread2_done, thread1_done))
            self.assertEqual(active_count.get(timeout=1), 2)

            futures1.wait(timeout=1)[0].result(timeout=1)
            futures2.wait(timeout=1)[0].result(timeout=1)
            self.assertEqual(dispatcher.get_active_count(), 0)
        finally:
            dispatcher.destroy()

    def test_optional_dispatcher_is_not_registered_if_message_is_not_defined(self):
        messagebus = create_messagebus()
        active_count = Queue()

        def handle_message(message):
            active_count.put(dispatcher.get_active_count())

        try:
            dispatcher = ThreadPoolDispatcher(messagebus, handle_message)
            dispatcher.register(message_ids=[notdefined_message], optional=True)
            self.assertEqual(dispatcher.get_active_count(), 0)
        finally:
            dispatcher.destroy()

    def test_optional_dispatcher_is_not_registered_if_endpoint_is_not_defined(self):
        messagebus = create_messagebus()
        active_count = Queue()

        def handle_message(message):
            active_count.put(dispatcher.get_active_count())

        try:
            dispatcher = ThreadPoolDispatcher(messagebus, handle_message)
            dispatcher.register(
                message_ids=[defined_message], endpoint_ids=[notdefined_endpoint], optional=True)
            self.assertEqual(dispatcher.get_active_count(), 0)
        finally:
            dispatcher.destroy()
