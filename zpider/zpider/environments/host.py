import logging
import subprocess
import sys

from zaf.component.decorator import component
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, FrameworkExtension, get_logger_name

from zpider.environments import ENV, RunException

logger = logging.getLogger(get_logger_name('zpider', 'hostenv'))
logger.addHandler(logging.NullHandler())


class HostEnv(object):
    """A host variant of the DockerEnv."""

    def run(self, command, host_paths=None):
        logger.info('Running command: {command}'.format(command=command))
        result = subprocess.Popen(
            command, stdout=sys.stdout, stderr=sys.stderr, shell=True, universal_newlines=True)
        result.wait()

        if result.returncode == 0:
            logger.debug('Done running command: {command}'.format(command=command))
        else:
            msg = 'Failed running command: {command}'.format(command=command)
            logger.debug(msg)
            raise RunException(msg)


@FrameworkExtension(name='hostenv', config_options=[ConfigOption(ENV, required=True)])
class HostEnvExtension(AbstractExtension):

    def __init__(self, config, instances):
        self._env = config.get(ENV)

    def register_components(self, component_manager):
        if self._env == 'host':
            component(name='Env', scope='session')(HostEnv, component_manager=component_manager)
