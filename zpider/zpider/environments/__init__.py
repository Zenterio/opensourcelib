from zaf.config.options import ConfigOptionId
from zaf.config.types import Choice, Flag


class RunException(Exception):
    pass


ENV = ConfigOptionId(
    'env',
    'Select the environment to run shell commands in',
    option_type=Choice(['docker', 'host']),
    default='docker')

ROOT = ConfigOptionId(
    'root', 'Run as the root user inside the Docker environment.', option_type=Flag())
