import tempfile
import unittest
from queue import Queue
from unittest.mock import MagicMock, Mock, call, patch

from zaf.commands.command import CommandId
from zaf.config.options import ConfigOption, ConfigOptionId
from zaf.extensions.extension import CommandExtension
from zaf.extensions.manager import InvalidDispatcherEntityError
from zaf.messages.decorator import callback_dispatcher, concurrent_dispatcher, \
    sequential_dispatcher, threadpool_dispatcher
from zaf.messages.dispatchers import CallbackDispatcher, ConcurrentDispatcher, \
    SequentialDispatcher, ThreadPoolDispatcher
from zaf.messages.message import EndpointId, MessageId
from zaf.utils.object import TypeComparator

from ..extension import AbstractExtension, ExtensionType, FrameworkExtension
from ..manager import ExtensionManager, _find_extensions_by_inspection
from .addons.testcommandaddon import TESTCOMMANDADDON_COMMAND


class TestFindExtensionsByInspection(unittest.TestCase):

    class ContainsConcreteExtension(object):

        class MyConcreteExtensionMock(object):
            _is_zaf_extension = True

    class ContainsAnotherConcreteExtension(object):

        class MyOtherConcreteExtensionMock(object):
            _is_zaf_extension = True

    class DoesNotContainConcreteExtension(object):
        pass

    def test_returns_the_empty_list_if_there_are_no_extensions(self):
        self._test_find_extensions([], [])

    def test_returns_the_empty_list_if_there_are_no_concrete_extensions(self):
        inspectables = [self.DoesNotContainConcreteExtension]
        self._test_find_extensions(inspectables, [])

    def test_can_find_a_concrete_extension(self):
        inspectables = [self.ContainsConcreteExtension]
        self._test_find_extensions(inspectables, ['MyConcreteExtensionMock'])

    def test_can_find_multiple_concrete_extensions(self):
        inspectables = [self.ContainsConcreteExtension, self.ContainsAnotherConcreteExtension]
        self._test_find_extensions(
            inspectables, ['MyConcreteExtensionMock', 'MyOtherConcreteExtensionMock'])

    def _test_find_extensions(self, inspectables, expected_names):
        found = _find_extensions_by_inspection(inspectables)
        self.assertEqual(sorted(map(lambda item: item.__name__, found)), sorted(expected_names))


class TestExtensionManager(unittest.TestCase):

    def setUp(self):
        self.em = ExtensionManager()

    def test_the_registry_is_initially_empty(self):
        self.assertEqual(self.em.command_extension_instances, [])

    def test_can_load_an_addon(self):
        self.em.find_addons('zaf.test_addons')
        self.assertTrue(self._ensure_in_all_extensions('testcommandaddon'))

    def test_call_init_with_something_loaded(self):
        self.em.find_addons('zaf.test_addons')
        self.em.enable_all_extensions()

        with patch('zaf.extensions.test.addons.testcommandaddon.TestCommandAddon.__init__',
                   new=Mock(side_effect=(None, ))) as mock:
            config = Mock()
            filtered_config = {'k': 'v'}
            config.filter_config = Mock(return_value=filtered_config)
            self.em.initialize_command_extensions(config, command=TESTCOMMANDADDON_COMMAND)
            mock.assert_called_with(filtered_config, {})

    def test_call_register_dispatchers_on_initialized_addon(self):
        self.em.find_addons('zaf.test_addons')
        self.em.enable_all_extensions()

        with patch(
                'zaf.extensions.test.addons.testcommandaddon.TestCommandAddon.register_dispatchers'
        ) as mock:
            self.em.initialize_command_extensions(Mock(), command=TESTCOMMANDADDON_COMMAND)
            messagebus = Mock()
            self.em.register_dispatchers(messagebus)
            mock.assert_called_with(messagebus)

    def test_call_destroy_on_initialized_addon(self):
        self.em.find_addons('zaf.test_addons')
        self.em.enable_all_extensions()

        with patch('zaf.extensions.test.addons.testcommandaddon.TestCommandAddon.destroy') as mock:
            self.em.initialize_command_extensions(Mock(), command=TESTCOMMANDADDON_COMMAND)
            self.em.destroy()
            mock.assert_called_with()

    def test_find_plugins_with_empty_path(self):
        with tempfile.TemporaryDirectory() as empty_directory:
            self.em.find_plugins(empty_directory)
        self.assertEqual(self.em.command_extension_instances, [])

    def test_destroy_called_on_all_extensions_even_if_exceptions_are_raised(self):
        called = Queue()

        @CommandExtension('extension1')
        class Extension1(AbstractExtension):

            def destroy(self):
                called.put(1)
                raise Exception('')

        @FrameworkExtension('extension2')
        class Extension2(AbstractExtension):

            def destroy(self):
                called.put(2)
                raise Exception('')

        self.em.add_extension(Extension1)
        self.em.add_extension(Extension2)
        self.em.command_extension_instances.append(Extension1(Mock(), Mock()))
        self.em.framework_extension_instances.append(Extension2(Mock(), Mock()))

        self.em.enable_all_extensions()

        self.em.destroy()
        self.assertEqual(called.get(timeout=1), 1)
        self.assertEqual(called.get(timeout=1), 2)

    def _ensure_in_all_extensions(self, name):
        return any(item.name == name for item in self.em.all_extensions)


