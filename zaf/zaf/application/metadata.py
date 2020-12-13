import inspect
import re
from collections import OrderedDict, defaultdict
from textwrap import dedent

from zaf.application import ApplicationContext
from zaf.commands.command import CommandId


class MetadataFilter(object):
    """Used to filter metadata."""

    def __init__(
            self,
            application_context=ApplicationContext.EXTENDABLE,
            include_hidden_commands=True,
            include_hidden_options=True,
            namespaces=None,
            additional_extensions=None):

        self.application_context = application_context
        self.include_hidden_commands = include_hidden_commands
        self.include_hidden_options = include_hidden_options
        self.namespaces = namespaces
        self.additional_extensions = additional_extensions if additional_extensions else []

    def include_extension_class(self, ext_class):
        return (
            not self.namespaces or ext_class.namespace in self.namespaces
            or ext_class.name in self.additional_extensions)

    def include_config_option_id(self, option_id):
        return (
            (self.include_hidden_options or not option_id.hidden)
            and option_id.is_applicable_for_application(self.application_context))

    def include_command(self, command):
        return (
            (self.include_hidden_commands or not command.hidden)
            and command.is_applicable_for_application(self.application_context))


class ZafMetadata(object):
    """
    Gathers metadata about the Zaf Application and creates an object structure representing the information.

    The metadata classes are wrappers around the actual data objects and all attributes of the wrapped object
    are available through the wrapper. Wrappers are only used when it's needed to add more information.

    The metadata objects contains references to the actual data objects and
    the metadata object are looked up on demand.
    """

    def __init__(
            self, all_extensions, all_components, config, application_name, extension_manager,
            metadata_filter):
        self._all_extensions = sorted(all_extensions, key=lambda e: e.name)
        self._all_components = sorted(all_components, key=lambda c: c.name)
        self._config = config
        self._application_name = application_name
        self._extension_manager = extension_manager
        self._metadata_filter = metadata_filter if metadata_filter else MetadataFilter()

        self._extension_classes = None
        self._extension_names = None
        self._extensions = None

        self._commands = None
        self._config_option_ids = None
        self._option_id_to_wrapped_option_id_mapping = None
        self._components = None

        self._initialize()

    def _initialize(self):
        self._init_extension_classes()
        self._init_commands()
        self._init_config_option_ids()
        self._init_components()
        self._init_endpoints_and_messages()
        self._init_extensions()

    def _init_extension_classes(self):
        """
        Initialize the extension class metadata objects.

        MetadataFilter is used to filter out out extension classes that shouldn't
        be included in the metadata.

        The extension classes will only contain commands and config option ids that
        are not filtered out by the metadata filter.
        """
        self._extension_classes = OrderedDict(
            [
                (
                    ext_class,
                    ExtensionClassMetadata(
                        self,
                        ext_class,
                        [
                            config_option.option_id
                            for config_option in sorted(
                                ext_class.config_options, key=lambda c: c.option_id.key)
                            if self._metadata_filter.include_config_option_id(
                                config_option.option_id)
                        ],
                        [
                            command for command in sorted(ext_class.commands, key=lambda c: c.name)
                            if self._metadata_filter.include_command(command)
                        ],
                        sorted(ext_class.endpoints_and_messages.keys(), key=lambda e: e.name),
                        [
                            message
                            for endpoint in ext_class.endpoints_and_messages.keys()
                            for message in sorted(
                                ext_class.endpoints_and_messages[endpoint], key=lambda e: e.name)
                        ],
                    )) for ext_class in self._all_extensions
                if self._metadata_filter.include_extension_class(ext_class)
            ])

    def _init_commands(self):
        """
        Initialize the command metadata objects.

        Commands are only included if the belong to an extension class that
        is included in the metadata and they are not filtered out by the
        MetadataFilter.

        The commands will only contain config option ids that
        are not filtered out by the metadata filter.
        """
        framework_config_option_ids = {
            config_option.option_id
            for ext_class in self._extension_manager.framework_extensions(only_enabled=False)
            if ext_class in self._extension_classes for config_option in ext_class.config_options
            if self._metadata_filter.include_config_option_id(config_option.option_id)
        }

        root_command = CommandId(
            self._application_name,
            'The {application} root command.'.format(application=self._application_name),
            None, [])
        commands = OrderedDict(
            [
                (
                    root_command,
                    CommandMetadata(
                        self, root_command, None, root_command, [], [],
                        framework_config_option_ids))
            ])

        for command, defining_ext_class in sorted(
            ((command, ext_class) for ext_class in self._extension_classes.keys()
             for command in ext_class.commands
             if self._metadata_filter.include_command(command)), key=lambda t: t[0].name):

            config_option_ids = [
                config_option.option_id for config_option in command.config_options
                if self._metadata_filter.include_config_option_id(config_option.option_id)
            ]

            ext_classes = [
                ext_class
                for ext_class in self._extension_manager.command_extensions(
                    command, only_enabled=False) if ext_class in self._extension_classes
            ]
            extension_config_option_ids = set()
            for ext_class in ext_classes:
                extension_config_option_ids.update(
                    [
                        config_option.option_id for config_option in ext_class.config_options
                        if self._metadata_filter.include_config_option_id(config_option.option_id)
                    ])

            commands[command] = CommandMetadata(
                self, command, defining_ext_class, root_command, ext_classes, config_option_ids,
                sorted(extension_config_option_ids, key=lambda c: c.key))

        self._commands = commands

    def _init_config_option_ids(self):
        """
        Initialize the config option id metadata objects.

        Config option ids are only included if the belong to an extension class or
        a command that is included in the metadata and they are not filtered out by the
        metadata filter.
        """

        config_option_ids = set()
        option_id_to_commands = defaultdict(set)
        for command in self._commands.values():
            for option_id in command._config_option_ids:
                config_option_ids.add(option_id)
                option_id_to_commands[option_id].add(command._wrapped)

            for option_id in command._extension_config_option_ids:
                option_id_to_commands[option_id].add(command._wrapped)

        option_id_to_extension_classes = defaultdict(set)
        for ext_class in self._extension_classes.values():
            for option_id in ext_class._config_option_ids:
                config_option_ids.add(option_id)
                option_id_to_extension_classes[option_id].add(ext_class._wrapped)

        self._config_option_ids = OrderedDict(
            [
                (
                    option_id,
                    ConfigOptionIdMetadata(
                        self, option_id, self._config, option_id_to_extension_classes[option_id],
                        option_id_to_commands[option_id]))
                for option_id in sorted(config_option_ids, key=lambda c: c.key)
                if self._metadata_filter.include_config_option_id(option_id)
            ])

    def _init_components(self):
        self._components = sorted(
            (
                ComponentMetadata(self, component_info, component_info.extension)
                for component_info in self._all_components),
            key=lambda c: c.name)

    def _init_endpoints_and_messages(self):
        endpoints_and_messages = defaultdict(list)
        endpoint_extensions = defaultdict(set)
        messages_and_endpoints = defaultdict(list)
        message_extensions = defaultdict(set)

        endpoint_message_extension_tuple = [
            (endpoint_id, message_id, extension_class)
            for extension_class in self._extension_classes
            for endpoint_id, message_ids in extension_class.endpoints_and_messages.items()
            for message_id in message_ids
        ]

        for endpoint_id, message_id, extension_class in endpoint_message_extension_tuple:
            endpoints_and_messages[endpoint_id].append(message_id)
            endpoint_extensions[endpoint_id].add(extension_class)
            messages_and_endpoints[message_id].append(endpoint_id)
            message_extensions[message_id].add(extension_class)

        self._endpoints = OrderedDict(
            [
                (
                    endpoint_id,
                    EndpointMetadata(
                        self, endpoint_id, sorted(message_ids, key=lambda m: m.name),
                        sorted(endpoint_extensions[endpoint_id], key=lambda e: e.name)))
                for endpoint_id, message_ids in sorted(
                    endpoints_and_messages.items(), key=lambda t: t[0].name)
            ])

        self._messages = OrderedDict(
            [
                (
                    message_id,
                    MessageMetadata(
                        self, message_id, sorted(endpoint_ids, key=lambda e: e.name),
                        sorted(message_extensions[message_id], key=lambda e: e.name)))
                for message_id, endpoint_ids in sorted(
                    messages_and_endpoints.items(), key=lambda t: t[0].name)
            ])

    def _init_extensions(self):
        self._extensions = OrderedDict()
        for name in sorted({ext_class.name for ext_class in self._extension_classes.values()}):
            extension_classes_for_name = [
                ext_class for ext_class in self._extension_classes.values()
                if ext_class.name == name
            ]

            groups = sorted(
                {group
                 for ext_class in extension_classes_for_name for group in ext_class.groups})

            self._extensions[name] = ExtensionMetadata(
                self, name, groups, extension_classes_for_name)

        for extension in self._extensions.values():
            extension.initialize()

    def metadata_option_id(self, option_id):
        return self._config_option_ids[option_id]

    def metadata_command(self, command):
        return self._commands[command]

    def metadata_extension_class(self, ext_class):
        return self._extension_classes[ext_class]

    def metadata_endpoint(self, endpoint):
        return self._endpoints[endpoint]

    def metadata_message(self, message):
        return self._messages[message]

    @property
    def extension_classes(self):
        """
        List of all extension classes of type ExtensionClassMetadata.

        :return: list of extension classes
        """
        return list(self._extension_classes.values())

    @property
    def extension_names(self):
        """
        List of of all extension names.

        :return: list of extension names
        """
        return sorted({ext_class.name for ext_class in self._extension_classes.values()})

    @property
    def extensions(self):
        """
        List of all extensions of type ExtensionMetadata.

        :return: list of extensions
        """
        return list(self._extensions.values())

    @property
    def commands(self):
        """
        List of all commands of type CommandMetadata.

        :return: list of commands
        """
        return list(self._commands.values())

    @property
    def config_option_ids(self):
        """
        List of all config option ids of type ConfigOptionIDMetadata.

        :return: list of config option ids
        """
        return list(self._config_option_ids.values())

    @property
    def components(self):
        """
        List of all components of type ComponentMetadata.

        :return: list of components
        """
        return self._components

    @property
    def endpoints(self):
        """
        List of all endpoints of type EndpointMetadata.

        :return: list of endpoints
        """
        return list(self._endpoints.values())

    @property
    def messages(self):
        """
        List of all messages of type MessageMetadata.

        :return: list of messages
        """
        return list(self._messages.values())

    def extension_with_name(self, name):
        """
        Get the extension, of type ExtensionMetadata, with the name.

        :param name: the name of the extension
        :return: the extension
        """
        return self._extensions[name]

    def extensions_with_group(self, group):
        """
        Get a list of extension names that are part of a group.

        :param group: the group
        :return: list of extension names
        """
        return [extension for extension in self.extensions if group in extension.groups]


