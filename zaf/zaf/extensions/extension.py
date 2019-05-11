import abc
import inspect
from collections import namedtuple
from enum import Enum
from textwrap import dedent

InternalExtensionId = namedtuple('InternalExtensionId', ['name', 'description', 'extension_class'])


class ExtensionId(InternalExtensionId):
    __slots__ = ()
    """
    Define a new ExtensionId.

    :param name: the name of the extension
    :param description: description of the extension
    :return: new ExtensionId
    """

    def __new__(cls, name, description, extension_class):
        return super().__new__(cls, name, dedent(description), extension_class)


def FrameworkExtension(
        name,
        load_order=50,
        config_options=None,
        commands=None,
        endpoints_and_messages=None,
        groups=None,
        default_enabled=True,
        activate_on=None,
        deactivate_on=None,
        replaces=None):
    """
    Decorate an extension with this to create framework extensions.

    :param name: the name of the extension
    :param load_order: the load order of the extension.
    :param config_options: the requested config options for the extension
    :param commands: the commands created by the extension
    :param endpoints_and_messages: the endpoints and messages defined by this extension
    :param groups: the groups that the extension belongs to
    :param default_enabled: should this extension be enabled by default
    :param activate_on: List of config options that all needs to be truthy for this
                        extension to be activated (and). Tuples of config options
                        can be specified within the list to specify that one or
                        more options in the tuple is enough (or).
    :param deactivate_on: List of config options that if all are truthy the
                        extension will be deactivated/not activated (and).
                        Tuples of config options can be specified within the
                        list to specify that one or more options in the tuple is enough (or).
                        `deactivate_on` has precedence over `activate_on`.
    :param replaces: List of extension names that this extension replaces.
                     When this extension is enabled, extensions on this list
                     will be disabled.
    :return: A wrapper that makes a class into a FrameworkExtension
    """

    def wrapped_extension(extension):
        extension._is_zaf_extension = True
        extension.name = name
        extension.extension_id = ExtensionId(
            name, extension.__doc__ if extension.__doc__ else '', extension)
        extension.extension_type = ExtensionType.FRAMEWORK
        extension.load_order = load_order
        extension.config_options = config_options if config_options else []
        extension.commands = commands if commands else []
        extension.endpoints_and_messages = endpoints_and_messages if endpoints_and_messages else {}
        extension.groups = groups if groups else []
        extension.default_enabled = default_enabled
        extension.activate_on = activate_on if activate_on else []
        extension.deactivate_on = deactivate_on if deactivate_on else []
        extension.replaces = replaces if replaces else []
        return extension

    return wrapped_extension


def CommandExtension(
        name,
        config_options=None,
        extends=None,
        endpoints_and_messages=None,
        groups=None,
        default_enabled=True,
        activate_on=None,
        deactivate_on=None,
        replaces=None):
    """
    Decorate an extension with this to create command extensions.

    :param name: the name of the extension
    :param config_options: the requested config options for the extension
    :param extends: the command that this extension extends
    :param endpoints_and_messages: the endpoints and messages defined by this extension
    :param groups: the groups that the extension belongs to
    :param default_enabled: should this extension be enabled by default
    :param activate_on: List of config options that all needs to be truthy for this
                        extension to be activated (and). Tuples of config options
                        can be specified within the list to specify that one or
                        more options in the tuple is enough (or).
    :param deactivate_on: List of config options that if all are truthy the
                        extension will be deactivated/not activated (and).
                        Tuples of config options can be specified within the
                        list to specify that one or more options in the tuple is enough (or).
                        `deactivate_on` has precedence over `activate_on`.
    :param replaces: List of extension names that this extension replaces.
                     When this extension is enabled, extensions on this list
                     will be disabled.
    :return: A wrapper that makes a class into a CommandExtension
    """

    def wrapped_extension(extension):
        extension._is_zaf_extension = True
        extension.name = name
        extension.extension_id = ExtensionId(
            name, extension.__doc__ if extension.__doc__ else '', extension)
        extension.extension_type = ExtensionType.COMMAND
        extension.load_order = 1000
        extension.config_options = config_options if config_options else []
        extension.extends = extends if extends else []
        extension.endpoints_and_messages = endpoints_and_messages if endpoints_and_messages else {}
        extension.groups = groups if groups else []
        extension.default_enabled = default_enabled
        extension.commands = []  # To not have to ask if an extension has commands attr
        extension.default_enabled = default_enabled
        extension.activate_on = activate_on if activate_on else []
        extension.deactivate_on = deactivate_on if deactivate_on else []
        extension.replaces = replaces if replaces else []
        return extension

    return wrapped_extension


class ExtensionType(Enum):
    FRAMEWORK = 1
    COMMAND = 2


class ExtensionConfig(namedtuple('InternalExtensionConfig', ['config', 'priority', 'source'])):
    __slots__ = ()

    def __new__(cls, config, priority, source=None):
        """
        Create a new extension config instance.

        :param config: the config
        :param priority: the priority of the config
        :param source: the source name for the config
        :return: ExtensionConfig instance
        """
        return super().__new__(cls, config, priority, source)


class AbstractExtension(metaclass=abc.ABCMeta):

    def __init__(self, config=None, instances=None):
        pass

    def get_config(self, config, requested_config_options, requested_command_config_options):
        """
        Get the config from the extension.

        :param config: the already loaded config
        :param requested_config_options: the config options for the main command that are known at this time
        :param requested_command_config_options: the config options for each command that are known at this time
        :return: an ExtensionConfig instance or a list of ExtensionConfig instances, containing
                 updates to be made to the config
        """
        return ExtensionConfig({}, priority=0)

    def register_components(self, component_manager):
        pass

    def register_dispatchers(self, messagebus):
        pass

    def destroy(self):
        pass


def is_concrete_extension(object):
    if inspect.isabstract(object):
        return False
    if hasattr(object, '_is_zaf_extension'):
        return object._is_zaf_extension
    return False


def get_logger_name(name, extension, *args):
    return '.'.join([name, 'extension', extension] + list(args))
