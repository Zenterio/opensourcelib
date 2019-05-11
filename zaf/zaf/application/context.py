from enum import Enum, unique


@unique
class ApplicationContext(Enum):
    """
    Used to match commands and config options to different kinds of applications.

    Internal should only used on commands and config options to indicate that it is
    not valid to configure from the outside.

    Extendable means that the application supports extensions and that commands and
    config options related to extendability should be available.

    Standalone means that the application is complete without extensions so any commands
    and config options related to extendability should not be available.
    """
    INTERNAL = 0
    EXTENDABLE = 1
    STANDALONE = 2