class ExtensionMetadata(object):

    def __init__(self, metadata, name, groups, extension_classes):
        self._metadata = metadata
        self._name = name
        self._groups = groups
        self._extension_classes = extension_classes

        self._description = None
        self._short_description = None
        self._components = None
        self._endpoints = None
        self._messages = None

    def initialize(self):
        self._initialize_description()
        self._initalize_components()
        self._initialize_group_members()

    def _initialize_description(self):
        modules = {ext_class.module for ext_class in self._extension_classes}
        description = dedent(
            '\n\n'.join(
                [
                    mod.__doc__.strip() for mod in modules
                    if mod.__doc__ is not None and mod.__doc__ != ''
                ]))

        if description:
            self._description = description
        else:
            self._description = 'No description'
        self._short_description = self.description.split('\n\n')[0].strip()

    def _initalize_components(self):
        self._components = [
            component for component in self._metadata.components
            if component.extension_name == self._name
        ]

    def _initialize_group_members(self):
        self._group_members = OrderedDict()
        for group in self._groups:
            self._group_members[group] = sorted(
                extension.name for extension in self._metadata.extensions_with_group(group)
                if extension.name != self._name)

    @property
    def extension_classes(self):
        """
        List of extension classes, of type ExtensionClassMetadata, that are part of this extension.

        :return: list of extension classes
        """
        return self._extension_classes

    @property
    def name(self):
        """
        Name of the extension.

        :return: the name
        """
        return self._name

    @property
    def description(self):
        """
        Return the string description for the extension.

        :return: the description
        """
        return self._description

    @property
    def components(self):
        """
        List of components, of type ComponentMetadata, that are part of the extension.

        :return: list of components
        """
        return self._components

    @property
    def commands(self):
        """
        List of commands, of type CommandMetadata, that are defined by this extension.

        :return:
        """
        return sorted(
            (command for ext_class in self._extension_classes for command in ext_class.commands),
            key=lambda c: c.name)

    @property
    def config_option_ids(self):
        """
        List of the config option ids, of type ConfigOptionIdMetadata, for this extension.

        :return: list of config option ids
        """
        return sorted(
            (
                option_id
                for ext_class in self._extension_classes
                for option_id in ext_class.config_option_ids),
            key=lambda o: o.key)

    @property
    def endpoints(self):
        """
        List of endpoints, of type EndpointMetadata, defined for this extension.

        :return: list of endpoints
        """
        return [
            endpoint for ext_class in self._extension_classes for endpoint in ext_class.endpoints
        ]

    @property
    def messages(self):
        """
        List of messages, of type MessageMetadata, defined for this extension.

        :return: list of messages
        """
        return sorted(
            (message for ext_class in self._extension_classes for message in ext_class.messages),
            key=lambda m: m.name)

    def group_members(self, group):
        """
        List of extension names of group members of the specified group excluding the name of this extension.

        :param group: the group
        :return: list of extension names
        """
        return self._group_members[group]

    @property
    def groups(self):
        """
        List the names of the groups that this extension is part of.

        :return: list of group names
        """
        return self._groups

    @property
    def short_description(self):
        """
        Short description of the extension. This is a part of the full description.

        :return: short description
        """
        return self._short_description


