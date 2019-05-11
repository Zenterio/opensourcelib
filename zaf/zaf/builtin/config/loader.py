"""
Provides the functionality to load configuration from `YAML <https://en.wikipedia.org/wiki/YAML>`_ files.

The format is just *key: value* where the key is a dot separated string and the value is
the YAML representation of any of the available config types.

Example of the format:

.. code-block:: yaml

    system.config.enabled: true
    system.config.file.pattern: /path/to/config/file
    config.file.pattern: /path/to/configs/*
    list.of.items: [item1, item2]
    value.for.entity.item1: 23
    value.for.entity.item2: 9.2
"""
import abc
import glob
import itertools
import logging
import os

import ruamel.yaml
import voluptuous
import voluptuous.humanize

from zaf.application import ApplicationContext
from zaf.config.options import ConfigOption, ConfigOptionId, GlobPattern
from zaf.config.types import Flag
from zaf.extensions.extension import AbstractExtension, ExtensionConfig, FrameworkExtension
from zaf.utils.bashcompletion import is_bash_completion

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class ConfigLoaderError(Exception):
    pass


CONFIG_GLOB_PATTERN = ConfigOptionId(
    'config.file.pattern',
    'Load config from specific files matching this glob pattern',
    multiple=True,
    option_type=GlobPattern(exists_match=True))

ADDITIONAL_CONFIG_GLOB_PATTERN = ConfigOptionId(
    'additional.config.file.pattern',
    'Load additional configuration from files matching this glob pattern',
    multiple=True,
    option_type=GlobPattern(exists_match=True))

SYSTEM_CONFIG_GLOB_PATTERN_ENABLED = ConfigOptionId(
    'system.config.enabled',
    'Should the system configuration be loaded',
    default=True,
    option_type=bool,
    hidden=True,
    application_contexts=ApplicationContext.EXTENDABLE)

SYSTEM_CONFIG_GLOB_PATTERN = ConfigOptionId(
    'system.config.file.pattern',
    'Load system configuration from files matching this glob pattern',
    default='/etc/${application.name}/config',
    option_type=GlobPattern(exists_match=False),
    hidden=True,
    application_contexts=ApplicationContext.EXTENDABLE)

USER_CONFIG_GLOB_PATTERN_ENABLED = ConfigOptionId(
    'user.config.enabled',
    'Should the user configuration be loaded',
    default=True,
    option_type=bool,
    hidden=True,
    application_contexts=ApplicationContext.EXTENDABLE)

USER_CONFIG_GLOB_PATTERN = ConfigOptionId(
    'user.config.file.pattern',
    'Load user configuration from files matching this glob pattern',
    default=os.path.join(os.path.expanduser('~'), '.${application.name}config'),
    option_type=GlobPattern(exists_match=False),
    hidden=True,
    application_contexts=ApplicationContext.EXTENDABLE)

LOCAL_CONFIG_GLOB_PATTERN_ENABLED = ConfigOptionId(
    'local.config.enabled',
    'Should the local configuration be loaded',
    default=True,
    option_type=bool,
    hidden=True,
    application_contexts=ApplicationContext.EXTENDABLE)

LOCAL_CONFIG_GLOB_PATTERN = ConfigOptionId(
    'local.config.file.pattern',
    'Load local configuration from files matching this glob pattern',
    default='./${application.name}config',
    option_type=GlobPattern(exists_match=False),
    hidden=True,
    application_contexts=ApplicationContext.EXTENDABLE)

DISABLE_DEFAULT_CONFIG_FILES = ConfigOptionId(
    'disable.default.config.files',
    'Do not load configuration from default configuration files (System, User and Local)',
    default=False,
    option_type=Flag(),
    hidden=True,
    application_contexts=ApplicationContext.EXTENDABLE)


class FileConfigLoader(AbstractExtension):
    """Loads config from file."""

    def __init__(self, config=None, instances=None):
        self.config = {} if config is None else config
        self.config_file_glob_patterns = []
        self.default_config = {}

    def get_config(self, config, requested_config_options, requested_command_config_options):

        def _glob(pattern):
            return glob.glob(pattern)

        extension_configs = [ExtensionConfig(self.default_config, priority=self.priority)]
        for path in itertools.chain(*list(map(_glob, self.config_file_glob_patterns))):
            if os.path.isdir(path) and is_bash_completion():
                logger.debug(
                    "Directory found during bash completion. Skipping path '{path}'".format(
                        path=path))
            else:
                extension_configs.extend(_recursively_load_configuration(path, self.priority))

        return extension_configs


@FrameworkExtension(
    name='fileconfig',
    load_order=2,
    config_options=[ConfigOption(CONFIG_GLOB_PATTERN, required=False)],
    groups=['config'])
