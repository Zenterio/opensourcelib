"""Extension that provides commands to clean docker containers and images."""
import sys

from zaf.commands import COMMAND
from zaf.commands.command import CommandId
from zaf.component.decorator import requires
from zaf.config.options import ConfigOption, ConfigOptionId
from zaf.config.types import Flag
from zaf.extensions.extension import AbstractExtension, ExtensionConfig, FrameworkExtension

from k2.sut import SUT
from virt.docker import DOCKER_IMAGES_IDS, DOCKER_IMAGES_REPOSITORY, DOCKER_IMAGES_TAG, \
    DockerContainerNode


@requires(manager='ComponentManager')
@requires(config='Config')
def clean_containers(application, manager, config):
    """Clean docker containers for configured suts."""
    docker_client = get_docker_client()
    exit_code = 0
    for sut in config.get(SUT):
        sut_component = manager.get_unique_class_for_entity(sut)

        if 'docker' in manager.get_cans(sut_component):
            node_name = DockerContainerNode(sut=sut_component, config=config).containername
            container = get_container(docker_client, node_name)
            if container:
                print('Cleaning up docker container {name}'.format(name=node_name))
                try:
                    remove_container(container, config.get(FORCE))
                except Exception as e:
                    print(
                        'Error: Cleaning up container {name} failed: {msg}'.format(
                            name=node_name, msg=str(e)), sys.stderr)
                    exit_code = 1

    return exit_code


def get_docker_client():
    import docker
    return docker.from_env()


def get_container(docker_client, name):
    for c in docker_client.containers.list():
        if c.name == name:
            return c

    return None


def remove_container(container, force):
    container.remove(force=force)


@requires(config='Config')
def clean_images(application, config):
    """Clean configured docker images."""
    docker_client = get_docker_client()
    exit_code = 0
    for image in config.get(DOCKER_IMAGES_IDS):

        repository = config.get(DOCKER_IMAGES_REPOSITORY, entity=image)
        tag = config.get(DOCKER_IMAGES_TAG, entity=image)
        tag = ':'.join([repository, tag])

        if image_exists(docker_client, tag):
            print('Cleaning up docker image {tag}'.format(tag=tag))
            try:
                docker_client.images.remove(tag, force=config.get(FORCE))
            except Exception as e:
                print('Cleaning of image {tag} failed: {msg}'.format(tag=tag, msg=str(e)))
                exit_code = 1

    return exit_code


def image_exists(docker_client, name):
    for i in docker_client.images.list():
        for tag in i.tags:
            if tag == name:
                return True

    return False


FORCE = ConfigOptionId(
    'force',
    'Force removal. Forwarded to docker.',
    option_type=Flag(),
    default=False,
    short_name='f',
    namespace='clean',
    short_alias=True,
)

CLEAN_CONTAINERS = CommandId(
    'cleancontainers',
    clean_containers.__doc__,
    clean_containers, [ConfigOption(FORCE, required=True)],
    uses=['sut'])

CLEAN_IMAGES = CommandId(
    'cleanimages',
    clean_images.__doc__,
    clean_images,
    [ConfigOption(FORCE, required=True)],
)


@FrameworkExtension('docker', load_order=91, commands=[CLEAN_CONTAINERS, CLEAN_IMAGES])
class CleanDocker(AbstractExtension):
    """Commands for cleaning up docker containers and images."""

    def get_config(self, config, requested_config_options, requested_command_config_options):
        """Change log level for cleancontainers and cleanimages to not get docker spam on command line."""
        created_config = {}
        if config.get(COMMAND) in ['cleancontainers', 'cleanimages']:
            created_config = {'log.level': 'warning'}
        return ExtensionConfig(created_config, priority=1, source='CleanDocker')