class MetadataWrapper(object):
    """
    Class used to wrap objects.

    Gives access to all the attributes of the wrapped object while also being
    able to provide additional attributes and methods.

    This expects the subclasses to have a description field.
    """

    def __init__(self, metadata, wrapped):
        self._metadata = metadata
        self._wrapped = wrapped

    def __getattr__(self, attr):
        return getattr(self._wrapped, attr)

    @property
    def short_description(self):
        """
        Short description of the wrapped object.

        :return: short description
        """
        return dedent(self.description.split('\n\n')[0]).strip()

    def __eq__(self, other):
        if hasattr(other, '_wrapped'):
            return self._wrapped == other._wrapped
        else:
            return other == self._wrapped

    def __hash__(self):
        return hash(self._wrapped)

    def __repr__(self):
        return repr(self._wrapped)


class ExtensionClassMetadata(MetadataWrapper):
    """Wrapper around Extension classes."""

    def __init__(self, metadata, extension_class, config_option_ids, commands, endpoints, messages):
        super().__init__(metadata, extension_class)
        self._extension_class = extension_class
        self._config_option_ids = config_option_ids
        self._commands = commands
        self._endpoints = endpoints
        self._messages = messages

    @property
    def class_name(self):
        """
        Name of the wrapped extension class.

        :return: class name
        """
        return self._extension_class.__name__

    @property
    def module(self):
        """
        Return the module that the extension class is defined in.

        :return: module object
        """
        return inspect.getmodule(self._extension_class)

    @property
    def config_option_ids(self):
        return [
            self._metadata.metadata_option_id(option_id) for option_id in self._config_option_ids
        ]

    @property
    def commands(self):
        return [self._metadata.metadata_command(command) for command in self._commands]

    @property
    def endpoints(self):
        return [self._metadata.metadata_endpoint(endpoint) for endpoint in self._endpoints]

    @property
    def messages(self):
        return [self._metadata.metadata_message(message) for message in self._messages]

    @property
    def description(self):
        return dedent(
            self._extension_class.__doc__
            if self._extension_class.__doc__ else 'No description').strip()


