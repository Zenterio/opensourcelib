"""Extension that handles the docker configuration to use."""
from zaf.component.decorator import component, requires
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, ExtensionConfig, FrameworkExtension

from zebra.config.config import find_docker_registry_cache
from zebra.docker import CONTAINER_ROOT_DIR_OPTION, ENV_VARIABLES_OPTION, HOSTNAME_OPTION, \
    IMAGE_OPTION, IMAGE_OVERRIDE_OPTION, MOUNTS_OPTION, NETWORK_OPTION, PROJECT_DIR_NAME_OPTION, \
    PROJECT_DIR_OPTION, PULL_OPTION, REGISTRY_CACHE_OPTION, REGISTRY_OPTION, ROOT_DIR_OPTION, \
    ROOT_OPTION, TAG_OPTION, USE_REGISTRY_OPTION


@component(name='DockerConfig')
@requires(config='Config')
class DockerConfig(object):
    """Config object with all the information to run the docker containers."""

    def __init__(self, config):
        self._config = config

    @property
    def image(self):
        return self._config.get(IMAGE_OPTION)

    @property
    def image_override(self):
        return self._config.get(IMAGE_OVERRIDE_OPTION)

    @property
    def tag(self):
        return self._config.get(TAG_OPTION)

    @property
    def registry(self):
        return self._config.get(REGISTRY_OPTION)

    @property
    def use_registry(self):
        return self._config.get(USE_REGISTRY_OPTION)

    @property
    def no_registry(self):
        return not self.use_registry

    @property
    def registry_cache(self):
        return self._config.get(REGISTRY_CACHE_OPTION)

    @property
    def pull(self):
        return self._config.get(PULL_OPTION)

    @property
    def no_pull(self):
        return not self.pull

    @property
    def env_variables(self):
        return self._config.get(ENV_VARIABLES_OPTION)

    @property
    def mounts(self):
        return self._config.get(MOUNTS_OPTION)

    @property
    def hostname(self):
        return self._config.get(HOSTNAME_OPTION)

    @property
    def root(self):
        return self._config.get(ROOT_OPTION)

    @property
    def root_dir(self):
        return self._config.get(ROOT_DIR_OPTION)

    @property
    def container_root_dir(self):
        return self._config.get(CONTAINER_ROOT_DIR_OPTION)

    @property
    def project_dir(self):
        return self._config.get(PROJECT_DIR_OPTION)

    @property
    def project_dir_name(self):
        return self._config.get(PROJECT_DIR_NAME_OPTION)

    @property
    def network(self):
        return self._config.get(NETWORK_OPTION)


@FrameworkExtension(
    'dockerconfig',
    load_order=49,
    config_options=[
        ConfigOption(IMAGE_OPTION, required=True),
        ConfigOption(IMAGE_OVERRIDE_OPTION, required=False),
        ConfigOption(TAG_OPTION, required=True),
        ConfigOption(REGISTRY_OPTION, required=True),
        ConfigOption(USE_REGISTRY_OPTION, required=True),
        ConfigOption(REGISTRY_CACHE_OPTION, required=False),
        ConfigOption(PULL_OPTION, required=True),
        ConfigOption(HOSTNAME_OPTION, required=False),
        ConfigOption(ENV_VARIABLES_OPTION, required=False),
        ConfigOption(MOUNTS_OPTION, required=False),
        ConfigOption(ROOT_OPTION, required=True),
        ConfigOption(ROOT_DIR_OPTION, required=False),
        ConfigOption(CONTAINER_ROOT_DIR_OPTION, required=True),
        ConfigOption(PROJECT_DIR_OPTION, required=False),
        ConfigOption(PROJECT_DIR_NAME_OPTION, required=False),
        ConfigOption(NETWORK_OPTION, required=True),
    ])
class DockerConfigExtension(AbstractExtension):

    def get_config(self, config, requested_config_options, requested_command_config_options):
        return ExtensionConfig(
            {
                REGISTRY_CACHE_OPTION.key: find_docker_registry_cache(),
            },
            priority=1,
            source='dockerconfig')
