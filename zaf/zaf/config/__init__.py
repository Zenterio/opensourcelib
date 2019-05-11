class ConfigException(Exception):
    pass


class MissingConditionalConfigOption(ConfigException):
    pass


class MutuallyExclusiveConfigOptions(ConfigException):
    pass
