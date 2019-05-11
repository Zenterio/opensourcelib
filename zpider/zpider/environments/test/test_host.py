import unittest
from unittest.mock import Mock, patch

from zaf.builtin.unittest.harness import ExtensionTestHarness
from zaf.config.manager import ConfigManager

from zpider.environments import ENV, RunException
from zpider.environments.host import HostEnv, HostEnvExtension


class TestHostExtension(unittest.TestCase):

    def test_host_component_is_registered_if_env_is_host(self):
        with _create_harness() as harness:
            self.assertEqual(
                harness.component_manager.COMPONENT_REGISTRY['Env'][0].__name__, 'HostEnv')

    def test_host_component_is_not_registered_if_env_is_not_host(self):
        with _create_harness(env='docker') as harness:
            self.assertNotIn('Env', harness.component_manager.COMPONENT_REGISTRY)


class TestHostEnv(unittest.TestCase):

    def test_host_returns_normally_if_returncode_is_0(self):
        result = Mock()
        result.returncode = 0
        with patch('subprocess.Popen', return_value=result):
            HostEnv().run('command')

    def test_host_env_raises_run_exception_if_returncode_is_not_0(self):
        result = Mock()
        result.returncode = 1
        with patch('subprocess.Popen', return_value=result):
            with self.assertRaises(RunException):
                HostEnv().run('command')


def _create_harness(env='host'):
    config = ConfigManager()
    config.set(ENV, env)
    return ExtensionTestHarness(HostEnvExtension, config=config)
