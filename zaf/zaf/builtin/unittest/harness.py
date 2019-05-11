import queue
from contextlib import contextmanager
from unittest.mock import DEFAULT, MagicMock, patch

from zaf.component.decorator import component
from zaf.component.factory import Factory
from zaf.component.manager import ComponentManager, create_registry
from zaf.component.scope import Scope
from zaf.config.manager import ConfigManager, ConfigView
from zaf.extensions.manager import _is_extension_active
from zaf.messages.decorator import get_dispatcher_descriptors
from zaf.messages.dispatchers import LocalMessageQueue
from zaf.messages.message import EndpointId
from zaf.messages.messagebus import MessageBus

HARNESS_ENDPOINT = EndpointId('harness', '')


class ComponentMock(object):

    def __init__(self, name, mock, scope=None, can=None, provided_by_extension=None):
        self.name = name
        self.mock = mock
        self.scope = scope
        self.can = can
        self.provided_by_extension = provided_by_extension

    def __name__(self):
        return self.name

    def __call__(self, *args, **kwargs):
        return self.mock


class SyncMockTimeoutException(Exception):
    pass


class SyncMock(MagicMock):
    """
    Mock with the extra method to wait for a call to take place.

    side_effect is not available. If side_effect is passed in kwargs, it will
    be overwritten by the custom side_effect that this class provides.

    .. code-block:: python

        mock = SyncMock()
        mock.func('arg', key='value')
        args, kwargs = mock.func.wait_for_call(timeout=4)
        mock.func.assert_called_with('arg', key='value')
        self.assertEqual(args, ('arg',))
        self.assertEqual(kwargs, {'key':'value'})
    """

    def __init__(self, *args, **kwargs):

        def side_effect(*mock_args, **mock_kwargs):
            self._result.put((mock_args, mock_kwargs))
            return DEFAULT

        kwargs['side_effect'] = side_effect
        super().__init__(*args, **kwargs)
        self._result = queue.Queue()

    def wait_for_call(self, timeout=None):
        """
        Wait for the next call to the mock.

        :param timeout: timeout is seconds
        :return: tuple with args and kwargs that the mock was called with
        """
        try:
            return self._result.get(timeout=timeout)
        except queue.Empty:
            raise SyncMockTimeoutException() from None