class ExplicitFileConfigLoader(FileConfigLoader):
    """Loads config files that will replace existing config files."""

    def __init__(self, config=None, instances=None):
        super().__init__(config, instances)
        self.priority = 50
        if self.config.get(CONFIG_GLOB_PATTERN):
            self.default_config[SYSTEM_CONFIG_GLOB_PATTERN_ENABLED.name] = False
            self.default_config[LOCAL_CONFIG_GLOB_PATTERN_ENABLED.name] = False
            self.default_config[USER_CONFIG_GLOB_PATTERN_ENABLED.name] = False
            self.config_file_glob_patterns = self.config.get(CONFIG_GLOB_PATTERN)


@FrameworkExtension(
    name='fileconfig',
    load_order=2,
    config_options=[ConfigOption(DISABLE_DEFAULT_CONFIG_FILES, required=False)],
    groups=['config'])
class DisableDefaultConfigFileLoader(FileConfigLoader):
    """Disables loading of default config files."""

    def __init__(self, config=None, instances=None):
        super().__init__(config, instances)
        self.priority = 50
        if self.config.get(DISABLE_DEFAULT_CONFIG_FILES):
            self.default_config[SYSTEM_CONFIG_GLOB_PATTERN_ENABLED.name] = False
            self.default_config[LOCAL_CONFIG_GLOB_PATTERN_ENABLED.name] = False
            self.default_config[USER_CONFIG_GLOB_PATTERN_ENABLED.name] = False


@FrameworkExtension(
    name='fileconfig',
    load_order=3,
    config_options=[ConfigOption(ADDITIONAL_CONFIG_GLOB_PATTERN, required=False)],
    groups=['config'])
class AdditionalFileConfigLoader(FileConfigLoader):
    """Load config files that are in addition to existing config files."""

    def __init__(self, config=None, instances=None):
        super().__init__(config, instances)
        self.priority = 40
        self.config_file_glob_patterns = self.config.get(ADDITIONAL_CONFIG_GLOB_PATTERN)


@FrameworkExtension(
    name='fileconfig',
    load_order=4,
    config_options=[
        ConfigOption(SYSTEM_CONFIG_GLOB_PATTERN_ENABLED, required=True),
        ConfigOption(SYSTEM_CONFIG_GLOB_PATTERN, required=True)
    ],
    groups=['config'])
class SystemFileConfigLoader(FileConfigLoader):
    """Load system config files."""

    def __init__(self, config=None, instances=None):
        super().__init__(config, instances)
        self.priority = 10
        if self.config.get(SYSTEM_CONFIG_GLOB_PATTERN_ENABLED) is True:
            self.config_file_glob_patterns = [self.config.get(SYSTEM_CONFIG_GLOB_PATTERN)]


@FrameworkExtension(
    name='fileconfig',
    load_order=6,
    config_options=[
        ConfigOption(USER_CONFIG_GLOB_PATTERN_ENABLED, required=True),
        ConfigOption(USER_CONFIG_GLOB_PATTERN, required=True)
    ],
    groups=['config'])
class UserFileConfigLoader(FileConfigLoader):
    """Load user config files."""

    def __init__(self, config=None, instances=None):
        super().__init__(config, instances)
        self.priority = 20
        if self.config.get(USER_CONFIG_GLOB_PATTERN_ENABLED) is True:
            self.config_file_glob_patterns = [self.config.get(USER_CONFIG_GLOB_PATTERN)]


@FrameworkExtension(
    name='fileconfig',
    load_order=8,
    config_options=[
        ConfigOption(LOCAL_CONFIG_GLOB_PATTERN_ENABLED, required=True),
        ConfigOption(LOCAL_CONFIG_GLOB_PATTERN, required=True)
    ],
    groups=['config'])
class LocalFileConfigLoader(FileConfigLoader):
    """Load local config files."""

    def __init__(self, config=None, instances=None):
        super().__init__(config, instances)
        self.priority = 30
        if self.config.get(LOCAL_CONFIG_GLOB_PATTERN_ENABLED) is True:
            self.config_file_glob_patterns = [self.config.get(LOCAL_CONFIG_GLOB_PATTERN)]


class EntityIncludeLoader(AbstractExtension, metaclass=abc.ABCMeta):
    """Base class for loading entity include files."""

    def __init__(self, config=None, instances=None):
        self.priority = 90

    @abc.abstractmethod
    def select_config_options(self, requested_config_options, requested_command_config_options):
        """Use to be able to run get_config for different sets of config options."""
        return None

    def get_config(self, config, requested_config_options, requested_command_config_options):
        extension_configs = []

        config_options = self.select_config_options(
            requested_config_options, requested_command_config_options)
        unique_ids = {option.option_id for option in config_options if option.option_id.entity}

        for option_id in unique_ids:
            entities = config.get(option_id)
            for entity in entities:
                extension_configs.extend(
                    _load_entity_include(
                        '{namespace}.{entity}'.format(namespace=option_id.namespace, entity=entity),
                        config.get(option_id.include, entity=entity), self.priority))
        return extension_configs


