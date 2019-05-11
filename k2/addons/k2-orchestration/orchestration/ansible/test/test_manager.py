from unittest import TestCase

from zaf.config.manager import ConfigManager

from orchestration.ansible import ANSIBLE_ENABLED, ANSIBLE_NODE, ANSIBLE_NODES
from orchestration.ansible.manager import AnsibleSuts

from ..manager import get_backend


class TestGetBackend(TestCase):

    def test_get_backend_raise_exception_for_unknown_backend(self):
        with self.assertRaises(Exception) as ctx:
            get_backend('UNKNOWN', None)
        self.assertEqual(str(ctx.exception), 'Unknown backend UNKNOWN')


class TestAnsibleSuts(TestCase):

    def test_get_config_does_not_create_config_when_not_enabled(self):
        config = ConfigManager()
        config.set_default_values([ANSIBLE_NODES, ANSIBLE_NODE])
        config.set(ANSIBLE_NODES, ['1', '2', '3'])
        config.set(ANSIBLE_ENABLED, False)
        ansible_suts = AnsibleSuts(None, None)
        self.assertNotIn('suts.ids', ansible_suts.get_config(config, [], {}).config)

    def test_get_config_uses_ansible_nodes_as_suts_when_ansible_node_is_not_set(self):
        config = ConfigManager()
        config.set_default_values([ANSIBLE_NODES, ANSIBLE_NODE])
        config.set(ANSIBLE_NODES, ['1', '2', '3'])
        config.set(ANSIBLE_ENABLED, True)
        ansible_suts = AnsibleSuts(None, None)
        self.assertCountEqual(
            ansible_suts.get_config(config, [], {}).config['suts.ids'], ['1', '2', '3'])

    def test_get_config_uses_ansible_node_as_suts_when_set(self):
        config = ConfigManager()
        config.set_default_values([ANSIBLE_NODES, ANSIBLE_NODE])
        config.set(ANSIBLE_NODES, ['1', '2', '3'])
        config.set(ANSIBLE_NODE, ['2', '3'])
        config.set(ANSIBLE_ENABLED, True)
        ansible_suts = AnsibleSuts(None, None)
        self.assertCountEqual(
            ansible_suts.get_config(config, [], {}).config['suts.ids'], ['2', '3'])
