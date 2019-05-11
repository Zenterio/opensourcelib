from unittest import TestCase
from unittest.mock import Mock, patch

from zaf.messages.decorator import threadpool_dispatcher
from zaf.messages.dispatchers import ThreadPoolDispatcher

from ..decorator import CallbackDispatcher, ConcurrentDispatcher, DispatcherDecorator, \
    SequentialDispatcher, _validate_function_argument, callback_dispatcher, concurrent_dispatcher, \
    get_dispatcher_descriptors, sequential_dispatcher


class TestValidateFunctionArgument(TestCase):

    def test_does_not_raise_if_called_with_a_valid_argument(self):

        def my_function():
            pass

        _validate_function_argument(my_function)

    def test_raises_type_error_if_called_with_something_that_is_not_a_function(self):
        not_a_function = 'hello I am not a function'
        with self.assertRaisesRegex(TypeError, "The 'function' argument of .* must be callable."):
            _validate_function_argument(not_a_function)


class TestDispatcherDecorator(TestCase):

    def setUp(self):
        self._dispatcher_constructor = Mock()
        self._decorator = DispatcherDecorator(self._dispatcher_constructor)
        self._function = lambda message: message

    def test_calling_the_decorator_validates_function_arguments(self):
        with patch('zaf.messages.decorator._validate_function_argument') as p:
            self._apply_decorator()
            p.assert_called_once_with(self._function)

    def test_decorating_a_function_adds_a_zaf_dispatcher_descriptors(self):
        message_ids, endpoint_ids, entity_option_id = self._apply_decorator()

        self.assertEqual(len(self._function._zaf_dispatcher_descriptors), 1)

        dispatcher_descriptor = self._function._zaf_dispatcher_descriptors[0]
        self.assertIs(dispatcher_descriptor.dispatcher_constructor, self._dispatcher_constructor)
        self.assertIs(dispatcher_descriptor.message_ids, message_ids)
        self.assertIs(dispatcher_descriptor.endpoint_ids, endpoint_ids)
        self.assertIs(dispatcher_descriptor.entity_option_id, entity_option_id)

    def test_decorating_a_function_multiple_times_adds_multiple_zaf_dispatcher_descriptorss(self):
        message_ids_a, endpoint_ids_a, entity_option_id_a = self._apply_decorator()
        message_ids_b, endpoint_ids_b, entity_option_id_b = self._apply_decorator()

        self.assertEqual(len(self._function._zaf_dispatcher_descriptors), 2)

        dispatcher_descriptor_a = self._function._zaf_dispatcher_descriptors[0]
        self.assertIs(dispatcher_descriptor_a.dispatcher_constructor, self._dispatcher_constructor)
        self.assertIs(dispatcher_descriptor_a.message_ids, message_ids_a)
        self.assertIs(dispatcher_descriptor_a.endpoint_ids, endpoint_ids_a)
        self.assertIs(dispatcher_descriptor_a.entity_option_id, entity_option_id_a)

        dispatcher_descriptor_b = self._function._zaf_dispatcher_descriptors[1]
        self.assertIs(dispatcher_descriptor_b.dispatcher_constructor, self._dispatcher_constructor)
        self.assertIs(dispatcher_descriptor_b.message_ids, message_ids_b)
        self.assertIs(dispatcher_descriptor_b.endpoint_ids, endpoint_ids_b)
        self.assertIs(dispatcher_descriptor_b.entity_option_id, entity_option_id_b)

    def _apply_decorator(self):
        message_ids = object()
        endpoint_ids = object()
        entity_option_id = object()

        self._decorator(message_ids, endpoint_ids, entity_option_id)(self._function)

        return message_ids, endpoint_ids, entity_option_id


class TestSequentialDispatcher(TestCase):

    def test_provides_a_sequential_dispatcher_decorator(self):
        self.assertIsInstance(sequential_dispatcher, DispatcherDecorator)

    def test_decorate_a_member_function(self):

        class MyClass(object):

            @sequential_dispatcher(message_ids=None)
            def my_method(self):
                pass

        instance = MyClass()
        self.assertEqual(len(instance.my_method._zaf_dispatcher_descriptors), 1)
        dispatcher = instance.my_method._zaf_dispatcher_descriptors[0].dispatcher_constructor
        self.assertIs(dispatcher, SequentialDispatcher)


