"""Provides the *noop* (no operation) command."""

import logging

from zaf.commands.command import CommandId
from zaf.extensions.extension import AbstractExtension, FrameworkExtension, get_logger_name

logger = logging.getLogger(get_logger_name('k2', 'noop'))
logger.addHandler(logging.NullHandler())


def noop(core):
    """Noop (no operation) command. Does nothing. Takes no arguments."""


NOOP_COMMAND = CommandId('noop', noop.__doc__, noop, [])


@FrameworkExtension(name='noop', commands=[NOOP_COMMAND])
class NoopCommand(AbstractExtension):
    """Provides the noop (no operation) command."""

    def __init__(self, config, instances):
        pass
