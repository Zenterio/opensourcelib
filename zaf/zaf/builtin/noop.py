"""Provides the *noop* (no operation) command."""

import logging

from zaf.application import ApplicationContext
from zaf.commands.command import CommandId
from zaf.extensions.extension import AbstractExtension, FrameworkExtension, get_logger_name

logger = logging.getLogger(get_logger_name('zaf', 'noop'))
logger.addHandler(logging.NullHandler())


def noop(core):
    """Noop (no operation) command. Does nothing. Takes no arguments."""
    return 0


NOOP_COMMAND = CommandId(
    'noop', noop.__doc__, noop, [], hidden=True, application_contexts=ApplicationContext.EXTENDABLE)


@FrameworkExtension(name='noop', commands=[NOOP_COMMAND])
class NoopExtension(AbstractExtension):
    """Provides the noop (no operation) command."""

    def __init__(self, config, instances):
        pass