class CommandMetadata(MetadataWrapper):
    """Wrapper around a CommandId."""

    def __init__(
            self, metadata, command, extension_class, root_command, extension_classes,
            config_option_ids, extension_config_option_ids):
        super().__init__(metadata, command)
        self._command = command
        self._extension_class = extension_class
        self._root_command = root_command
        self._extension_classes = extension_classes
        self._config_option_ids = config_option_ids
        self._extension_config_option_ids = extension_config_option_ids

    @property
    def name(self):
        """Return the name of the command including parent command names."""
        command = self._command
        parts = [command.name]
        while command.parent is not None:
            parts.append(command.parent.name)
            command = command.parent

        if self._command != self._root_command:
            parts.append(self._root_command.name)
        return ' '.join(reversed(parts))

    @property
    def short_name(self):
        """Return the short name of the command."""
        return self._command.name

    @property
    def description(self):
        return '\n'.join(line for line in self._command.description.split('\n') if '\b' not in line)

    @property
    def extension_class(self):
        """
        Extension class that this command is defined by.

        :return: extension class or None
        """
        if self._extension_class is None:
            return None
        else:
            return self._metadata.metadata_extension_class(self._extension_class)

    @property
    def extension_name(self):
        """
        Name of the extension that defines this command.

        :return: extension name or None
        """
        if self._extension_class is None:
            return None
        else:
            return self._extension_class.name

    @property
    def extension_names(self):
        """Names of the extensions that extend this command."""
        return sorted({ext_class.name for ext_class in self._extension_classes})

    @property
    def config_option_ids(self):
        """
        List of config option ids, of type ConfigOptionIdMetadata, of the options needed by the command.

        :return:
        """
        return [
            self._metadata.metadata_option_id(option_id) for option_id in self._config_option_ids
        ]

    @property
    def extension_config_option_ids(self):
        """
        List of config option ids, of type ConfigOptionIdMetadata, of the options added by extensions.

        :return:
        """
        return [
            self._metadata.metadata_option_id(option_id)
            for option_id in self._extension_config_option_ids
        ]


