import unittest
from unittest.mock import Mock

from znake.systest import get_namespace


class TestGetNamespace(unittest.TestCase):

    def test_get_namespace_with_no_targets(self):
        config = self._get_mock_config()
        namespace = get_namespace(config)
        self.assertEqual(len(namespace.tasks), 0)
        self.assertEqual(len(namespace.collections), 1)

    def test_get_namespace_with_systest_target(self):
        config = self._get_mock_config()
        config.znake.systest.targets.append({'name': 'u14', 'image': 'k2runner.u14'})
        namespace = get_namespace(config)
        self.assertEqual(len(namespace.tasks), 3)
        self.assertEqual(len(namespace.collections), 1)

    def _get_mock_config(self):
        config = Mock()
        config.znake.systest.packages = ['my_package']
        config.znake.systest.targets = []
        return config
