import logging
import re
from collections import defaultdict

from zaf.config.typechecker import ConfigOptionIdTypeChecker

from .values import ConfigValueHolder

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class InvalidReference(Exception):
    pass


class InvalidValue(Exception):
    pass


class ConfigView(object):

    def __init__(self, manager, option_ids, entity_option, entity):
        super().__init__()
        self._manager = manager
        self._option_ids = option_ids
        self._entity_option = entity_option
        self._entity = entity

    def get(self, option_id, default=None, entity=None, additional_options={}):
        if option_id not in self._option_ids:
            raise KeyError(
                'The requested option_id ({name}) does not exist.'.format(name=option_id.name))
        elif option_id == self._entity_option:
            return self._entity
        elif option_id.at is not None and option_id.at == self._entity_option:
            return self._manager.get(
                option_id, default, entity=self._entity, additional_options=additional_options)
        else:
            return self._manager.get(option_id, default, entity, additional_options)

    def __contains__(self, option_id):
        if option_id not in self._option_ids:
            return False

        if option_id.at is not None and option_id.at == self._entity_option:
            return self.get(option_id, entity=self._entity) is not None
        elif option_id.at is not None:
            for entity in self.get(option_id.at):
                if self.get(option_id, entity=entity) is not None:
                    return True
            return False
        else:
            return self.get(option_id, ) is not None


