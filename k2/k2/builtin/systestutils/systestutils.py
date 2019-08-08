"""Utilities for using K2 for systests of other tools."""

import logging

from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name

from k2.cmd.run import RUN_COMMAND

from .remoteclient import SystestRemoteClient  # noqa
from .workspace import CallableWorkspace, TestWorkspace  # noqa

logger = logging.getLogger(get_logger_name('k2', 'systestutils'))
logger.addHandler(logging.NullHandler())


@CommandExtension(
    name='systestutils',
    extends=[RUN_COMMAND],
    config_options=[],
    endpoints_and_messages={},
    default_enabled=False,
)
class SystestUtils(AbstractExtension):
    """Utilities for using K2 for systests of other tools."""

    def __init__(self, config, instances):
        pass
