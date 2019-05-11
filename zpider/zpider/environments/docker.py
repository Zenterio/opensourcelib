import logging
import os

from zaf.component.decorator import component
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, FrameworkExtension, get_logger_name

from zpider.data import zpider_package_dir
from zpider.environments import ENV, ROOT
from zpider.environments.host import HostEnv

logger = logging.getLogger(get_logger_name('zpider', 'dockerenv'))
logger.addHandler(logging.NullHandler())


class DockerEnv(object):

    root = False

    def __init__(self):
        self._host_env = HostEnv()

    def run(self, command, host_paths=None):
        """
        Run the command in using Docker.

        :param command: The command to run
        :param host_paths: Paths on the host that are needed inside the docker container
        """
        cwd = os.getcwd()
        mounts = [
            '--mount', 'type=bind,source={cwd},target={cwd}'.format(cwd=cwd), '--mount',
            'type=bind,source={zpider_package_dir},target={zpider_package_dir}'.format(
                zpider_package_dir=zpider_package_dir())
        ]
        for mount in [] if host_paths is None else host_paths:
            mounts.extend(
                [
                    '--mount',
                    'type=bind,source={path},target={path}'.format(path=mount),
                ])

        workdir = '--workdir {cwd}'.format(cwd=cwd)

        command_line = (
            'docker run {mount_flags} {user_flags} {workdir} '
            '--rm docker.zenterio.lan/zenterio/zpider:latest {command}').format(
                mount_flags=' '.join(mounts),
                user_flags=self._get_docker_user_flags(),
                workdir=workdir,
                command=command)

        return self._host_env.run(command_line)

    def _get_docker_user_flags(self):
        if self.root:
            return ''
        flags = [
            '--mount',
            'type=bind,source=/etc/group,target=/etc/group,readonly',
            '--mount',
            'type=bind,source=/etc/passwd,target=/etc/passwd,readonly',
            '--user',
            '{uid}:{gid}'.format(uid=os.getuid(), gid=os.getgid()),
        ]
        return ' '.join(flags)


@FrameworkExtension(
    name='dockerenv',
    config_options=[ConfigOption(ENV, required=True),
                    ConfigOption(ROOT, required=False)])
class DockerEnvExtension(AbstractExtension):

    def __init__(self, config, instances):
        self._env = config.get(ENV)
        self._root = config.get(ROOT, False)

    def register_components(self, component_manager):
        if self._env == 'docker':
            DockerEnv.root = self._root
            component(name='Env', scope='session')(DockerEnv, component_manager=component_manager)