class ConfigManager(object):

    def __init__(self):
        self._config = defaultdict(ConfigValueHolder)
        self._type_checker = ConfigOptionIdTypeChecker(self)

    def set_default_values(self, option_ids):
        """
        Set all default values in the config to the default value in the option_ids.

        The default priority is set to 0 so that all new values override the default.

        :param option_ids: The option_ids
        """
        independent_option_ids = [option_id for option_id in option_ids if option_id.at is None]
        dependent_option_ids = [option_id for option_id in option_ids if option_id.at is not None]

        def set_defaults(option_ids):
            for option_id in [option_id for option_id in option_ids if option_id.has_default]:
                if option_id.at is not None:
                    entities = self.get(option_id.at)
                    for entity in entities:
                        if not self._option_key(option_id, entity) in self._config:
                            self.set(option_id, option_id.default, 0, 'default', entity)
                else:
                    if not self._option_key(option_id) in self._config:
                        self.set(option_id, option_id.default, 0, 'default')

        set_defaults(independent_option_ids)
        set_defaults(dependent_option_ids)

    def update_config(self, config, priority, source):
        """
        Update this config manager with values from the config dict.

        All values will be given the priority and source if they have higher
        priority than the current values.

        :param config: a dict with config values to add to the config manager
        :param priority: the priority of the new values
        :param source: the source of the new values

        """
        for key, value in config.items():
            self._config[key].add(value, priority, source)

    def filter_config(self, option_ids, entity_option=None, entity=None):
        """
        Create a filtered view of the config with only the specified option_ids.

        If entity_option and entity is given then config options that related to
        the entity will be converted to only include that entity.

        :param option_ids: list of option IDs that should be part of the filtered config
        :param entity_option: the option ID that defines the entity
        :param entity: the entity value to match against
        :return: a filtered view of the config
        """
        return ConfigView(self, option_ids, entity_option, entity)

    def get(self, option_id, default=None, entity=None, additional_options={}, transform=True):
        """
        Get the value for the specified option_id.

        First looks in the additonal options and then in the config.
        If no value for the option_id is found then the default value is returned

        :param option_id: the option_id to get the config value for
        :param default: the default value if option_id doens't exist in the config
        :param entity: the entity that should be used to look up the config value.
                       Only applicable for option_ids that depend on an entity with the at-specifier
        :param additional_options: Additional options that isn't included in the config but should have higher
                                   priority than the config.

        :return: the config value
        """
        key = self._option_key(option_id, entity)

        if key in additional_options:
            value = additional_options.get(key)
        elif key in self._config:
            holder = self._config[key]
            if option_id.multiple:
                value = holder.get_combined(option_id.default)
            else:
                value = holder.get_highest_priority().value
        elif default is not None:
            value = default
        else:
            value = option_id.default
            # If someone asks for an option that we didn't know about then we add the default value
            # to the config so that it can be logged and printed
            self.set_default_values([option_id])

        return_value = value
        if transform and option_id.transform is not None:
            return_value = option_id.transform(value)

        try:
            return self._expand_value(return_value, multiple=option_id.multiple)
        except RuntimeError:
            raise InvalidValue(
                'Circular reference found when evaluating config value for {key}'.format(key=key))

    def _raw_get(self, raw_key, default=None):
        """
        Get the value using a raw string key.

        :param raw_key: A string representing the internal storage in the config
        :return: the value from the config or default if raw_key does not exist
        """
        try:
            if raw_key in self._config:
                holder = self._config[raw_key]
                if holder.is_multiple():
                    return self._expand_value(holder.get_combined(default), multiple=True)
                else:
                    return self._expand_value(holder.get_highest_priority().value)
            else:
                return self._expand_value(default)
        except RuntimeError:
            raise InvalidValue(
                'Circular reference found when evaluating config value for {key}'.format(
                    key=raw_key))

    def _expand_value(self, value, multiple=False):
        """
        Expand the value by recursively expanding all the references in the value.

        This only works on string or multiple strings values and if a non string value is referenced
        it will be converted to string.

        :param value: the value
        :param multiple: If the value is a multiple
        :return: value with all references expanded
        :raises: RuntimeError if there is a cyclic dependency between values
        """
        if multiple:
            return tuple(self._expand_value(item) for item in value)
        elif isinstance(value, str):
            expanded_value = value
            for match in re.finditer(r'\${([\w\d.]+)}', value):
                key = match.group(1)
                substring = '${{{key}}}'.format(key=key)

                if key in self._config:
                    expanded_value = value.replace(substring, str(self._raw_get(key)))
                else:
                    msg = 'Error expanding value {value}. No value found for reference {ref}'.format(
                        value=value, ref=key)
                    raise InvalidReference(msg)

            return expanded_value
        else:
            return value

    def set(self, option_id, value, priority=1, source='unknown', entity=None):
        """
        Set the value for option_id with priority and source.

        Entity is required if the option_id.at is specified

        :param option_id: the option_id
        :param value: the new value
        :param priority: the priority of the value
        :param source: the source of the value
        :param entity: the entity to set the value for (if option_id.at is specified)
        """
        self._type_checker.assert_type(option_id, value, entity=entity)
        key = self._option_key(option_id, entity)
        self._config[key].add(value, priority, source)

    def _option_key(self, option_id, entity=None):
        """
        Calculate the internal key from the option_id and entity.

        :param option_id: the option_id
        :param entity: the entity to use if option_id.at is specified
        :return: internal key representation
        """
        parts = [] if option_id.namespace is None else [option_id.namespace]
        if option_id.at is not None:
            if entity is None:
                raise ValueError(
                    'Error reading entity config option {option} without entity'.format(
                        option=option_id.name))
            parts.append(re.sub(r'[_-]', '.', entity))
        parts.append(re.sub(r'[_-]', '.', option_id.name))
        return '.'.join(parts)

    def print_config(self, options=()):
        """
        Print config to stdout.

        If options are provided, only named config options are printed.
        Otherwise, the options specified are printed.
        """
        if len(options) == 0:
            options_to_print = sorted(self._config.keys())
        else:
            options_to_print = options

        for key in options_to_print:
            if key in self._config:
                config_value = self._config[key].get_highest_priority()
                actual_value = self._raw_get(key)  # for multiple this is a combined value
                print(
                    '{key}: {value}  -  prio: {priority}, source: {source}'.format(
                        key=key,
                        value=actual_value,
                        priority=config_value.priority,
                        source=config_value.source))

    def log_config(self, level=logging.DEBUG):
        """Log the config. Used for debugging."""
        for key in sorted(self._config.keys()):
            if key in self._config:
                config_value = self._config[key].get_highest_priority()
                actual_value = self._raw_get(key)  # for multiple this is a combined value
                logger.log(
                    level, '{key}: {value}  -  prio: {priority}, source: {source}'.format(
                        key=key,
                        value=actual_value,
                        priority=config_value.priority,
                        source=config_value.source))
