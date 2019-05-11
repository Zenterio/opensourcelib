import unittest
from unittest.mock import Mock

from znake.debtest import generate_install_dependencies_command, get_namespace


class TestRenderDebianTest(unittest.TestCase):

    def test_generate_install_dependencies_without_dependencies(self):
        assert generate_install_dependencies_command([]) == ''

    def test_generate_install_dependencies_with_some_dependencies(self):
        assert generate_install_dependencies_command(['package_a', 'package_b']) == (
            'sudo apt-get --yes '
            '-o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" '
            'install package_a package_b && ')


class TestGetNamespace(unittest.TestCase):

    def test_get_namespace_with_no_targets(self):
        config = self._get_mock_config()
        namespace = get_namespace(config)
        self.assertEqual(len(namespace.tasks), 0)
        self.assertEqual(len(namespace.collections), 1)

    def test_get_namespace_with_debtest_target(self):
        config = self._get_mock_config()
        config.znake.deb.targets.append({'name': 'u14', 'test_image': 'k2runner.u14'})
        namespace = get_namespace(config)
        self.assertEqual(len(namespace.tasks), 3)
        self.assertEqual(len(namespace.collections), 1)

    def _get_mock_config(self):
        config = Mock()
        config.znake.debtest.packages = ['my_package']
        config.znake.deb.targets = []
        return config
