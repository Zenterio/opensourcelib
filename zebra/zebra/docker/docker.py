import getpass
import grp
import logging
import os
import subprocess
from collections import OrderedDict, namedtuple
from textwrap import dedent

from zaf.component.decorator import component, requires

from zebra.docker.run import execute_capture, execute_interactive, run_docker_run
from zebra.docker.util import is_interactive

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class DockerGroupException(Exception):
    pass


class DockerImageException(Exception):
    pass


ImageInfo = namedtuple('ImageInfo', ['config', 'description'])
ImageConfig = namedtuple('ImageConfig', ['directory', 'make_command'])
default_config = ImageConfig('zenterio', make_command='zmake')

# first member is used as default value
IMAGES = OrderedDict(
    [
        (
            '<image_name>',
            ImageInfo(
                default_config,
                dedent(
                    """\
            Long description of the image
            """)))
    ])

FORWARDED_ENVIRONMENT_VARIABLES = [
    'LANG=en_US.UTF-8',
    'LC_ALL=en_US.UTF-8',
    'CCACHE_SIZE',
    'CCACHE_DIR',
    'CCACHE_MAXSIZE',
    'CCACHE_NOHASHDIR',
    'MAKEFLAGS',
]


@component(name='DockerRun')
@requires(docker_config='DockerConfig')
class DockerRun(object):

    def __init__(self, docker_config):
        self._docker_config = docker_config

    @property
    def docker_config(self):
        return self._docker_config

    def run_in_docker_with_capture(self, command_with_arguments):
        """
        Run the command and capture all output in the specified docker container.

        The name of the docker image is <registry>/<image>:<tag>.
        If no_registry is specified then <registry>/ will not be included.

        This captures

        :param config: The DockerConfig object
        :param command_with_arguments: The command to run and the arguments to the command
        :return: (exit_code, stdout, stderr) tuple
        """
        return _internal_run_in_docker(
            self._docker_config, command_with_arguments, execute_capture, forward_signals=False)

    def run_in_docker(self, command_with_arguments, forward_signals=True):
        """
        Run the command interactively in the specified docker container.

        The name of the docker image is <registry>/<image>:<tag>.
        If no_registry is specified then <registry>/ will not be included.

        This opens a completely interactive subprocess that forwards
        stdin, stdout and stderr.

        :param config: The DockerConfig object
        :param command_with_arguments: The command to run and the arguments to the command
        :param forward_signals: Forward signals to the docker container. Otherwise they will be handled
                                by the DockerSignalHandler to give a good default behavior.
        :return: exit code from the docker command
        """
        return _internal_run_in_docker(
            self._docker_config, command_with_arguments, execute_interactive, forward_signals)


def _internal_run_in_docker(config, command_with_arguments, execute, forward_signals):
    """
    Run the command in docker with a custom execute function.

    Internal implementation of run in docker that can take a special
    implementation of the execute function.

    :return: Returns the output from the run function
    """

    docker_run_command = determine_docker_run()
    docker_pull_command = determine_docker_pull()

    if docker_run_command == 'docker' and docker_pull_command == 'docker':
        assert_user_in_docker_group_or_sudo()

    if config.image_override is not None:
        image_name = config.image_override
    else:
        image_name = '{dir}/{short_name}'.format(
            dir=IMAGES[config.image].config.directory, short_name=config.image)

    if not config.no_registry:
        image_name = '{registry}/{image}'.format(registry=config.registry, image=image_name)

    image = '{image}:{tag}'.format(image=image_name, tag=config.tag)
    logger.debug('Using image {image}'.format(image=image))

    root_dir, rel_project_dir, rel_cwd = determine_root_and_rel_project_dir_and_relative_cwd(
        config.root_dir, config.project_dir)
    logger.debug(
        (
            'Root directory is {root_dir}, relative project dir is {rel_project_dir} '
            'and relative current working directory is {rel_cwd}').format(
                root_dir=root_dir, rel_project_dir=rel_project_dir, rel_cwd=rel_cwd))

    docker_rel_project_dir = determine_docker_rel_project_dir(rel_project_dir, config)

    docker_workdir = os.path.join(config.container_root_dir, docker_rel_project_dir, rel_cwd)
    logger.debug(
        'Inside Docker container root directory is {root_dir} and current working directory is {cwd}'.
        format(root_dir=config.container_root_dir, cwd=docker_workdir))
    home = os.path.expanduser('~')
    logger.debug('Home directory is {home}'.format(home=home))

    docker_flags = determine_docker_flags(
        root_dir, config.container_root_dir, rel_project_dir, docker_rel_project_dir, home,
        config.env_variables, config.mounts, config.root, config.hostname, config.network)

    if not config.no_pull:
        run_docker_pull(docker_pull_command, image, config.registry, config.registry_cache)

    return run_docker_run(
        docker_run_command, image, docker_flags, docker_workdir, command_with_arguments, execute,
        forward_signals)


