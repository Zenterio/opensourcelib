import configparser
import copy
import functools
import glob
import inspect
import logging
import os
import sys
from collections import OrderedDict, defaultdict
from importlib import import_module

from zaf.config.options import ConfigOptionId
from zaf.messages.decorator import get_dispatcher_descriptors
from zaf.utils.pythonloader import load_module_or_package, load_submodules_and_subpackages
from zaf.utils.subgrouplist import eval_subgroup_list

from .extension import ExtensionType, is_concrete_extension

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class EndpointAlreadyDefined(Exception):
    pass


class ExtensionNotLoaded(Exception):
    pass


class PluginPackageError(Exception):
    pass


class MultipleInstanceOptions(Exception):
    pass


class RequiredOptionNotFound(Exception):
    pass


class InvalidDispatcherEntityError(Exception):
    pass


def _find_entry_points(path, config):

    def _follow_egg_link(egg_link_path):
        with open(egg_link_path, 'r') as f:
            egg_info_path = f.readline().strip()
            egg_info_paths = map(
                functools.partial(os.path.join, egg_info_path), os.listdir(egg_info_path))
            return filter(lambda p: p.endswith('.egg-info'), egg_info_paths)

    paths = list(map(functools.partial(os.path.join, path), os.listdir(path)))
    all_infos = list(filter(lambda p: p.endswith('.dist-info') or p.endswith('.egg-info'), paths))
    for egg_link_path in filter(lambda p: p.endswith('.egg-link'), paths):
        all_infos.extend(_follow_egg_link(egg_link_path))

    for f in [f for f in all_infos if os.path.exists(f)]:
        config.read(os.path.join(f, 'entry_points.txt'))


def _load_entry_point(entry_point):
    module_name, attr = entry_point.split(':')
    module = import_module(module_name)
    try:
        return getattr(module, attr)
    except AttributeError as e:
        raise ImportError(str(e))


def _find_extensions_by_namespace(namespace):
    config = configparser.ConfigParser()
    for path in filter(lambda path: 'site-package' in path, sys.path):
        _find_entry_points(path, config)
    try:
        return {_load_entry_point(entry_point) for entry_point in config[namespace].values()}
    except KeyError:
        return set()


def _find_extensions_by_inspection(inspectables):
    extensions = []
    for inspectable in inspectables:
        for name, member in inspect.getmembers(inspectable):
            if inspect.isclass(member) and \
                    is_concrete_extension(member) and member not in extensions:

                extensions.append(member)
    return extensions


def _is_extension_active(filtered_config, extension):
    """
    Items are "and:ed" together, while items in subgroups are "or:ed".

    For an extension to be active, all config option ids in the activate_on
    list must be truthy. Within a subgroup, it is enough for any of the items
    to be truthy for the subgroup to be considered truthy.

    In contrast, deactivate_on has the opposite effect. If it is fullfilled,
    it will force the extension to be inactive; deactivate_on has presidence
    over acticate_on.
    """
    if extension.deactivate_on and eval_subgroup_list(filtered_config.get, extension.deactivate_on):
        return False

    if extension.activate_on and not eval_subgroup_list(filtered_config.get, extension.activate_on):
        return False

    return True


