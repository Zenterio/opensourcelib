"""
Facilitate managing and running Docker containers in K2.

The communication with the Docker daemon is handled by the docker-py package.
For information about its capabilities and interface, please see:
https://docker-py.readthedocs.io/en/3.7.0/index.html
"""
import hashlib
import logging
import os
import pprint
from collections import OrderedDict

from zaf.component.decorator import component, requires
from zaf.component.util import add_cans
from zaf.config.options import ConfigOption, ConfigOptionId
from zaf.config.types import Entity, Flag
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name

from k2.cmd.run import RUN_COMMAND
from k2.sut import SUT

logger = logging.getLogger(get_logger_name('k2', 'docker'))
logger.addHandler(logging.NullHandler())


class DockerError(Exception):
    pass


class Container(object):
    """Interact with a running Docker container."""

    def __init__(self, image, container):
        self._image = image
        self._container = container

    def stop(self, timeout=None):
        logger.info('Stopping container {i} {id}'.format(i=self._image, id=self._container.id))
        self._container.stop(timeout=timeout)

    def exec(self, line):
        exit_code, (stdout, stderr) = self._container.exec_run(line, demux=True)
        stdout = stdout.decode('utf-8') if stdout else ''
        stderr = stderr.decode('utf-8') if stderr else ''
        return stdout, stderr, exit_code

    @property
    def ip(self):
        self._container.reload()
        logger.debug('Trying to get container IP from: {attrs}'.format(attrs=self._container.attrs))
        networks = list(self._container.attrs['NetworkSettings']['Networks'].values())

        if networks:
            ip = networks[0]['IPAddress']
            logger.debug('IP for first network is {ip}'.format(ip=ip))

            return ip
        else:
            logger.debug('No IP found')
            return None


class Docker(object):
    """
    Interact with a Docker daemon.

    By default, a docker-py client is created based on environment variables.
    If required, a more specialized client may be provided.
    """

    def __init__(self, client=None):
        import docker
        self._client = client if client else docker.from_env()
        self._log_client_version_information()

    def pull(self, repository, tag=None):
        if tag is None:
            # tag=None will pull every tag for a repository.
            # This can be time consuming, assume "latest" instead.
            logger.info('No tag provided, assuming "latest"')
            tag = 'latest'
        logger.info('Pulling Docker image: {r}:{t}'.format(r=repository, t=tag))
        image = self._client.images.pull(repository, tag=tag)
        logger.info('Pulled Docker image: {r} {id}'.format(r=repository, id=image.id))

    def start(self, image, command=None, name=None, **kwargs):
        kwargs.update({'detach': True, 'auto_remove': True})
        cmd = '(default command)' if command is None else command
        logger.info('Starting {i} with command "{cmd}"'.format(i=image, cmd=cmd))
        logger.debug('kwargs: {kwargs}'.format(kwargs=kwargs))

        container = self.client.containers.run(image, command, name=name, **kwargs)
        logger.info('Started container {i} {id}'.format(i=image, id=container.id))
        return Container(image, container)

    def get_container(self, name):
        for c in self._client.containers.list():
            if c.name == name:
                return c

        return None

    @property
    def client(self):
        import docker
        try:
            self._client.ping()
            return self._client
        except docker.errors.APIError as e:
            msg = 'Docker API server unresponsive'
            logger.debug(msg, exc_info=True)
            logger.error(msg)
            raise DockerError(msg) from e

    def _log_client_version_information(self):
        logger.info('Docker client version:')
        logger.info(pprint.pformat(self.client.version()))


DOCKER_IMAGE_PULL = ConfigOptionId(
    'docker.image.pull',
    'Pull Docker image before starting the containers',
    option_type=Flag(),
    default=True,
)

DOCKER_IMAGE_REGISTRY = ConfigOptionId(
    'docker.image.registry',
    'Docker registry, intended to be used as part of image repository definitions.',
    option_type=str,
)

DOCKER_IMAGE_STOP_TIMEOUT = ConfigOptionId(
    'docker.image.stop.timeout',
    (
        'Time to wait before forcefully stopping a container. '
        'Set to zero to not attempt a graceful stop.'),
    option_type=int,
    default=10,
)

DOCKER_KEEP_RUNNING = ConfigOptionId(
    'docker.keep.running',
    'Keep docker containers running after usage.'
    'Will also re-connect to running containers if they exist.',
    default=False,
    option_type=Flag(),
)

DOCKER_IMAGES_IDS = ConfigOptionId(
    'ids',
    'Identifies a Docker image',
    namespace='docker.images',
    entity=True,
    multiple=True,
)