def run_docker_pull(docker_command, image, registry, registry_cache):
    image_to_pull = image
    if registry is not None and registry_cache is not None:
        image_to_pull = image.replace(registry, registry_cache)

    pull_command = [docker_command, 'pull', image_to_pull]
    logger.debug(
        'Trying to pull image using command: {command}'.format(command=' '.join(pull_command)))

    logger.info('Pulling image {image}. This might take a while.'.format(image=image_to_pull))
    result = subprocess.Popen(
        pull_command,
        shell=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True)

    result.wait()
    for line in result.stdout.read().split('\n'):
        logger.debug(line)

    if result.returncode != 0:
        logger.warning('Failed to pull image {image}'.format(image=image_to_pull))
        for line in result.stderr.read().split('\n'):
            logger.warning(line)

        logger.info('Checking if image {image} is found locally'.format(image=image))
        if not docker_image_exists_locally(docker_command, image):
            raise DockerImageException(
                'Failed to pull image {image} and not found locally'.format(image=image))
    else:
        if image != image_to_pull:
            logger.info(
                'Renaming cached image {cached_image} to {image}.'.format(
                    cached_image=image_to_pull, image=image))
            _docker_tag(determine_docker_tag(), image_to_pull, image)


def _docker_tag(docker_command, cached_image, image):
    tag_command = [docker_command, 'tag', cached_image, image]

    result = subprocess.Popen(
        tag_command,
        shell=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True)

    result.wait()
    for line in result.stdout.read().split('\n'):
        logger.debug(line)

    if result.returncode != 0:
        logger.warning(
            'Failed to tag image {name} as {new_name}'.format(name=cached_image, new_name=image))
        for line in result.stderr.read().split('\n'):
            logger.warning(line)

        raise DockerImageException(
            'Failed to tag image {name} as {new_name}'.format(name=cached_image, new_name=image))


def assert_user_in_docker_group_or_sudo():
    if getpass.getuser() != 'root' and 'docker' not in [grp.getgrgid(gid)[0]
                                                        for gid in os.getgroups()]:
        raise DockerGroupException(
            "Docker commands are only allowed for 'root' or users that are members of the 'docker' group. "
            "Add user to the docker group with 'sudo adduser <user> docker'.")


def determine_docker_run():
    override = os.getenv('OVERRIDE_RUN')
    if override is not None:
        logger.info('Overriding docker run with {command}'.format(command=override))
        return override
    else:
        return '/usr/bin/docker'


def determine_docker_pull():
    override = os.getenv('OVERRIDE_PULL')
    if override is not None:
        logger.info('Overriding docker pull with {command}'.format(command=override))
        return override
    else:
        return '/usr/bin/docker'


def determine_docker_tag():
    override = os.getenv('OVERRIDE_TAG')
    if override is not None:
        logger.info('Overriding docker tag with {command}'.format(command=override))
        return override
    else:
        return '/usr/bin/docker'


def determine_user_and_group():
    return os.getuid(), os.getgid()


