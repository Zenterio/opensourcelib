import unittest
from unittest.mock import Mock, patch

from zaf.builtin.unittest.harness import ExtensionTestHarness
from zaf.component.decorator import requires
from zaf.component.scope import Scope
from zaf.config.manager import ConfigManager

from zebra.docker import CONTAINER_ROOT_DIR_OPTION, ENV_VARIABLES_OPTION, HOSTNAME_OPTION, \
    IMAGE_OPTION, MOUNTS_OPTION, NETWORK_OPTION, PROJECT_DIR_NAME_OPTION, PROJECT_DIR_OPTION, \
    PULL_OPTION, REGISTRY_CACHE_OPTION, REGISTRY_OPTION, ROOT_DIR_OPTION, ROOT_OPTION, TAG_OPTION, \
    USE_REGISTRY_OPTION
from zebra.docker.dockerconfig import DockerConfig, DockerConfigExtension


class TestDockerConfig(unittest.TestCase):

    def test_docker_config_extension_can_be_instantiated_with_only_defaults(self):
        with create_harness():
            pass

    def test_get_config_finds_default_docker_registry_cache(self):
        with create_harness() as harness, \
                patch('zebra.docker.dockerconfig.find_docker_registry_cache', return_value='registry_cache'):
            self.assertEqual(
                harness.extension.get_config(Mock(), [], {}).config[REGISTRY_CACHE_OPTION.key],
                'registry_cache')

    def test_docker_config_component_uses_config_values(self):
        scope = Scope('scope')

        config = ConfigManager()
        config.set(IMAGE_OPTION, 'abs.u16')
        config.set(TAG_OPTION, 'tag')
        config.set(REGISTRY_OPTION, 'registry')
        config.set(USE_REGISTRY_OPTION, False)
        config.set(REGISTRY_CACHE_OPTION, 'registry_cache')
        config.set(PULL_OPTION, False)
        config.set(HOSTNAME_OPTION, 'hostname')
        config.set(ENV_VARIABLES_OPTION, ['envvar'])
        config.set(MOUNTS_OPTION, ['mount'])
        config.set(ROOT_OPTION, True)
        config.set(ROOT_DIR_OPTION, 'root_dir')
        config.set(CONTAINER_ROOT_DIR_OPTION, 'container_root_dir')
        config.set(PROJECT_DIR_OPTION, 'project_dir')
        config.set(PROJECT_DIR_NAME_OPTION, 'project_dir_name')
        config.set(NETWORK_OPTION, 'network')

        with create_harness(config) as harness:

            @requires(docker_config='DockerConfig')
            def assert_docker_config(docker_config):
                self.assertEqual(docker_config.image, 'abs.u16')
                self.assertEqual(docker_config.tag, 'tag')
                self.assertEqual(docker_config.registry, 'registry')
                self.assertFalse(docker_config.use_registry)
                self.assertEqual(docker_config.registry_cache, 'registry_cache')
                self.assertFalse(docker_config.pull)
                self.assertEqual(docker_config.hostname, 'hostname')
                self.assertEqual(docker_config.env_variables, ('envvar', ))
                self.assertEqual(docker_config.mounts, ('mount', ))
                self.assertEqual(docker_config.root, True)
                self.assertEqual(docker_config.root_dir, 'root_dir')
                self.assertEqual(docker_config.container_root_dir, 'container_root_dir')
                self.assertEqual(docker_config.project_dir, 'project_dir')
                self.assertEqual(docker_config.project_dir_name, 'project_dir_name')
                self.assertEqual(docker_config.network, 'network')

            harness.component_factory.call(assert_docker_config, scope)


def create_harness(config=None):
    return ExtensionTestHarness(DockerConfigExtension, config=config, components=[DockerConfig])
