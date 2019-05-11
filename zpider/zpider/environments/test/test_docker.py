import unittest
from unittest.mock import Mock, patch

from zaf.builtin.unittest.harness import ExtensionTestHarness
from zaf.config.manager import ConfigManager

from zpider.environments import ENV
from zpider.environments.docker import DockerEnv, DockerEnvExtension


class TestDockerExtension(unittest.TestCase):

    def test_docker_component_is_registered_if_env_is_docker(self):
        with _create_harness() as harness:
            self.assertEqual(
                harness.component_manager.COMPONENT_REGISTRY['Env'][0].__name__, 'DockerEnv')

    def test_docker_component_is_not_registered_if_env_is_not_docker(self):
        with _create_harness(env='host') as harness:
            self.assertNotIn('Env', harness.component_manager.COMPONENT_REGISTRY)


class TestDockerEnv(unittest.TestCase):

    def setUp(self):
        host_env = Mock()

        with patch('zpider.environments.docker.HostEnv', return_value=host_env), \
                patch('os.getcwd', return_value='cwd'), \
                patch('zpider.environments.docker.zpider_package_dir', return_value='zpider_package_dir'):
            DockerEnv().run('command')
            self.host_env_command = host_env.method_calls[0][1][0]

    def test_docker_mounts_cwd_to_itself_inside_container(self):
        self.assertIn('--mount type=bind,source=cwd,target=cwd', self.host_env_command)

    def test_docker_mounts_zpider_package_dir_to_itself_inside_container(self):
        self.assertIn(
            '--mount type=bind,source=zpider_package_dir,target=zpider_package_dir',
            self.host_env_command)

    def test_docker_sets_cwd_to_workdir(self):
        self.assertIn('--workdir cwd', self.host_env_command)

    def test_docker_removes_container_after_command_is_completed(self):
        self.assertIn('--rm', self.host_env_command)

    def test_user_flag_is_provided_if_root_flag_is_not_set(self):
        DockerEnv.root = False
        with patch('os.getuid', return_value=1), patch('os.getgid', return_value=2):
            self.assertEqual(
                DockerEnv()._get_docker_user_flags(), ' '.join(
                    [
                        '--mount', 'type=bind,source=/etc/group,target=/etc/group,readonly',
                        '--mount', 'type=bind,source=/etc/passwd,target=/etc/passwd,readonly',
                        '--user 1:2'
                    ]))

    def test_user_flag_is_not_provided_if_root_flag_is_set(self):
        DockerEnv.root = True
        self.assertEqual(DockerEnv()._get_docker_user_flags(), '')


def _create_harness(env='docker'):
    config = ConfigManager()
    config.set(ENV, env)
    return ExtensionTestHarness(DockerEnvExtension, config=config)