def determine_docker_flags(
        root_dir,
        docker_root_dir,
        rel_project_dir,
        docker_rel_project_dir,
        home,
        env_variables,
        additonal_mounts=None,
        run_as_root=False,
        hostname=None,
        network=None):

    flags = [
        '--mount',
        'type=bind,source={root_dir},target={docker_root_dir}'.format(
            root_dir=root_dir, docker_root_dir=docker_root_dir),
        '--mount',
        'type=bind,source={home},target={home}'.format(home=home),
        '--mount',
        'type=bind,source=/etc/timezone,target=/etc/timezone,readonly',
        '--mount',
        'type=bind,source=/etc/localtime,target=/etc/localtime,readonly',
        '--mount',
        'type=bind,source=/etc/group,target=/etc/group,readonly',
        '--mount',
        'type=bind,source=/etc/passwd,target=/etc/passwd,readonly',
        '--cap-add',
        'SYS_PTRACE',
    ]

    if rel_project_dir != docker_rel_project_dir:
        flags.extend(
            [
                '--mount', 'type=bind,source={project_dir},target={docker_project_dir}'.format(
                    project_dir=os.path.join(root_dir, rel_project_dir),
                    docker_project_dir=os.path.join(docker_root_dir, docker_rel_project_dir))
            ])

    if os.path.exists('/opt/toolchains'):
        flags.extend(['--mount', 'type=bind,source=/opt/toolchains,target=/opt/toolchains'])

    if os.path.exists('/opt/tools'):
        flags.extend(['--mount', 'type=bind,source=/opt/tools,target=/opt/tools'])

    if os.path.exists('/opt/STM'):
        flags.extend(['--mount', 'type=bind,source=/opt/STM,target=/opt/STM'])

    if os.path.exists('/opt/cov-analysis'):
        flags.extend(['--mount', 'type=bind,source=/opt/cov-analysis,target=/opt/cov-analysis'])

    if is_interactive():
        flags.extend(['-it'])

    if run_as_root:
        flags.extend(["-e TAR_OPTIONS='--no-same-owner --no-same-permissions'"])
    else:
        flags.extend([
            '-u',
            '{id}:{gid}'.format(id=os.getuid(), gid=os.getgid()),
        ])

    if additonal_mounts:
        for mount in additonal_mounts:
            flags.extend(['--mount', '{mount}'.format(mount=mount)])

    if hostname is not None:
        flags.extend(['--hostname', hostname])

    if network is not None:
        flags.extend(['--network', network])

    for env_var in FORWARDED_ENVIRONMENT_VARIABLES + list(env_variables):
        flags.extend(['-e', env_var])

    return flags


def docker_image_exists_locally(docker_command, image):
    """
    Check if the image exists locally.

    :param docker_command: The docker command to use when running docker image ls
    :param image: the image to look for
    :return: True if image exists locally
    """
    try:
        output = subprocess.check_output(
            [
                docker_command, 'image', 'ls', '--filter', 'reference={ref}'.format(ref=image),
                '--format', '{{.Repository}}:{{.Tag}}'
            ],
            shell=False,
            universal_newlines=True).strip()
        return output == image
    except Exception:
        return False


def determine_root_and_rel_project_dir_and_relative_cwd(root_dir=None, project_dir=None):
    """
    Determine the root directory, the project_dir and the relative current working directory.

    First determines the project dir and if none are found the current working directory is used as
    project dir.

    Then if root_dir is specified it must be a parent of project_dir and if root_dir is not specified
    the parent directory of the project dir is used.

    :param root_dir:
    :param project_dir:
    :return: Tuple with (abs_root_dir, rel_project_dir, rel_cwd)
    """
    cwd = os.getcwd()

    if project_dir is None:
        try:
            project_dir = find_project_dir(cwd)
            logger.debug('Using {project_dir} as project dir'.format(project_dir=project_dir))
        except ValueError:
            project_dir = cwd
            logger.debug('Using current working directory {cwd} as root directory'.format(cwd=cwd))
    else:
        project_dir = os.path.abspath(project_dir)
        logger.debug(
            'Using specified directory {project_dir} as project directory'.format(
                project_dir=project_dir))

    rel_cwd = os.path.relpath(cwd, project_dir)
    if rel_cwd.startswith('..'):
        raise ValueError(
            'Invalid project dir {project_dir}. Must be parent to current working directory {cwd}'.
            format(project_dir=project_dir, cwd=cwd))

    if root_dir is None:
        root_dir = os.path.dirname(project_dir)
        rel_project_dir = os.path.basename(project_dir)
    else:
        root_dir = os.path.abspath(root_dir)
        rel_project_dir = os.path.relpath(project_dir, root_dir)
        if rel_project_dir.startswith('..'):
            raise ValueError(
                'Invalid root dir {root_dir}. Must be parent to project directory {project_dir}'.
                format(root_dir=root_dir, project_dir=project_dir))

    return root_dir, rel_project_dir, rel_cwd


def determine_docker_rel_project_dir(rel_project_dir, config):
    if rel_project_dir != '.' and config.project_dir_name is not None and os.path.basename(
            rel_project_dir) != config.project_dir_name:
        return os.path.join(os.path.dirname(rel_project_dir), config.project_dir_name)
    else:
        return rel_project_dir


def find_project_dir(directory):
    if not directory or directory == '/':
        raise ValueError('No directory found')
    elif (os.path.exists(os.path.join(directory, 'maketools', 'setup.mk'))
          or os.path.exists(os.path.join(directory, '.zebra'))):
        return directory
    else:
        return find_project_dir(os.path.dirname(directory))