class TestEndpointsAndMessages(unittest.TestCase):

    def setUp(self):
        self.em = ExtensionManager()

    def test_call_get_endpoints_and_messages_with_uninitialized_command_extension(self):
        extension = Mock()
        extension.endpoints_and_messages = {Mock(): [Mock(), Mock()]}
        extension.extension_type = ExtensionType.COMMAND
        extension.load_order = 5
        command = CommandId('name', 'doc', lambda x: x, ())
        extension.extends = [command]

        self.em._all_extensions.append(extension)
        self.em.enable_all_extensions()

        self.assertEqual(
            self.em.get_endpoints_and_messages(command), extension.endpoints_and_messages)

    def test_get_endpoints_and_messages_combines_endpoints_and_messages_from_all_addons(self):
        endpoint1 = EndpointId('extension1', '')
        endpoint2 = EndpointId('extension2', '')
        msg1 = MessageId('msg1', '')
        msg2 = MessageId('msg2', '')
        msg3 = MessageId('msg3', '')

        @FrameworkExtension('extension1', endpoints_and_messages={endpoint1: [msg1, msg2]})
        class Extension1():
            pass

        @FrameworkExtension('extension2', endpoints_and_messages={endpoint2: [msg3]})
        class Extension2():
            pass

        self.em.add_extension(Extension1)
        self.em.add_extension(Extension2)
        self.em.enable_all_extensions()

        actual_endpoints_and_messages = self.em.get_endpoints_and_messages()
        self.assertEqual(actual_endpoints_and_messages[endpoint1], [msg1, msg2])
        self.assertEqual(actual_endpoints_and_messages[endpoint2], [msg3])


