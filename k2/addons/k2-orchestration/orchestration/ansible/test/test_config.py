from unittest import TestCase

from ..config import AnsibleConfig


class TestAnsibleConfigEnvironmentConfigToDict(TestCase):

    def test_empty_list_gives_empty_dictionary(self):
        result = AnsibleConfig._environment_config_to_dict([])
        self.assertEqual({}, result)

    def test_key_pairs_separated_by_equalsign(self):
        k2_configs = ['key1=value1', 'key2=value2']
        result = AnsibleConfig._environment_config_to_dict(k2_configs)
        expected = {'key1': 'value1', 'key2': 'value2'}
        self.assertEqual(expected, result)

    def test_mall_formated_item_raise_exception(self):
        with self.assertRaises(Exception) as ctx:
            AnsibleConfig._environment_config_to_dict(['badly formated config item'])
        self.assertEqual(
            str(ctx.exception),
            "The ansible configuration 'badly formated config item' is mall-formated")


class TestAnsibleConfigProperties(TestCase):

    def test_default_env(self):
        ac = AnsibleConfig('ansible.cfg', 'playbook', remote_user='user')
        self.assertIn('ANSIBLE_CONFIG', ac.env)
        self.assertEqual('ansible.cfg', ac.env['ANSIBLE_CONFIG'])
        self.assertIn('ANSIBLE_REMOTE_USER', ac.env)
        self.assertEqual('user', ac.env['ANSIBLE_REMOTE_USER'])

    def test_extra_env(self):
        ac = AnsibleConfig('ansible.cfg', 'playbook', environmental_config=['k=v'])
        self.assertIn('k', ac.env)
        self.assertEqual('v', ac.env['k'])
        # default is not overwritten
        self.assertIn('ANSIBLE_CONFIG', ac.env)
        self.assertEqual('ansible.cfg', ac.env['ANSIBLE_CONFIG'])

    def test_env_str(self):
        ac = AnsibleConfig('ansible.cfg', 'playbook', environmental_config=['k=v'])
        self.assertEqual('ANSIBLE_CONFIG=ansible.cfg k=v', ac.env_str)

    def test_ansible_file(self):
        ac = AnsibleConfig('ansible.cfg', 'playbook')
        self.assertEqual('ansible.cfg', ac.ansible_file)

    def test_playbook(self):
        ac = AnsibleConfig('ansible.cfg', 'playbook')
        self.assertEqual('playbook', ac.playbook)

    def test_remote_user(self):
        ac = AnsibleConfig('ansible.cfg', 'playbook', remote_user='user')
        self.assertEqual('user', ac.remote_user)

    def test_log_path_is_set_via_env(self):
        ac = AnsibleConfig(
            'ansible.cfg', 'playbook', environmental_config=['ANSIBLE_LOG_PATH=path.log'])
        self.assertEqual('path.log', ac.log_path)

    def test_log_dir(self):
        ac = AnsibleConfig('ansible.cfg', 'playbook', log_dir='logdir')
        self.assertEqual('logdir', ac.log_dir)

    def test_log_path_is_none_if_not_set(self):
        ac = AnsibleConfig('ansible.cfg', 'playbook')
        self.assertEqual(None, ac.log_path)

    def test_extra_vars_file(self):
        ac = AnsibleConfig('ansible.cfg', 'playbook', extra_vars_file='vars_file')
        self.assertEqual('vars_file', ac.extra_vars_file)