class ExtensionManager(object):

    def __init__(self):
        self._all_extensions = []
        self._all_dispatchers = []
        self._enabled_extensions = []
        self._entity_per_instance = defaultdict(None)
        self.command_extension_instances = []
        self.framework_extension_instances = []

    def extensions_with_name(self, name):
        return [extension for extension in self._all_extensions if extension.name == name]

    @property
    def all_extensions(self):
        return sorted(self._all_extensions, key=lambda e: e.load_order)

    def add_extension(self, extension):
        self._all_extensions.append(extension)

    def enable_extension(self, extension):
        """
        Enable an extension.

        :param extension: the extension to enable
        """
        self._enabled_extensions.append(extension)

    def enable_all_extensions(self):
        """Enable all registered extensions."""
        for extension in self._all_extensions:
            self.enable_extension(extension)

    @property
    def enabled_extensions(self):
        return self._enabled_extensions

    def find_addons(self, namespace='zaf.addons'):
        """
        Find addons using the namespace.

        :param namespace: the namespace to use when looking for addons
        """
        for addon in _find_extensions_by_namespace(namespace):
            addon.namespace = namespace
            self._all_extensions.append(addon)

    def find_plugins(self, path):
        """
        Find plugins using the path.

        :param path: the path to use when looking for plugins
        """
        root_init = os.path.join(path, '__init__.py')
        if os.path.exists(root_init):
            package_paths = [root_init]
        else:
            package_paths = glob.glob(os.path.join(path, '**', '__init__.py'))

        # Plugins may depend on other plugins. In order to support importing
        # things from one plugin in another plugin, make sure to add all
        # packages to sys.path before doing any actual imports.
        packages = []
        for package_path in package_paths:
            path, package = os.path.split(os.path.dirname(package_path))
            sys.path.insert(0, path)
            packages.append(package)

        for package in packages:
            root = load_module_or_package(package)
            extensions = _find_extensions_by_inspection(load_submodules_and_subpackages(root))
            for extension in extensions:
                self._all_extensions.append(extension)

    def framework_extensions(self, load_order_start=0, load_order_end=1000, only_enabled=True):
        """
        Return a list of framework extensions.

        The list is filtered to only include extensions with load order between
        load_order_start and load_order_end.

        If only_enabled is True then only enabled extensions with be included.

        :param load_order_start: the start load order
        :param load_order_end: the end load order
        :param only_enabled: if only enabled extensions should be included
        :return: list of framework extensions
        """
        extensions = self.all_extensions
        if only_enabled:
            extensions = self.enabled_extensions

        return [
            extension for extension in extensions
            if extension.extension_type == ExtensionType.FRAMEWORK
            and load_order_start <= extension.load_order <= load_order_end
        ]

    def command_extensions(self, command=None, only_enabled=True):
        """
        Return a list of command extensions.

        If command is specified then only extensions extending the command will be included.
        If only_enabled is True then only enabled extensions with be included.

        :param command: the command to look for extensions for
        :param only_enabled: if only enabled extensions should be included
        :return:
        """

        def is_command_capability(extend):
            return isinstance(extend, str)

        extensions = self.all_extensions
        if only_enabled:
            extensions = self.enabled_extensions

        if hasattr(command, 'uses'):
            uses = set(command.uses)
        elif isinstance(command, str):
            uses = {command}  # Same logic as CommandId
        else:
            uses = set()

        matching_extensions = []
        for extension in extensions:
            if extension.extension_type != ExtensionType.COMMAND:
                continue

            extends = set(extension.extends)
            command_capability_extends = {
                extend
                for extend in extends if is_command_capability(extend)
            }
            commandid_extends = extends - command_capability_extends

            if (command is None or command in commandid_extends
                    or command in {cmd.name for cmd in commandid_extends}
                    or (command_capability_extends and command_capability_extends <= uses)):
                matching_extensions.append(extension)

        return matching_extensions

    def initialize_framework_extension(self, extension, config):
        """
        Create a framework extension using the config.

        :param extension: the extension to initialize
        :param config: the config manager
        :return: the instance of the extension
        """
        instances = self._initialize_extension(extension, config)
        self.framework_extension_instances.extend(instances)
        return instances

    def initialize_command_extensions(self, config, command):
        """
        Create all command extensions for the specified command using the config.

        :param config: the config manager
        :param command: the command for which extensions should be initialized
        """
        for extension in self.command_extensions(command):
            self.command_extension_instances.extend(self._initialize_extension(extension, config))

    def _initialize_extension(self, extension, config):
        config_options = extension.config_options

        instances = [None]

        instance_options = [
            config_option.option_id for config_option in config_options
            if config_option.instantiate_on
        ]

        instance_option_id = None
        if len(instance_options) == 1:
            instance_option_id = instance_options[0]
        elif len(instance_options) > 1:
            raise MultipleInstanceOptions(
                'Not possible to instantiate extension {extension} on multiple options'.format(
                    extension=extension.name))

        if instance_option_id is not None:
            instances = config.get(instance_option_id)
            if not instance_option_id.multiple:
                instances = [instances]

        created_instances = []
        for instance in instances:
            filtered_config = config.filter_config(
                [config_option.option_id for config_option in config_options],
                instance_option_id,
                entity=instance)

            for required_id in [option.option_id for option in config_options if option.required]:
                if required_id not in filtered_config:
                    instance_repr = " instance '{instance}'".format(instance=instance)\
                        if instance_option_id is not None and instance_option_id.multiple else ''
                    raise RequiredOptionNotFound(
                        "Error initializing extension '{extension}'{instance}: "
                        "Required option '{option}' not found".format(
                            extension=extension.name,
                            option=required_id.name,
                            instance=instance_repr))

            logger.debug('Instantiating extension: {extension}'.format(extension=extension))
            extension_instance = extension(
                filtered_config,
                {instance_option_id: instance
                 for instance in [instance] if instance is not None})

            active = _is_extension_active(filtered_config, extension)
            logger.debug(
                'Extension {extension} is {active}'.format(
                    extension=extension, active='active' if active else 'inactive'))
            extension_instance._zaf_dispatcher_descriptors = {}
            for method, descriptor in get_dispatcher_descriptors(extension_instance):
                if descriptor.entity_option_id is not None:
                    if instance_option_id is None:
                        msg = 'Entity option id on {method} not allowed on non-instanced extension'.format(
                            method=method)
                        raise InvalidDispatcherEntityError(msg)
                    elif descriptor.entity_option_id != instance_option_id:
                        msg = (
                            'Invalid entity option id on {method}, only config options '
                            'with instantiate_on allowed.').format(method=method)
                        raise InvalidDispatcherEntityError(msg)

                max_workers = descriptor.max_workers
                if descriptor.max_workers is not None and isinstance(descriptor.max_workers,
                                                                     ConfigOptionId):
                    max_workers = filtered_config.get(descriptor.max_workers)

                descriptor_clone = copy.copy(descriptor)
                descriptor_clone.active = active
                descriptor_clone.entity = instance
                descriptor_clone.max_workers = max_workers
                extension_instance._zaf_dispatcher_descriptors[descriptor_clone] = method

            created_instances.append(extension_instance)

        return created_instances

    def get_endpoints_and_messages(self, command=None):
        """
        Get a dict mapping endpoints to the messages that should be defined for the endpoint.

        :param command: If not None Command Extensions will be filtered by the ones that are
                        applicable for the command
        :return: dict from MessageId to EndpointID
        """
        endpoints_and_messages = OrderedDict()
        for extension_id, extension_eps_and_msgs in self.get_extensions_endpoints_and_messages(
                command).items():
            for endpoint_id, message_ids in extension_eps_and_msgs.items():
                if endpoint_id in endpoints_and_messages:
                    raise EndpointAlreadyDefined(
                        'Extension {extension} tries to define already defined endpoint {endpoint}'.
                        format(extension=extension_id.name, endpoint=endpoint_id.name))
                endpoints_and_messages[endpoint_id] = message_ids
        return endpoints_and_messages

    def get_extensions_endpoints_and_messages(self, command=None):
        """
        Get a dict mapping ExtensionId to a dict mapping endpoints to messages.

        :param command: If not None Command Extensions will be filtered by the ones that are
                        applicable for the command
        :return: dict from ExtensionId to dictionary from EndpointId to list of MessageIds
        """
        extension_endpoints_and_messages = OrderedDict()
        for extension in self.framework_extensions():
            extension_endpoints_and_messages[
                extension.extension_id] = extension.endpoints_and_messages

        for extension in self.command_extensions(command):
            extension_endpoints_and_messages[
                extension.extension_id] = extension.endpoints_and_messages

        return extension_endpoints_and_messages

    def get_commands(self):
        """
        Get a list of all CommandIds registered by enabled extensions, in alphabetical order.

        :return: sorted list with CommandIds
        """
        commands = [
            command for extension in self.framework_extensions() for command in extension.commands
        ]
        return sorted(commands, key=lambda cmd: cmd.name)

    def register_components(self, component_manager):
        """
        Register components and component properties to the component manager for all enabled extensions.

        :param component_manager: the component manager
        """
        for extension in self.command_extension_instances + self.framework_extension_instances:
            if hasattr(extension, 'register_components'):
                extension.register_components(component_manager)

    def register_dispatchers(self, messagebus):
        """
        Register dispatchers to the messagebus for all enabled extensions.

        :param messagebus: the message bus
        """
        for extension in self.command_extension_instances + self.framework_extension_instances:
            for descriptor, method in extension._zaf_dispatcher_descriptors.items():
                if descriptor.active:
                    entities = None
                    additional_kwargs = {}
                    if descriptor.max_workers is not None:
                        additional_kwargs['max_workers'] = descriptor.max_workers

                    dispatcher = descriptor.dispatcher_constructor(
                        messagebus, method, priority=descriptor.priority, **additional_kwargs)
                    if descriptor.entity_option_id is not None:
                        entities = [descriptor.entity]
                    dispatcher.register(
                        descriptor.message_ids,
                        endpoint_ids=descriptor.endpoint_ids,
                        entities=entities,
                        optional=descriptor.optional)
                    self._all_dispatchers.append(dispatcher)
            if hasattr(extension, 'register_dispatchers'):
                extension.register_dispatchers(messagebus)

    def destroy(self):
        """Destroy all extension instances."""
        for dispatcher in self._all_dispatchers[::-1]:
            try:
                dispatcher.destroy()
            except Exception as e:
                msg = 'Error when deregistering dispatcher {dispatcher}: {msg}'.format(
                    dispatcher=dispatcher.log_repr(), msg=str(e))
                logger.debug(msg, exc_info=True)
                logger.warning(msg)
        for extension in self.command_extension_instances + self.framework_extension_instances:
            logger.debug('Destroying extension {name}'.format(name=str(extension)))
            if hasattr(extension, 'destroy'):
                try:
                    extension.destroy()
                except Exception as e:
                    msg = 'Error when destroying extension {extension}: {msg}'.format(
                        extension=extension.name, msg=str(e))
                    logger.debug(msg, exc_info=True)
                    logger.warning(msg)