class ConfigOptionIdMetadata(MetadataWrapper):
    """Wrapper around ConfigOptionId."""

    FIX_SPHINX_FORMATTING_REGEX = re.compile(r'([@])')

    def __init__(self, metadata, option_id, config, extension_classes, commands):
        super().__init__(metadata, option_id)
        self._option_id = option_id
        self._config = config
        self._extension_classes = extension_classes
        self._commands = commands

    @property
    def type_string(self):
        """
        Format the type of the options dealing with both zaf types and primitive types.

        :return: string representation of the type
        """
        if hasattr(self._option_id.type, 'is_zaf_type'):
            return self._option_id.type.doc_string(self._config)
        else:
            return self._option_id.type.__name__

    @property
    def description(self):
        """
        Return the description of the option.

        :return: description
        """
        return self._option_id.description

    @property
    def extension_classes(self):
        """
        Extensions that use this option.

        :return: list of extension names
        """
        return [
            self._metadata.metadata_extension_class(ext_class)
            for ext_class in self._extension_classes
        ]

    @property
    def extension_names(self):
        """Names of the extensions that uses this option."""
        return sorted({ext_class.name for ext_class in self._extension_classes})

    @property
    def commands(self):
        """
        Return the commands that use this option.

        :return: list of commands
        """
        return [self._metadata.metadata_command(command) for command in self._commands]

    @property
    def command_names(self):
        """
        Return the names of the commands that use this option.

        :return: list of commands
        """
        return sorted({command.name for command in self.commands})

    @property
    def cli(self):
        """
        Return a string of the concatenated cli options.

        :return: string with the concatenated cli options
        """

        entity_name = None
        if self._option_id.at is not None:
            entity_name = '<{id}>'.format(id=self._option_id.at.name.rstrip('s'))
        _, options = self._option_id.cli_options(entity_name)
        return ', '.join(
            self.FIX_SPHINX_FORMATTING_REGEX.sub(r'\\\1', option) for option in options)


