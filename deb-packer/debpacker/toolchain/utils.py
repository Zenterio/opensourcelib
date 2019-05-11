import logging
import os
from collections import namedtuple

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

DEFAULT_VERSION = '1.0.0'
DEFAULT_TOOLCHAIN_ROOT = ''


class GetToolchainException(Exception):
    pass


def get_template_path(name):
    return os.path.join(os.path.dirname(__file__), 'templates', name)


ToolchainLink = namedtuple('ToolchainLink', ['src', 'dst'])
