import abc
import glob
import os


class Type(metaclass=abc.ABCMeta):
    is_zaf_type = True


class Path(Type):
    """
    Config option type for representing paths in the file system.

    This is represented as a string value on both command line and in config files.
    """

    def __init__(self, exists=False):
        """
        Define a new Path option type.

        :param exists: If the path should exist
        """
        self.exists = exists

    def __call__(self, string, key=None):
        check_type('Path', string, str, key=None)

        if self.exists and not os.path.exists(string):
            raise TypeError(
                "Path '{path}'{key} does not exist".format(
                    key='' if key is None else " for '{key}'".format(key=key), path=string))
        return string

    def doc_string(self, config):
        return 'Path(exists={exists})'.format(exists=self.exists)


class Choice(Type):
    """
    Config option type for representing a set of valid choices for the option.

    This only supports string values as options.
    """

    def __init__(self, choices):
        """
        Define a new Choice option type.

        :param choices: list of valid choices
        """
        self.choices = choices

    def __call__(self, string, key=None):
        check_type('Choice', string, str, key)

        if string not in self.choices:
            raise TypeError(
                "'{choice}' is not a valid Choice{key}, expected '{expected}'".format(
                    key='' if key is None else " for '{key}'".format(key=key),
                    choice=string,
                    expected=', '.join(self.choices)))
        return string

    def doc_string(self, config):
        return 'Choice([{choices}])'.format(choices=', '.join(self.choices))


class ConfigChoice(Type):
    """
    Config option type for representing a set of valid choices for the option.

    Similar to choice but the set of valid options is configurable through another
    config option with multiple values.
    """

    wants_config = True

    def __init__(self, option_id):
        """
        Define a new ConfigChoice option type.

        :param option_id: ConfigOptionId specifying multiple choices
        """
        if not option_id.multiple:
            raise ValueError('ConfigChoice is only valid for option IDs with multiple=True')

        self.option_id = option_id

    def choices(self, config):
        return config.get(self.option_id)

    def __call__(self, string, config, key=None):
        check_type('ConfigChoice', string, str, key)

        expected = config.get(self.option_id)
        if string not in expected:
            raise TypeError(
                "'{choice}' is not a valid ConfigChoice{key}, expected '{expected}'".format(
                    key='' if key is None else " for '{key}'".format(key=key),
                    choice=string,
                    expected=', '.join(expected)))
        return string

    def doc_string(self, config):
        return 'ConfigChoice([{choices}])'.format(choices=', '.join(self.choices(config)))


class GlobPattern(Type):
    """
    Config option type for representing a glob pattern.

    This is represented as a string value on both command line and in config files.
    """

    def __init__(self, exists_match=False):
        """
        Define a new GlobPattern option type.

        :param exists_match: If True, verify that the pattern has at least one match
        """
        self._exists_match = exists_match

    def __call__(self, string, key=None):
        check_type('GlobPattern', string, str, key)

        if self._exists_match is True and not glob.glob(string):
            raise TypeError(
                "GlobPattern{key} with pattern '{pattern}' doesn't match any file.".format(
                    key=" '{key}'".format(key=key) if key is not None else '', pattern=string))
        return string

    def doc_string(self, config):
        return 'GlobPattern(exists_match={exists_match})'.format(exists_match=self._exists_match)


class Flag(Type):
    """
    Config option type for representing a simple flag.

    On command line this is represented as *--option* and *--no-option* flags that doesn't take any value.
    Depending on the default value and values from config files both of them are necessary.

    In config files this is represented as a simple boolean value.
    """

    def __call__(self, boolean, key=None):
        check_type('Flag', boolean, bool, key)
        return boolean

    def doc_string(self, config):
        return 'Flag'


class Count(Type):
    """
    Counts the number of times the option is given.

    This can be used for example for an increasing verbosity option
    *--verbose (-v)* that counts the times it is given.
    For example *-vvv* would give verbosity=3.

    Due to how this gets interpreted on command line it's not possible
    to override a non zero config file value on command line.

    In config files this is represented as a simple int value.
    """

    def __init__(self, min=0, max=2):
        self.min = min
        self.max = max

    def __call__(self, integer, key=None):
        check_type('Count', integer, int, key)
        if integer < self.min or integer > self.max:
            raise TypeError(
                "'{integer}' is not a valid Count{key}, expected '{expected}'".format(
                    key='' if key is None else " for '{key}'".format(key=key),
                    integer=integer,
                    expected='[{min}, {max}]'.format(min=self.min, max=self.max)))
        return integer

    def doc_string(self, config):
        return 'Count([{min}, {max}])'.format(min=self.min, max=self.max)


class Entity(Type):
    """Config option type for representing an entity."""

    def __call__(self, string, key=None):
        check_type('Entity', string, str, key)

        for delimiter in ('-', '_'):
            if delimiter in string:
                raise TypeError(
                    "'{entity}' is not a valid Entity {key}, entity names must not contain '{delimiter}'".
                    format(entity=string, key=key, delimiter=delimiter))

        if not string.lower() == string:
            raise TypeError(
                "'{entity}' is not a valid Entity {key}, entity names must be lower case.".format(
                    entity=string, key=key))

        return string

    def doc_string(self, config):
        return 'Entity'

    def __eq__(self, other):
        return isinstance(other, Entity)

    def __hash__(self):
        return hash(Entity)


def check_builtin_type(actual_value, expected_type, key):
    if type(actual_value) != expected_type and not (type(actual_value) == int
                                                    and expected_type == float):
        raise TypeError(
            "Option '{key}' has unexpected type '{actual}', expected '{expected}'".format(
                key=key, actual=type(actual_value).__name__, expected=expected_type.__name__))


def check_type(name, actual_value, expected_type, key=None):
    actual_type = type(actual_value)
    if actual_type != expected_type:
        raise TypeError(
            "{name}{key} has value '{actual}' of unexpected type '{actual_type}', expected '{expected}'".
            format(
                name=name,
                key=" '{key}'".format(key=key) if key is not None else '',
                actual=actual_value,
                actual_type=actual_type.__name__,
                expected=expected_type.__name__))