class ComponentMetadata(MetadataWrapper):
    """Wrapper around ComponentInfo."""

    def __init__(self, metadata, component_info, extension_name=None):
        super().__init__(metadata, component_info)
        self._component_info = component_info
        self._extension_name = extension_name

    @property
    def extension_name(self):
        """
        Name of the extension that this component is provided by.

        :return: extension name
        """
        return self._extension_name

    @property
    def description(self):
        """
        Return the description of the component.

        :return: description
        """
        return self.doc

    @property
    def name(self):
        """
        Return the formatted name of the component.

        This is used to deduplicate components registered with the same name.

        :return: name
        """
        if self._component_info.name.lower() == self.callable_name.lower():
            return self._component_info.name
        else:
            return '{name}({callable})'.format(
                name=self._component_info.name, callable=self.callable_name)

    @property
    def methods(self):
        """
        List of public methods, of type ComponentMethodMetadata, on this component.

        :return:  list of methods
        """
        return [
            ComponentMethodMetadata(self._metadata, self._component_info.callable, method)
            for method in self._component_info.methods
        ]


class ComponentMethodMetadata(MetadataWrapper):
    """Wrapper around Method."""

    def __init__(self, metadata, component, method):
        super().__init__(metadata, method)
        self._component = component
        self._method = method

    @property
    def path(self):
        """
        Return the path to the function.

        :return: name
        """
        return '{module}.{cls}.{name}'.format(
            module=self._component.__module__,
            cls=self._component.__name__,
            name=self._method.__name__)

    @property
    def description(self):
        """
        Return the description of the method.

        :return: description
        """
        return dedent(self._method.__doc__ if self._method.__doc__ else 'No description').strip()


class EndpointMetadata(MetadataWrapper):
    """Wrapper around EndpointId."""

    def __init__(self, metadata, endpoint_id, messages, extension_classes):
        super().__init__(metadata, endpoint_id)
        self._endpoint_id = endpoint_id
        self._messages = messages
        self._extension_classes = extension_classes

    @property
    def endpoint_id(self):
        """
        Get access to the wrapped endpoint id.

        :return: endpoint id
        """
        return self._endpoint_id

    @property
    def messages(self):
        """
        List of messages, of type MessageMetadata, connected to this endpoint.

        :return: list of messages
        """
        return [self._metadata.metadata_message(message) for message in self._messages]

    @property
    def extension_names(self):
        return sorted({ext_class.name for ext_class in self._extension_classes})


class MessageMetadata(MetadataWrapper):
    """Wrapper around MessageId."""

    def __init__(self, metadata, message_id, endpoints, extension_classes):
        super().__init__(metadata, message_id)
        self._message_id = message_id
        self._endpoints = endpoints
        self._extension_classes = extension_classes

    @property
    def message_id(self):
        """
        Get access to the wrapped message id.

        :return: message id
        """
        return self._message_id

    @property
    def endpoints(self):
        """
        List of endpoints that this message is defined for.

        :return: list of endpoints
        """
        return [self._metadata.metadata_endpoint(endpoint) for endpoint in self._endpoints]

    @property
    def extension_names(self):
        return sorted({ext_class.name for ext_class in self._extension_classes})