class TestDispatcherDecorators(unittest.TestCase):

    def test_inactive_if_activate_on_is_not_fullfilled(self):
        extension_manager = ExtensionManager()
        messagebus = Mock()
        my_message_ids = object()
        my_endpoint_ids = object()
        my_config_opt = ConfigOptionId('name', 'description')
        config = MagicMock()
        config.filter_config.return_value.get.return_value = False
        config.filter_config.return_value.__contains__.return_value = True

        @FrameworkExtension(
            'extension',
            config_options=[ConfigOption(my_config_opt, required=True)],
            activate_on=[my_config_opt])
        class Extension(AbstractExtension):

            @callback_dispatcher(message_ids=my_message_ids, endpoint_ids=my_endpoint_ids)
            def my_callback_dispatcher(self):
                pass

        try:
            extension_manager.initialize_framework_extension(Extension, config)
            extension_manager.register_dispatchers(messagebus)
            self.assertEqual(messagebus.register_dispatcher.call_count, 0)
        finally:
            extension_manager.destroy()

    def test_active_if_activate_on_is_fullfilled(self):
        extension_manager = ExtensionManager()
        messagebus = Mock()
        my_message_ids = object()
        my_endpoint_ids = object()
        my_config_opt = ConfigOptionId('name', 'description')
        config = MagicMock()
        config.filter_config.return_value.get.return_value = True
        config.filter_config.return_value.__contains__.return_value = True

        @FrameworkExtension(
            'extension',
            config_options=[ConfigOption(my_config_opt, required=True)],
            activate_on=[my_config_opt])
        class Extension(AbstractExtension):

            @callback_dispatcher(message_ids=my_message_ids, endpoint_ids=my_endpoint_ids)
            def my_callback_dispatcher(self):
                pass

        try:
            extension_manager.initialize_framework_extension(Extension, config)
            extension_manager.register_dispatchers(messagebus)
            self.assertEqual(messagebus.register_dispatcher.call_count, 1)
        finally:
            extension_manager.destroy()

    def test_inactive_if_deactivate_on_is_fullfilled(self):
        extension_manager = ExtensionManager()
        messagebus = Mock()
        my_message_ids = object()
        my_endpoint_ids = object()
        my_config_opt = ConfigOptionId('name', 'description')
        config = MagicMock()
        config.filter_config.return_value.get.return_value = True
        config.filter_config.return_value.__contains__.return_value = True

        @FrameworkExtension(
            'extension',
            config_options=[ConfigOption(my_config_opt, required=True)],
            deactivate_on=[my_config_opt])
        class Extension(AbstractExtension):

            @callback_dispatcher(message_ids=my_message_ids, endpoint_ids=my_endpoint_ids)
            def my_callback_dispatcher(self):
                pass

        try:
            extension_manager.initialize_framework_extension(Extension, config)
            extension_manager.register_dispatchers(messagebus)
            self.assertEqual(messagebus.register_dispatcher.call_count, 0)
        finally:
            extension_manager.destroy()

    def test_callback_dispatcher(self):
        extension_manager = ExtensionManager()
        messagebus = Mock()
        my_message_ids = object()
        my_endpoint_ids = object()

        @FrameworkExtension('extension')
        class Extension(AbstractExtension):

            @callback_dispatcher(message_ids=my_message_ids, endpoint_ids=my_endpoint_ids)
            def my_callback_dispatcher(self):
                pass

        try:
            extension_manager.initialize_framework_extension(Extension, Mock())
            extension_manager.register_dispatchers(messagebus)
            messagebus.register_dispatcher.assert_called_once_with(
                TypeComparator(CallbackDispatcher), my_message_ids, my_endpoint_ids, None)
        finally:
            extension_manager.destroy()

    def test_sequential_dispatcher(self):
        extension_manager = ExtensionManager()
        messagebus = Mock()
        my_message_ids = object()
        my_endpoint_ids = object()

        @FrameworkExtension('extension')
        class Extension(AbstractExtension):

            @sequential_dispatcher(message_ids=my_message_ids, endpoint_ids=my_endpoint_ids)
            def my_sequential_dispatcher(self):
                pass

        try:
            extension_manager.initialize_framework_extension(Extension, Mock())
            extension_manager.register_dispatchers(messagebus)
            messagebus.register_dispatcher.assert_called_once_with(
                TypeComparator(SequentialDispatcher), my_message_ids, my_endpoint_ids, None)
        finally:
            extension_manager.destroy()

    def test_threadpool_dispatcher(self):
        extension_manager = ExtensionManager()
        messagebus = Mock()
        my_message_ids = object()
        my_endpoint_ids = object()

        @FrameworkExtension('extension')
        class Extension(AbstractExtension):

            @threadpool_dispatcher(
                message_ids=my_message_ids, endpoint_ids=my_endpoint_ids, max_workers=4)
            def my_threadpool_dispatcher(self):
                pass

        try:
            extension_manager.initialize_framework_extension(Extension, Mock())
            extension_manager.register_dispatchers(messagebus)
            messagebus.register_dispatcher.assert_called_once_with(
                TypeComparator(ThreadPoolDispatcher), my_message_ids, my_endpoint_ids, None)
        finally:
            extension_manager.destroy()

    def test_concurrent_dispatcher(self):
        extension_manager = ExtensionManager()
        messagebus = Mock()
        my_message_ids = object()
        my_endpoint_ids = object()

        @FrameworkExtension('extension')
        class Extension(AbstractExtension):

            @concurrent_dispatcher(message_ids=my_message_ids, endpoint_ids=my_endpoint_ids)
            def my_concurrent_dispatcher(self):
                pass

        try:
            extension_manager.initialize_framework_extension(Extension, Mock())
            extension_manager.register_dispatchers(messagebus)
            messagebus.register_dispatcher.assert_called_once_with(
                TypeComparator(ConcurrentDispatcher), my_message_ids, my_endpoint_ids, None)
        finally:
            extension_manager.destroy()

    def test_register_multiple(self):
        extension_manager = ExtensionManager()
        messagebus = Mock()
        my_message_ids = object()
        my_endpoint_ids = object()
        my_other_message_ids = object()
        my_other_endpoint_ids = object()

        @FrameworkExtension('extension')
        class Extension(AbstractExtension):

            @concurrent_dispatcher(message_ids=my_message_ids, endpoint_ids=my_endpoint_ids)
            @concurrent_dispatcher(
                message_ids=my_other_message_ids, endpoint_ids=my_other_endpoint_ids)
            def my_concurrent_dispatcher(self):
                pass

        try:
            extension_manager.initialize_framework_extension(Extension, Mock())
            extension_manager.register_dispatchers(messagebus)
            messagebus.register_dispatcher.assert_any_call(
                TypeComparator(ConcurrentDispatcher), my_message_ids, my_endpoint_ids, None)
            messagebus.register_dispatcher.assert_any_call(
                TypeComparator(ConcurrentDispatcher), my_other_message_ids, my_other_endpoint_ids,
                None)
        finally:
            extension_manager.destroy()

    def test_combine_manual_and_decorated_dispatchers(self):
        extension_manager = ExtensionManager()
        messagebus = Mock()

        @FrameworkExtension('extension')
        class Extension(AbstractExtension):

            def register_dispatchers(self, messagebus):
                self._dispatcher = CallbackDispatcher(messagebus, self.my_manual_dispatcher)
                self._dispatcher.register(None)

            def my_manual_dispatcher(self):
                pass

            @concurrent_dispatcher(None)
            def my_decorated_dispatcher(self):
                pass

            def destroy(self):
                self._dispatcher.destroy()

        extension_manager.initialize_framework_extension(Extension, Mock())
        extension_manager.register_dispatchers(messagebus)
        messagebus.register_dispatcher.assert_has_calls(
            [
                call(TypeComparator(ConcurrentDispatcher), None, None, None),
                call(TypeComparator(CallbackDispatcher), None, None, None)
            ])

    def test_initialize_fails_for_dispatcher_with_entity_option_id_if_not_instantiated(self):
        extension_manager = ExtensionManager()
        entity_option_id = Mock()
        my_message_ids = object()
        my_endpoint_ids = object()

        @FrameworkExtension('extension')
        class Extension(AbstractExtension):

            @concurrent_dispatcher(
                message_ids=my_message_ids,
                endpoint_ids=my_endpoint_ids,
                entity_option_id=entity_option_id)
            def my_decorated_dispatcher(self):
                pass

        with self.assertRaises(InvalidDispatcherEntityError):
            extension_manager.initialize_framework_extension(Extension, Mock())

    def test_initialize_fails_for_dispatcher_with_entity_option_id_if_not_instantiated_on_that_id(
            self):
        extension_manager = ExtensionManager()
        instantiate_on_id = Mock()
        entity_option_id = Mock()
        my_message_ids = object()
        my_endpoint_ids = object()

        @FrameworkExtension(
            'extension',
            config_options=[ConfigOption(instantiate_on_id, required=False, instantiate_on=True)])
        class Extension(AbstractExtension):

            @concurrent_dispatcher(
                message_ids=my_message_ids,
                endpoint_ids=my_endpoint_ids,
                entity_option_id=entity_option_id)
            def my_decorated_dispatcher(self):
                pass

        config = Mock()
        config.get.return_value = ['entity']
        with self.assertRaises(InvalidDispatcherEntityError):
            extension_manager.initialize_framework_extension(Extension, config)

    def test_deregister_called_on_all_dispatchers_even_when_exceptions_are_raised(self):
        extension_manager = ExtensionManager()

        dispatcher1 = Mock()
        dispatcher1.destroy.side_effect = Exception('')
        dispatcher2 = Mock()
        dispatcher2.destroy.side_effect = Exception('')

        extension_manager._all_dispatchers.append(dispatcher1)
        extension_manager._all_dispatchers.append(dispatcher2)

        extension_manager.destroy()
        dispatcher2.destroy.assert_called_with()
        dispatcher1.destroy.assert_called_with()


