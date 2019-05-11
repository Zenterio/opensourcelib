import unittest
from unittest.mock import Mock

from zaf.builtin.unittest.harness import ComponentMock, ExtensionTestHarness
from zaf.component.scope import Scope

from zebra.ui.shell import ShellExtension, shell


class Testshell(unittest.TestCase):

    def test_shell_called_with_correct_parameters(self):
        docker_run = Mock()

        scope = Scope('scope')
        with create_harness(docker_run) as harness:
            application = Mock()
            application.config = harness.config

            docker_run.run_in_docker.return_value = 0
            exit_code = harness.component_factory.call(shell, scope, application)

            self.assertEqual(exit_code, 0)
            docker_run.run_in_docker.assert_called_with(['/bin/bash'], forward_signals=True)

    def test_shell_forwards_all_exceptions(self):
        docker_run = Mock()

        scope = Scope('scope')
        with create_harness(docker_run) as harness:
            application = Mock()
            application.config = harness.config

            docker_run.run_in_docker.side_effect = Exception()
            with self.assertRaises(Exception):
                harness.component_factory.call(shell, scope, application)


def create_harness(docker_run=Mock()):
    return ExtensionTestHarness(
        ShellExtension,
        components=[ComponentMock('DockerRun', docker_run)],
    )
