import queue
import unittest

from zaf.config.manager import ConfigManager
from zaf.config.options import ConfigOption, ConfigOptionId
from zaf.extensions.extension import AbstractExtension, CommandExtension
from zaf.messages.decorator import sequential_dispatcher
from zaf.messages.dispatchers import SequentialDispatcher
from zaf.messages.message import EndpointId, MessageId

from ..harness import ExtensionTestHarness, SyncMock, SyncMockTimeoutException


class _TestTestHarness(object):

    def test_harness_defines_endpoints_and_messages(self):
        endpoints_and_messages = {other_endpoint: [other_message]}
        harness = create_harness(
            self.extension, endpoints_and_messages, config={
                required_option: 'value'
            })

        self.assertEqual(
            harness.messagebus.get_defined_endpoints_and_messages(), {
                other_endpoint: [other_message]
            })

        with harness:
            self.assertEqual(
                harness.messagebus.get_defined_endpoints_and_messages(), {
                    my_endpoint: [my_message],
                    other_endpoint: [other_message]
                })

    def test_harness_registerextensions_dispatchers_on_enter(self):
        endpoints_and_messages = {other_endpoint: [other_message]}
        harness = create_harness(
            self.extension, endpoints_and_messages, config={
                required_option: 'value'
            })

        self.assertFalse(harness.any_registered_dispatchers(other_message, other_endpoint))
        with harness:
            self.assertTrue(harness.any_registered_dispatchers(other_message, other_endpoint))

    def test_trigger_event_triggers_dispatcher(self):
        endpoints_and_messages = {other_endpoint: [other_message]}
        with create_harness(self.extension, endpoints_and_messages, config={required_option:
                                                                            'value'}) as harness:
            harness.trigger_event(other_message, other_endpoint, data='message')
            self.assertEqual(harness.extension.queue.get(timeout=1).data, 'message')

    def test_send_request_triggers_dispatcher(self):
        endpoints_and_messages = {other_endpoint: [other_message]}
        with create_harness(self.extension, endpoints_and_messages, config={required_option:
                                                                            'value'}) as harness:
            harness.send_request(my_message, my_endpoint, data='message')
            self.assertEqual(harness.extension.queue.get(timeout=1).data, 'message')

    def test_message_queue(self):
        endpoints_and_messages = {other_endpoint: [other_message]}
        with create_harness(self.extension, endpoints_and_messages, config={required_option:
                                                                            'value'}) as harness:
            with harness.message_queue([other_message], [other_endpoint]) as queue:
                harness.trigger_event(other_message, other_endpoint)
                self.assertEqual(queue.get(timeout=1).message_id, other_message)

    def test_raise_exception_when_required_option_is_not_specified(self):
        self.assertRaises(AssertionError, create_harness, self.extension, {}, config={})

    def test_wait_for_call_on_harness_patch_blocks_until_call_has_been_performed_and_returns_args_and_kwargs(
            self):
        endpoints_and_messages = {other_endpoint: [other_message]}
        with create_harness(self.extension, endpoints_and_messages, config={required_option:
                                                                            'value'}) as harness:
            with harness.patch('zaf.builtin.unittest.test.test_harness.do') as mock:
                harness.send_request(my_message, my_endpoint, data='message')
                args, kwargs = mock.wait_for_call(timeout=1)
                self.assertEqual(args[1].data, 'message')


def create_harness(extension, endpoints_and_messages, config={}):
    config_manager = ConfigManager()
    for id, value in config.items():
        config_manager.set(id, value)

    return ExtensionTestHarness(
        extension, endpoints_and_messages=endpoints_and_messages, config=config_manager)


other_endpoint = EndpointId('otherendpoint', '')
other_message = MessageId('othermessage', '')

my_endpoint = EndpointId('myendpoint', '')
my_message = MessageId('mymessage', '')

required_option = ConfigOptionId('opt', '')


@CommandExtension(
    'name',
    config_options=[ConfigOption(required_option, required=True)],
    extends=[],
    endpoints_and_messages={my_endpoint: [my_message]},
)
class MyManualExtension(AbstractExtension):

    def __init__(self, config, instances):
        self.queue = queue.Queue()

    def register_dispatchers(self, messagebus):
        self.dispatcher = SequentialDispatcher(messagebus, self.handle_message)
        self.dispatcher.register([other_message], [other_endpoint])
        self.dispatcher.register([my_message], [my_endpoint])

    def handle_message(self, message):
        do(self.queue, message)

    def destroy(self):
        self.dispatcher.destroy()


@CommandExtension(
    'name',
    config_options=[ConfigOption(required_option, required=True)],
    extends=[],
    endpoints_and_messages={my_endpoint: [my_message]},
)
class MyDecoratedExtension(AbstractExtension):

    def __init__(self, config, instances):
        self.queue = queue.Queue()

    @sequential_dispatcher([other_message], [other_endpoint])
    @sequential_dispatcher([my_message], [my_endpoint])
    def handle_message(self, message):
        do(self.queue, message)


class TestTestHarnessWithManualDispatchers(_TestTestHarness, unittest.TestCase):
    extension = MyManualExtension


class TestTestHarnessWithDecoratedDispatchers(_TestTestHarness, unittest.TestCase):
    extension = MyDecoratedExtension


def do(queue, message):
    queue.put(message)


class TestSyncMock(unittest.TestCase):

    def test_works_like_a_normal_mock(self):
        mock = SyncMock()
        mock.call_function(1, 2)
        mock.call_function.assert_called_with(1, 2)

    def test_wait_for_call_raise_exception_on_timeout(self):
        mock = SyncMock()
        with self.assertRaises(SyncMockTimeoutException):
            mock.wait_for_call(timeout=0)

    def test_wait_for_call_returns_args_and_kwargs(self):
        mock = SyncMock()
        mock(1, 1, k='v')
        args, kwargs = mock.wait_for_call(timeout=0)
        self.assertEqual(args, (1, 1))
        self.assertEqual(kwargs, {'k': 'v'})

    def test_nested_calls_also_works(self):
        mock = SyncMock()
        mock.my_function(1, k='v')
        args, kwargs = mock.my_function.wait_for_call(timeout=0)
        self.assertEqual(args, (1, ))
        self.assertEqual(kwargs, {'k': 'v'})

    def test_code_example_in_documentation(self):
        mock = SyncMock()
        mock.func('arg', key='value')
        args, kwargs = mock.func.wait_for_call(timeout=4)
        mock.func.assert_called_with('arg', key='value')
        self.assertEqual(args, ('arg', ))
        self.assertEqual(kwargs, {'key': 'value'})

    def test_synkmock_is_truthy(self):
        self.assertTrue(SyncMock())
