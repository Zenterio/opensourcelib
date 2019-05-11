"""
Provides ProcessRunner component for dealing with subprocesses.

Started processes are represented by Process objects.

.. autoclass:: k2.builtin.proc.processrunner.Process
       :members: __init__, wait, write_stdin, wait_for_match_in_stdout, wait_for_match_in_stderr, kill, signal
"""

import logging

from zaf.extensions.extension import AbstractExtension, FrameworkExtension, get_logger_name

from .processrunner import ProcessRunner  # noqa

logger = logging.getLogger(get_logger_name('k2', 'proc'))
logger.addHandler(logging.NullHandler())


@FrameworkExtension(name='proc', config_options=[], endpoints_and_messages={})
class Proc(AbstractExtension):
    """Dummy extension class used to register ProcessRunner component."""

    def __init__(self, config, instances):
        pass
