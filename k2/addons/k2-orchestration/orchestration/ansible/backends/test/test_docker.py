from unittest import TestCase

from ...config import AnsibleConfig
from ...manager import get_backend
from ..docker import DockerBackend


class TestGetDockerBackend(TestCase):

    def test_get_backend_docker(self):
        ac = AnsibleConfig('ansible.cfg', 'playbook')
        backend = get_backend('docker', ac)
        self.assertIsInstance(backend, DockerBackend)


class TestDockerBackend(TestCase):

    def test_register_components(self):
        pass