class TestCallbackDispatcher(TestCase):

    def test_provides_a_callback_dispatcher_decorator(self):
        assert isinstance(callback_dispatcher, DispatcherDecorator)

    def test_decorate_a_member_function(self):

        class MyClass(object):

            @callback_dispatcher(message_ids=None)
            def my_method(self):
                pass

        instance = MyClass()
        self.assertEqual(len(instance.my_method._zaf_dispatcher_descriptors), 1)
        dispatcher = instance.my_method._zaf_dispatcher_descriptors[0].dispatcher_constructor
        self.assertIs(dispatcher, CallbackDispatcher)


class TestConcurrentDecorator(TestCase):

    def test_provides_a_concurrent_dispatcher_decorator(self):
        self.assertIsInstance(concurrent_dispatcher, DispatcherDecorator)

    def test_decorate_a_member_function(self):

        class MyClass(object):

            @concurrent_dispatcher(message_ids=None)
            def my_method(self):
                pass

        instance = MyClass()
        self.assertEqual(len(instance.my_method._zaf_dispatcher_descriptors), 1)
        dispatcher = instance.my_method._zaf_dispatcher_descriptors[0].dispatcher_constructor
        self.assertIs(dispatcher, ConcurrentDispatcher)


class TestThreadPoolDecorator(TestCase):

    def test_provides_a_threadpool_dispatcher_decorator(self):
        self.assertIsInstance(threadpool_dispatcher, DispatcherDecorator)

    def test_decorate_a_member_function(self):

        class MyClass(object):

            @threadpool_dispatcher(message_ids=None, max_workers=3)
            def my_method(self):
                pass

        instance = MyClass()
        self.assertEqual(len(instance.my_method._zaf_dispatcher_descriptors), 1)
        dispatcher = instance.my_method._zaf_dispatcher_descriptors[0].dispatcher_constructor
        self.assertIs(dispatcher, ThreadPoolDispatcher)


class TestGetDispatcherDescriptors(TestCase):

    def test_no_dispatchers(self):

        class MyClass(object):
            pass

        self.assertEqual(get_dispatcher_descriptors(MyClass()), [])

    def test_single_dispatcher(self):

        class MyClass(object):

            @sequential_dispatcher(message_ids=None)
            def my_sequential_dispatcher(self):
                pass

        my_instance = MyClass()
        expected_dispatchers = zip(
            [my_instance.my_sequential_dispatcher],
            MyClass.my_sequential_dispatcher._zaf_dispatcher_descriptors)
        self.assertEqual(get_dispatcher_descriptors(my_instance), list(expected_dispatchers))

    def test_multiple_dispatchers(self):

        class MyClass(object):

            @sequential_dispatcher(message_ids=None)
            def my_sequential_dispatcher(self):
                pass

            @concurrent_dispatcher(message_ids=None)
            def my_concurrent_dispatcher(self):
                pass

        my_instance = MyClass()
        expected_dispatchers = zip(
            [my_instance.my_sequential_dispatcher, my_instance.my_concurrent_dispatcher],
            MyClass.my_sequential_dispatcher._zaf_dispatcher_descriptors +
            MyClass.my_concurrent_dispatcher._zaf_dispatcher_descriptors)
        self.assertEqual(set(get_dispatcher_descriptors(my_instance)), set(expected_dispatchers))

    def test_dispatcher_mixed_with_non_dispathcers(self):

        class MyClass(object):

            def my_non_dispatcher(self):
                pass

            @sequential_dispatcher(message_ids=None)
            def my_sequential_dispatcher(self):
                pass

        my_instance = MyClass()
        expected_dispatchers = zip(
            [
                my_instance.my_sequential_dispatcher,
            ], MyClass.my_sequential_dispatcher._zaf_dispatcher_descriptors)
        self.assertEqual(get_dispatcher_descriptors(my_instance), list(expected_dispatchers))