@FrameworkExtension(name='fileconfig', load_order=22, config_options=[], groups=['config'])
class EntityMainIncludeConfigLoader(EntityIncludeLoader):
    """Load entity include files for main config options."""

    def __init__(self, config=None, instances=None):
        super().__init__(config, instances)

    def select_config_options(self, requested_config_options, requested_command_config_options):
        return requested_config_options


@FrameworkExtension(name='fileconfig', load_order=91, config_options=[], groups=['config'])
class EntityCommandIncludeConfigLoader(EntityIncludeLoader):
    """Load entity include files for command config options."""

    def __init__(self, config=None, instances=None):
        super().__init__(config, instances)

    def select_config_options(self, requested_config_options, requested_command_config_options):
        """Combine the command config options from all commands."""
        return [
            option
            for command_options in requested_command_config_options.values()
            for option in command_options
        ]


def _recursively_load_configuration(path, priority, parent_path=None):
    extension_configs = []
    try:
        config = _load_yaml_configuration(path)
        _validate_configuration(config)
    except FileNotFoundError as e:
        parent_string = ", included from file '{parent_path}',".format(
            parent_path=parent_path) if parent_path else ''
        raise FileNotFoundError(
            "File '{included_file}'{parent} was not found.".format(
                included_file=path, parent=parent_string)) from e
    except ConfigLoaderError as e:
        e.args = (e.args[0] + ' (source: {path})'.format(path=path), )
        raise

    extension_configs.append(ExtensionConfig(config, priority=priority, source=path))

    if 'include.files' in config:
        for include_path in config['include.files']:
            include_path = _ensure_absolute_path(include_path, path)
            extension_configs.extend(
                _recursively_load_configuration(include_path, priority - 1, path))

        # Should not be included in config because this is not a valid config option
        del config['include.files']

    entity_include_keys_to_be_deleted = []
    for key in config.keys():
        if key.endswith('.include.files'):
            entity_include_keys_to_be_deleted.append(key)
            entity = key.split('.include.files')[0]
            include_files = [_ensure_absolute_path(x, path) for x in config[key]]
            extension_configs.extend(_load_entity_include(entity, include_files, priority, path))

    # Should not be included in config because these are already loaded and
    # if they are kept they might be loaded again by entity include extensions.
    for key in entity_include_keys_to_be_deleted:
        del config[key]

    return extension_configs


def _ensure_absolute_path(include_path, path):
    if not include_path.startswith('/'):
        include_path = os.path.join(os.path.dirname(path), include_path)
    return include_path


def _load_entity_include(entity_prefix, included_files, priority, parent_path=None):
    """Load include files for the and prefixes all keys with entity prefix."""
    extension_configs = []
    for entity_include_path in included_files:
        entity_configs = _recursively_load_configuration(
            entity_include_path, priority - 1, parent_path)

        for entity_config in entity_configs:
            updated_config = {}
            for entity_key, entity_value in entity_config.config.items():
                updated_config['{entity_prefix}.{entity_key}'.format(
                    entity_prefix=entity_prefix, entity_key=entity_key)] = entity_value
                extension_configs.append(
                    ExtensionConfig(updated_config, entity_config.priority, entity_config.source))

    return extension_configs


def _load_yaml_configuration(path):
    """
    Load configuration from a YAML file.

    Raises FileNotFoundError if the file can not be found.
    Raises ConfigLoaderError on other errors.

    Returns a dictionary containing the configuration.
    """
    try:
        yaml = ruamel.yaml.YAML()
        with open(path, 'r') as f:
            result = yaml.load(f)
            return result if result is not None else {}
    except FileNotFoundError:
        raise
    except Exception as e:
        logger.debug('Error occurred when loading YAML config file:', exc_info=True)
        raise ConfigLoaderError(str(e))


def _validate_configuration(data):
    """
    Attempt to validate some configuration data.

    The data is assumed to be a dictionary where the keys are strings and the
    values are either integers, booleans, strings or lists.

    Raises a ConfigLoaderError if the validation fails.
    """

    schema = voluptuous.Schema(
        {
            str: voluptuous.validators.Any(int, bool, float, str, [int, float, bool, str])
        })
    exception = None
    try:
        schema(data)
    except Exception as e:
        exception = ConfigLoaderError(voluptuous.humanize.humanize_error(data, e))
    if exception is not None:
        raise exception