class ExtensionTestHarness(object):
    """
    Class that helps testing extensions by creating and configuration the surroundings.

    It can be used as a context manager and helps with multi threaded tests.

    .. code-block:: python

        with ExtensionTestHarness(
                MyExtension(), {endpoint: [message1, message2]}, {option1: value1, option2: value2}) as harness:
            with harness.patch('module.to.patch') as m:
                harness.trigger_event(message1, endpoint, data=MyData())
                m.wait_for_call() # Waits for the call to module.to.patch. Needed due to multi threading.
                m.assert_called_with('the wanted value')

    """

    def __init__(
            self, constructor, entity=None, endpoints_and_messages=None, config=None,
            components=None):
        """
        Initialize a new Harness for an extension and defines endpoints_and_messages in the messagebus.

        :param constructor: the constructor of the extension to test
        :param entity: If not given and the extension is instantiated on an entity the first entity
                       in the config will be used. Otherwise this can be used to set the wanted entity.
        :param endpoints_and_messages: endpoints and messages that the extensions wants to subscribe to
        :param config: Instance of ConfigManager with the wanted config for the extension.
        :param components: The components to insert into the component registry. List of ComponentMock
        """
        self._constructor = constructor

        self.config = ConfigManager() if config is None else config
        self._all_dispatchers = []
        self._instances = {}
        self._entity = None
        self._entity_option_id = None
        self.init_component_handling([] if components is None else components)

        if not isinstance(self._constructor, type):
            raise Exception('Extension should be a constructor of an extension, not an instance.')

        if endpoints_and_messages:
            self.messagebus.define_endpoints_and_messages(endpoints_and_messages)

        config_options = self._constructor.config_options
        config_option_ids = [c.option_id for c in config_options]
        self.config.set_default_values(config_option_ids)
        self.init_entity(entity, config_options)

        self.assert_required_options(config_options, self._entity_option_id)

        self._config_view = ConfigView(
            self.config, config_option_ids, self._entity_option_id, self._entity)
        self._active = _is_extension_active(self._config_view, constructor)

    def init_entity(self, entity, config_options):
        self._entity_option_id = None

        entity_option_ids = [c.option_id for c in config_options if c.instantiate_on]
        if entity_option_ids:
            self._entity_option_id = entity_option_ids[0]
            entities = self.config.get(self._entity_option_id)
            if entity:
                if entity not in entities:
                    AssertionError(
                        "Entity '{entity}' is not a valid entity for '{option_id}', "
                        "valid options are '{entities}'".format(
                            entity=entity, option_id=self._entity_option_id.key, entities=entities))
                self._entity = entity
            else:
                self._entity = entities[0]

            self._instances[self._entity_option_id] = self._entity

    def init_component_handling(self, components):
        self.component_registry = create_registry()
        self.component_manager = ComponentManager(self.component_registry)
        self.component_factory = Factory(self.component_manager)
        self.messagebus = MessageBus(self.component_factory, Scope('session'))

        components.append(ComponentMock(name='ComponentFactory', mock=self.component_factory))
        components.append(ComponentMock(name='MessageBus', mock=self.messagebus))
        components.append(ComponentMock(name='Config', mock=self.config))
        components.append(ComponentMock(name='ComponentManager', mock=self.component_manager))
        components.append(ComponentMock(name='ExtensionManager', mock=MagicMock()))
        for comp in components:
            if type(comp) == ComponentMock:
                component(
                    name=comp.name,
                    scope=comp.scope,
                    can=comp.can,
                    provided_by_extension=comp.provided_by_extension)(comp, self.component_manager)
            else:
                self.component_manager.register_component(comp)

    def assert_required_options(self, config_options, entity_option_id):

        def assert_in_config(option_id, entity=None):
            if self.config.get(option_id, entity=entity) is None:
                raise AssertionError(
                    'Missing required option {option}{for_entity}'.format(
                        option=option.option_id.key,
                        for_entity='for entity {entity}'.format(entity=entity) if entity else ''))

        for option in config_options:
            if option.required and not option.option_id.has_default:
                if option.option_id.at is not None and option.option_id == entity_option_id:
                    assert_in_config(option.option_id, entity=self._entity)
                elif option.option_id.at is not None:
                    entities = self.config.get(option.option_id.at)
                    if not option.option_id.at.multiple:
                        entities = [entities]

                    for entity in entities:
                        assert_in_config(option.option_id, entity=entity)
                else:
                    assert_in_config(option.option_id)

    @property
    def extension(self):
        return self._instance

    def __enter__(self):
        self._instance = self._constructor(self._config_view, self._instances)
        self.messagebus.define_endpoints_and_messages(self._instance.endpoints_and_messages)

        if hasattr(self._instance, 'register_components'):
            self._instance.register_components(self.component_manager)

        for method, descriptor in get_dispatcher_descriptors(self._instance):
            dispatcher = descriptor.dispatcher_constructor(self.messagebus, method)
            entities = None
            if descriptor.entity_option_id is not None:
                entities = [self._instances[descriptor.entity_option_id]]
            if self._active:
                dispatcher.register(
                    descriptor.message_ids, endpoint_ids=descriptor.endpoint_ids, entities=entities)
            self._all_dispatchers.append(dispatcher)

        self._instance.register_dispatchers(self.messagebus)
        return self

    def __exit__(self, *exc_info):
        for dispatcher in self._all_dispatchers:
            if self._active:
                dispatcher.destroy()
        self._instance.destroy()

    def trigger_event(self, message_id, sender_endpoint_id, entity=None, data=None):
        self.messagebus.trigger_event(message_id, sender_endpoint_id, entity, data)

    def send_request(self, message_id, receiver_endpoint_id=None, entity=None, data=None):
        return self.messagebus.send_request(message_id, receiver_endpoint_id, entity, data)

    def any_registered_dispatchers(self, message_id, endpoint_id=None, entity=None):
        return self.messagebus.has_registered_dispatchers(message_id, endpoint_id, entity)

    @contextmanager
    def message_queue(self, message_ids, endpoint_ids=None, entities=None, match=None, priority=0):
        with LocalMessageQueue(self.messagebus, message_ids, endpoint_ids, entities, match,
                               priority) as q:
            yield q

    def patch(self, target, *patch_args, **patch_kwargs):
        """
        Patch with a special multi threaded wait_for_call method.

        The returned mock stores the arguments when it's called in a queue and then
        wait_for_call can be used to get the a tuple of *args* and *kwargs* that the
        mock was called with.
        The mock is a normal mock so after waiting for a call the normal mock asserts
        can be called.

        .. code-block:: python

            harness = ExtensionTestHarness(...)

            with harness.patch('function.to.patch') as mock:
                trigger_something()
                mock_args, mock_kwargs = mock.wait_for_call(timeout=4)
                mock.assert_called_once()
                self.assertEqual(mock_args[0], 'expected_value')

        :param target: the target
        :param patch_args: args sent to normal patch
        :param patch_kwargs: kwargs sent to normal patch
        :return: a mock with the extra wait_for_call method
        """

        return patch(target, *patch_args, new=SyncMock(), **patch_kwargs)