DOCKER_IMAGES_REPOSITORY = ConfigOptionId(
    'repository',
    'Docker image repository',
    at=DOCKER_IMAGES_IDS,
)

DOCKER_IMAGES_TAG = ConfigOptionId(
    'tag', 'Docker image tag', at=DOCKER_IMAGES_IDS, default='latest')

DOCKER_IMAGES_ENVIRONMENT = ConfigOptionId(
    'environment',
    'Key-value pair separated by equal-sign, e.g. ENVVAR=value',
    at=DOCKER_IMAGES_IDS,
    option_type=str,
    multiple=True,
)

DOCKER_IMAGES_HOSTNAME = ConfigOptionId(
    'hostname',
    'Hostname for Docker containers started from this image',
    at=DOCKER_IMAGES_IDS,
)

DOCKER_IMAGES_MOUNT_POINTS = ConfigOptionId(
    'mountpoints',
    'Mountpoints for Docker containers started from this image',
    at=DOCKER_IMAGES_IDS,
    multiple=True,
)

DOCKER_IMAGES_NETWORK = ConfigOptionId(
    'network',
    'Network for Docker containers started from this image',
    at=DOCKER_IMAGES_IDS,
)

SUT_DOCKER_IMAGE_ID = ConfigOptionId(
    'docker.image',
    'Docker image to use when starting the SUT',
    at=SUT,
    option_type=Entity(),
)

SUT_DOCKER_IMAGE_ENVIRONMENT = ConfigOptionId(
    'docker.environment',
    'Key-value pair separated by equal-sign, e.g. ENVVAR=value',
    at=SUT,
    option_type=str,
    multiple=True,
)

SUT_DOCKER_IMAGE_HOSTNAME = ConfigOptionId(
    'docker.hostname',
    'Hostname to use for this SUT',
    at=SUT,
    option_type=str,
)

SUT_DOCKER_CONTAINER_NAME = ConfigOptionId(
    'docker.container.name',
    'Container name to use for this SUT',
    at=SUT,
    option_type=str,
)

SUT_DOCKER_IMAGE_MOUNT_POINTS = ConfigOptionId(
    'docker.mountpoints',
    'Mountpoints to use for this SUT',
    at=SUT,
    option_type=str,
    multiple=True,
)

SUT_DOCKER_IMAGE_NETWORK = ConfigOptionId(
    'docker.network',
    'Network to use for this SUT',
    at=SUT,
    option_type=str,
)


@component(name='Node', can=['docker'])
@requires(sut='Sut', can=['docker'])
@requires(config='Config')
class DockerContainerNode(object):

    def __init__(self, extra_args=None, sut=None, config=None):
        self._extra_args = extra_args if extra_args is not None else {}
        self._entity = sut.entity
        self._container = None
        self._containername = config.get(SUT_DOCKER_CONTAINER_NAME, entity=sut.entity)
        self._docker = Docker()
        self._image_entity = config.get(SUT_DOCKER_IMAGE_ID, entity=sut.entity)
        self._repository = config.get(DOCKER_IMAGES_REPOSITORY, entity=self._image_entity)
        self._tag = config.get(DOCKER_IMAGES_TAG, entity=self._image_entity)
        self._environment = self._translate_config_to_env(
            config.get(SUT_DOCKER_IMAGE_ENVIRONMENT, entity=sut.entity, default=[]) +
            config.get(DOCKER_IMAGES_ENVIRONMENT, entity=self._image_entity, default=[]))
        self._hostname = config.get(
            SUT_DOCKER_IMAGE_HOSTNAME,
            entity=sut.entity,
            default=config.get(DOCKER_IMAGES_HOSTNAME, entity=self._image_entity))
        self._mounts = self._translate_config_to_mounts(
            config.get(SUT_DOCKER_IMAGE_MOUNT_POINTS, entity=sut.entity, default=[]) +
            config.get(DOCKER_IMAGES_MOUNT_POINTS, entity=self._image_entity, default=[]))
        self._networkname = config.get(
            SUT_DOCKER_IMAGE_NETWORK,
            entity=sut.entity,
            default=config.get(DOCKER_IMAGES_NETWORK, entity=self._image_entity, default=None))
        self._timeout = config.get(DOCKER_IMAGE_STOP_TIMEOUT, entity=self._image_entity)
        self._pull = config.get(DOCKER_IMAGE_PULL)
        self._image_name = '{r}:{t}'.format(r=self._repository, t=self._tag)
        self._keep_running = config.get(DOCKER_KEEP_RUNNING)
        self._registry = config.get(DOCKER_IMAGE_REGISTRY, default=None)

    def _translate_config_to_mounts(self, config):
        import docker
        mounts = []
        for mount in config:
            mount_type = None
            source = None
            target = None
            read_only = False
            for part in mount.split(','):
                if 'type=' in part:
                    mount_type = part.replace('type=', '')
                if 'source=' in part:
                    source = part.replace('source=', '')
                if 'target=' in part:
                    target = part.replace('target=', '')
                if 'readonly' == part:
                    read_only = True
            mounts.append(docker.types.Mount(target, source, type=mount_type, read_only=read_only))
        return mounts

    def _translate_config_to_env(self, config):
        result = OrderedDict()
        for item in config:
            try:
                key, value = item.split('=')
                if key not in result:  # early entries has precedence
                    result[key] = value
            except ValueError:
                raise Exception("The environment entry '{item}' is mall-formated".format(item=item))
        return result

    def __enter__(self):

        name = self.containername

        if self._keep_running:
            container = self._docker.get_container(name)
            if container is not None:
                self._container = Container(self._image_name, container)
                return self

        if self._pull:
            self._docker.pull(self._repository, self._tag)
        self._container = self._docker.start(
            self._image_name,
            name=name,
            hostname=self._hostname,
            mounts=self._mounts,
            network=self._networkname,
            environment=self._environment,
            **self._extra_args)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._container and not self._keep_running:
            self._container.stop(timeout=self._timeout)

    @property
    def ip(self):
        return self._container.ip

    @property
    def hostname(self):
        return self._hostname

    @property
    def containername(self):
        if self._containername:
            return self._containername
        if self._keep_running:
            return 'k2.' + self._entity + '.' + hashlib.sha256(os.getcwdb()).hexdigest()[:43]
        return None


