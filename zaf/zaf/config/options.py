import re
from collections import defaultdict, namedtuple
from textwrap import dedent

from zaf.config.types import Count

from .types import Choice, ConfigChoice, Entity, Flag, GlobPattern, Path

InternalConfigOption = namedtuple('ConfigOption', ['option_id', 'required', 'instantiate_on'])

InternalConfigOptionId = namedtuple(
    'InternalConfigOptionId', [
        'name', 'description', 'type', 'multiple', 'default', 'transform', 'at', 'entity',
        'namespace', 'argument', 'hidden', 'application_contexts', 'short_alias', 'short_name'
    ])


class OptionsWithSameName(Exception):
    pass


class ConfigOption(InternalConfigOption):
    __slots__ = ()

    def __new__(cls, option_id, required, instantiate_on=False):
        """
        Create a new instance of a config option.

        :param option_id: the ConfigOptionId that defines this option
        :param required: if a value for this options is required or not
        :param instantiate_on: if this should be used to instantiate the extension
        :return:
        """
        return super().__new__(cls, option_id, required, instantiate_on)


class ConfigOptionId(InternalConfigOptionId):
    """
    Identifier for a Config Option.

    This can be reused by multiple extensions to register need for config options.
    """

    __slots__ = ()

    def __new__(
            cls,
            name,
            description,
            option_type=str,
            multiple=False,
            default=None,
            transform=None,
            at=None,
            entity=False,
            namespace=None,
            argument=False,
            hidden=False,
            application_contexts=None,
            short_alias=False,
            short_name=False,
    ):
        """
        Define a new ConfigOptionId.

        :param name: the name of the option
        :param description: description of the option
        :param option_type: the type of the option. One of [str, int, float, bool, .types.Flag, .types.Path,
                            .types.Choice]
        :param multiple: if the option represents a list of multiple values
        :param default: default value
        :param transform: function to transform the config value
        :param at: ConfigOptionId of an entity option that this should be connected to
        :param entity: specifies if values of this option are entities that can affect other options
        :param namespace: the namespace in the config for this option. Can not be combined with 'at'
        :param argument: Can be used for command options to turn them into arguments instead of options
        :param hidden: Hide the config option from the normal help.
        :param application_contexts: One or more ApplicationContexts that this option should be available
                                     for. If not given then this option will be applicable for all contexts.
        :param short_alias: Create a short command line alias by removing the namespace.
                            This should be used with care to not cause name collisions on command line.
        :param short_name: A configurable short name that will be used with a single dash on command line.
                            This should most often be a single letter.
                            This will cause collisions on command line if not used with care.
        :return: new ConfigOptionId
        """

        if option_type not in [str, int, float, bool] and type(option_type) not in [
                Path, Choice, ConfigChoice, GlobPattern, Flag, Count, Entity
        ]:
            raise ValueError('Invalid type for config option with name {name}'.format(name=name))

        if entity is True:
            if option_type != str and type(option_type) != Entity:
                raise ValueError(
                    "Option '{name}' is an entity and must have an option of type Entity".format(
                        name=name))
            else:
                option_type = Entity()

        if at is not None and namespace is not None:
            raise ValueError("Namespace is not valid when using 'at'. Namespace will be inherited")

        if at is not None and entity:
            raise ValueError("Only one of 'at' and 'entity' are allowed for a config option")

        if at is not None and not at.entity:
            raise ValueError('Can only use at towards entity options')

        if at is not None:
            namespace = at.namespace

        if multiple and default is None:
            default = ()

        if isinstance(default, list):
            default = tuple(default)

        from zaf.application.context import ApplicationContext
        if application_contexts is None:
            application_contexts = ()
        elif isinstance(application_contexts, ApplicationContext):
            application_contexts = (application_contexts, )
        else:
            application_contexts = tuple(application_contexts)

        return super().__new__(
            cls, name,
            dedent(description).strip(), option_type, multiple, default, transform, at, entity,
            namespace, argument, hidden, application_contexts, short_alias, short_name)

    @property
    def has_default(self):
        """
        Return bool telling if the id has a default value specified.

        :return: True if default value is specified
        """

        return self.default is not None and not (self.multiple and len(self.default) == 0)

    @property
    def key(self):
        """
        Return a string representation of the key defined by the id. This doesn't use the config.

        and instead replaces dependencies on entity options with at using <entity> syntax.
        :return: a string representation of the id
        """

        return self._recursively_create_key(self)

    def _recursively_create_key(self, option_id, at=False):
        parts = []

        if option_id.at:
            parts.append(self._recursively_create_key(option_id.at, at=True))
        elif option_id.namespace:
            parts.append(option_id.namespace)

        if option_id.entity and at:
            parts.append('<{name}>'.format(name=option_id.name))
        else:
            parts.append(option_id.name)

        return '.'.join(parts)

    @property
    def include(self):
        if self.entity:
            return ConfigOptionId(
                'include.files',
                "Include options from files into '{id}'".format(
                    id=self._recursively_create_key(self, at=True)),
                at=self,
                multiple=True,
                hidden=True,
                application_contexts=self.application_contexts)
        else:
            return None

    def is_applicable_for_application(self, application_context):
        return not self.application_contexts or application_context in self.application_contexts

    def cli_options(self, entity_name=None):
        name = self.name if entity_name is None else '@'.join([entity_name, self.name])

        full_name = name
        if self.namespace:
            full_name = '.'.join([self.namespace, name])

        if self.argument:
            return full_name, ('{name}'.format(name=re.sub(r'[_.]', '-', full_name)), )
        else:

            is_flag = type(self.type) == Flag

            def option_string(name):
                cli_formatted = re.sub(r'[_.]', '-', name)
                if is_flag:
                    return '--{name}/--no-{name}'.format(name=cli_formatted)
                else:
                    return '--{name}'.format(name=cli_formatted)

            option_strings = []
            if self.short_name:
                option_strings.append('-{short_name}'.format(short_name=self.short_name))

            option_strings.append(option_string(full_name))

            if name != full_name and self.short_alias:
                option_strings.append(option_string(name))

            return full_name, tuple(option_strings)


def handle_duplicate_config_options(config_options):
    """
    Handle config options with the same option_id by merging them.

    :param config_options: list of config options
    :return: list of merged config options
    """
    combined_config_options = []

    def get_option_id(option):
        return option.option_id

    grouped_config_options = defaultdict(list)
    for option in config_options:
        grouped_config_options[option.option_id].append(option)

    for option_id, config_options_with_id in grouped_config_options.items():
        config_options_with_id = list(config_options_with_id)
        combined_config_options.append(_combine_options_with_same_id(config_options_with_id))
    return combined_config_options


def _combine_options_with_same_id(config_options):
    option = config_options[0]

    for other_option in config_options[1:]:
        option = option if option.required else other_option

    return option
