import unittest
from unittest.mock import Mock

from zaf.builtin.unittest.harness import ComponentMock, ExtensionTestHarness
from zaf.component.scope import Scope
from zaf.config.manager import ConfigManager

from zebra.cache.commands import CacheExtension
from zebra.ui.exec import EXEC_COMMAND_WITH_ARGUMENTS, exec


class TestExec(unittest.TestCase):

    def test_exec_called_with_correct_parameters(self):
        docker_run = Mock()

        scope = Scope('scope')
        with create_harness(docker_run) as harness:
            application = Mock()
            application.config = harness.config

            docker_run.run_in_docker.return_value = 0
            exit_code = harness.component_factory.call(exec, scope, application)

            self.assertEqual(exit_code, 0)
            docker_run.run_in_docker.assert_called_with(
                ('exec', 'with', 'args'), forward_signals=False)

    def test_exec_forwards_all_exceptions(self):
        docker_run = Mock()

        scope = Scope('scope')
        with create_harness(docker_run) as harness:
            application = Mock()
            application.config = harness.config

            docker_run.run_in_docker.side_effect = Exception()
            with self.assertRaises(Exception):
                harness.component_factory.call(exec, scope, application)


def create_harness(docker_run=Mock()):
    config = ConfigManager()
    config.set(EXEC_COMMAND_WITH_ARGUMENTS, ('exec', 'with', 'args'))

    return ExtensionTestHarness(
        CacheExtension,
        config=config,
        components=[ComponentMock('DockerRun', docker_run)],
    )