@component(name='Exec', can=['docker'])
@requires(node='Node', can=['docker'])
class DockerContainerExec(object):

    def __init__(self, node):
        self._node = node

    def send_line(
            self, line, timeout=None, expected_exit_code=None, extended_process_information=True):
        stdout, stderr, exit_code = self._node._container.exec(line)
        if expected_exit_code is not None and not exit_code == expected_exit_code:
            msg = (
                'Unexpected exit code {exit_code} when running command. '
                'Expected was {expected}').format(
                    exit_code=exit_code, expected=expected_exit_code)
            logger.error(msg)
            raise DockerError(msg)
        if extended_process_information:
            return stdout, stderr, exit_code
        return stdout + stderr

    @property
    def node(self):
        return self.node


@CommandExtension(
    name='docker',
    extends=[RUN_COMMAND],
    config_options=[
        ConfigOption(DOCKER_IMAGE_PULL, required=True),
        ConfigOption(DOCKER_IMAGE_REGISTRY, required=False),
        ConfigOption(DOCKER_IMAGE_STOP_TIMEOUT, required=True),
        ConfigOption(DOCKER_IMAGES_HOSTNAME, required=False),
        ConfigOption(DOCKER_IMAGES_IDS, required=False, instantiate_on=True),
        ConfigOption(DOCKER_IMAGES_MOUNT_POINTS, required=False),
        ConfigOption(DOCKER_IMAGES_NETWORK, required=False),
        ConfigOption(DOCKER_IMAGES_REPOSITORY, required=True),
        ConfigOption(DOCKER_IMAGES_TAG, required=True),
        ConfigOption(DOCKER_KEEP_RUNNING, required=False),
        ConfigOption(SUT_DOCKER_CONTAINER_NAME, required=False),
        ConfigOption(SUT_DOCKER_IMAGE_HOSTNAME, required=False),
        ConfigOption(SUT_DOCKER_IMAGE_ID, required=False),
        ConfigOption(SUT_DOCKER_IMAGE_MOUNT_POINTS, required=False),
        ConfigOption(SUT_DOCKER_IMAGE_NETWORK, required=False),
    ],
    endpoints_and_messages={})
class DockerExtension(AbstractExtension):
    pass


@CommandExtension(
    name='docker',
    extends=['sut'],
    config_options=[
        ConfigOption(SUT, required=False, instantiate_on=True),
        ConfigOption(SUT_DOCKER_IMAGE_ID, required=False),
    ],
    endpoints_and_messages={})
class DockerAddSutCansExtension(AbstractExtension):

    def __init__(self, config, instances):
        self._entity = instances[SUT]
        self._enabled = bool(config.get(SUT_DOCKER_IMAGE_ID, default=False))

    def register_components(self, component_manager):
        if self._enabled is True:
            sut = component_manager.get_unique_class_for_entity(self._entity)
            add_cans(sut, ['docker'])