class TestCommands(unittest.TestCase):

    def setUp(self):
        self.em = ExtensionManager()

    def get_extension_mock(self):
        extension = Mock()
        extension.extension_type = ExtensionType.FRAMEWORK
        extension.load_order = 5
        return extension

    def get_command_mock(self, name):
        command = Mock()
        command.name = name
        return command

    def test_call_get_commands(self):
        extension = self.get_extension_mock()
        command = Mock(name='name')
        extension.commands = [command]
        self.em._all_extensions.append(extension)
        self.em.enable_all_extensions()

        self.assertCountEqual(self.em.get_commands(), [command])

    def test_call_get_commands_alphabetical(self):
        extension1 = self.get_extension_mock()
        command_a = self.get_command_mock('A')
        command_c = self.get_command_mock('C')
        extension1.commands = [command_a, command_c]
        self.em._all_extensions.append(extension1)

        extension2 = self.get_extension_mock()
        command_b = self.get_command_mock('B')
        extension2.commands = [command_b]
        self.em._all_extensions.append(extension2)

        self.em.enable_all_extensions()

        self.assertListEqual(self.em.get_commands(), [command_a, command_b, command_c])


class TestCommandExtensionMatching(unittest.TestCase):

    def setUp(self):
        self.em = ExtensionManager()

    @staticmethod
    def mock_extension(extends):
        extension = Mock()
        extension.endpoints_and_messages = {Mock(): [Mock(), Mock()]}
        extension.extension_type = ExtensionType.COMMAND
        extension.load_order = 5
        extension.extends = extends
        return extension

    def test_extension_extending_commandid_matches(self):
        command = CommandId('name', 'doc', lambda x: x, ())
        extension = self.mock_extension(extends=[command])

        self.em._all_extensions.append(extension)
        self.em.enable_all_extensions()

        self.assertEqual(self.em.command_extensions(command), [extension])

    def test_extension_extending_command_capability_matches_command_using_same(self):
        extension = self.mock_extension(extends=['a'])
        command = CommandId('name', 'doc', lambda x: x, (), uses=['a'])

        self.em._all_extensions.append(extension)
        self.em.enable_all_extensions()

        self.assertEqual(self.em.command_extensions(command), [extension])

    def test_extension_extending_command_capability_matches_command_name(self):
        extension = self.mock_extension(extends=['name'])

        command = CommandId('name', 'doc', lambda x: x, ())

        self.em._all_extensions.append(extension)
        self.em.enable_all_extensions()

        self.assertEqual(self.em.command_extensions(command), [extension])

    def test_command_capability_matches_extends(self):
        extension = self.mock_extension(extends=['a'])

        self.em._all_extensions.append(extension)
        self.em.enable_all_extensions()

        self.assertEqual(self.em.command_extensions('a'), [extension])

    def test_mixed_extends(self):
        command = CommandId('name', 'doc', lambda x: x, (), uses=['a'])

        extension_1 = self.mock_extension(extends=[command])
        self.em._all_extensions.append(extension_1)
        extension_2 = self.mock_extension(extends=['a', 'name'])
        self.em._all_extensions.append(extension_2)

        self.em.enable_all_extensions()

        self.assertEqual(self.em.command_extensions(command), [extension_1, extension_2])

    def test_none_command_always_matches(self):
        extension = self.mock_extension(extends=['a'])

        self.em._all_extensions.append(extension)
        self.em.enable_all_extensions()

        self.assertEqual(self.em.command_extensions(None), [extension])
