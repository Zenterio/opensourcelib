from collections import namedtuple

ConfigValue = namedtuple('ConfigValue', ['value', 'priority', 'source'])


class ConfigValueHolder(object):

    def __init__(self):
        self.items = []

    def add(self, value, priority, source):
        if isinstance(value, set) or isinstance(value, list):
            value = tuple(value)
        self.items.append(ConfigValue(value, priority, source))

    def get_highest_priority(self):
        """
        Get the highest priority value.

        If multiple items share highest priority then the first added item will be returned.

        :return: The highest priority ConfigValueItem
        """
        return sorted(self.items, key=lambda value: value.priority, reverse=True)[0]

    def get_combined(self, default=None):
        """
        Combine lists of values of multiple priorities into a combined list.

        This is only allowed when is_multiple is True.
        The returned values are sorted in priority order with highest priority first.
        If multiple values have the same priority the first added item will be placed earlier in the result.

        :param default: Default values that should be included in combined
        :return: list of values
        """
        return_values = []
        config_values = sorted(self.items, key=lambda value: value.priority, reverse=True)
        for config_value in config_values:
            for value in config_value.value:
                if value not in return_values:
                    return_values.append(value)
        for default_value in [] if not default else list(default):
            if default_value not in return_values:
                return_values.append(default_value)
        return return_values

    def is_multiple(self):
        return isinstance(self.items[0].value, tuple)
