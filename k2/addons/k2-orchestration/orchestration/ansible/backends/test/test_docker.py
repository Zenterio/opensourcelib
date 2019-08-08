from unittest import TestCase
from unittest.mock import Mock, patch

from docker.errors import ContainerError

from orchestration.ansible.backends.docker import ContainerKilledException, ContainerKiller, \
    ContainerNotRunException, DockerAnsibleRunner
from virt.docker import DOCKER_IMAGE_REGISTRY

from ...config import AnsibleConfig
from ...manager import get_backend
from ..docker import DockerBackend


class TestGetDockerBackend(TestCase):

    def test_get_backend_docker(self):
        ac = AnsibleConfig('ansible.cfg', 'playbook')
        backend = get_backend('docker', ac)
        self.assertIsInstance(backend, DockerBackend)


class TestDockerAnsibleRunner(TestCase):

    def test_successful_run_command(self):
        runner = _create_and_mock_runner()
        runner._run_command('command', 'hostgroup')

    def test_unsuccessful_run_command_raises_container_error(self):
        runner = _create_and_mock_runner(exit_code=1)
        with self.assertRaises(ContainerError):
            runner._run_command('command', 'hostgroup')

    def test_when_stopped_run_command_raises_not_run_exception(self):
        runner = _create_and_mock_runner(stopped=True)
        with self.assertRaises(ContainerNotRunException):
            runner._run_command('command', 'hostgroup')

    def test_when_stopped_after_run_started_run_command_raises_killed_exception(self):
        runner = _create_and_mock_runner()
        container = runner._client.containers.run.return_value

        def wait(*args, **kwargs):
            """Triggers stop after run has started."""
            runner._container_killer.stop_all()
            return {'StatusCode': 0}

        # Overrides default return value with side effect
        container.wait.return_value = None
        container.wait.side_effect = wait

        with self.assertRaises(ContainerKilledException):
            runner._run_command('command', 'hostgroup')

        container.kill.assert_called()

    def test_image_uses_registry_if_given(self):
        runner = _create_and_mock_runner()
        assert runner._image == 'edgegravity/ansible.run'
        runner = _create_and_mock_runner(
            config_side_effect=lambda x, y: 'test' if x == DOCKER_IMAGE_REGISTRY else y)
        assert runner._image == 'test/edgegravity/ansible.run'


def _create_and_mock_runner(exit_code=0, stopped=False, config_side_effect=lambda x, y: y):
    ansible_config = AnsibleConfig('file', 'playbook')
    config = Mock()
    config.get.side_effect = config_side_effect
    docker_client = Mock()

    container_mock = Mock()
    container_mock.name = 'container_mock'
    docker_client.containers.run.return_value = container_mock
    container_mock.wait.return_value = {'StatusCode': exit_code}

    with patch('orchestration.ansible.backends.docker._get_docker_client',
               return_value=docker_client):
        container_killer = ContainerKiller()
        container_killer._stopped = stopped

        return DockerAnsibleRunner(ansible_config, config, 'logpath', container_killer)
