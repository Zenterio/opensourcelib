import unittest
from unittest.mock import Mock

from zaf.builtin.unittest.harness import ComponentMock, ExtensionTestHarness
from zaf.component.scope import Scope
from zaf.config.manager import ConfigManager
from zaf.messages.dispatchers import LocalMessageQueue

from zebra.docker import IMAGE_OPTION
from zebra.docker.dockerconfig import DockerConfig
from zebra.ui.make import MAKE_ARGUMENTS, MAKE_ENDPOINT, PRE_MAKE, MakeExtension, make


class Testmake(unittest.TestCase):

    def test_make_called_with_correct_parameters(self):
        docker_run = Mock()

        scope = Scope('scope')
        with create_harness(docker_run) as harness:
            application = Mock()
            application.config = harness.config
            docker_run.docker_config = DockerConfig(harness.config)

            docker_run.run_in_docker.return_value = 0
            exit_code = harness.component_factory.call(make, scope, application)

            self.assertEqual(exit_code, 0)
            docker_run.run_in_docker.assert_called_with(
                ['zmake', 'arg1', '--opt2'], forward_signals=False)

    def test_make_command_taken_from_image(self):
        docker_run = Mock()

        scope = Scope('scope')
        with create_harness(docker_run, 'abs.u12') as harness:
            application = Mock()
            application.config = harness.config
            docker_run.docker_config = DockerConfig(harness.config)

            docker_run.run_in_docker.return_value = 0
            exit_code = harness.component_factory.call(make, scope, application)

            self.assertEqual(exit_code, 0)
            docker_run.run_in_docker.assert_called_with(
                ['make', 'arg1', '--opt2'], forward_signals=False)

    def test_make_triggers_pre_make_event_with_make_arguments_as_data(self):
        docker_run = Mock()

        scope = Scope('scope')
        with create_harness(docker_run) as harness:
            application = Mock()
            application.config = harness.config
            application.messagebus = harness.messagebus
            docker_run.docker_config = DockerConfig(harness.config)

            with LocalMessageQueue(harness.messagebus, [PRE_MAKE], [MAKE_ENDPOINT]) as queue:
                harness.component_factory.call(make, scope, application)
                self.assertEqual(queue.get(timeout=1).data, ('arg1', '--opt2'))

    def test_make_forwards_all_exceptions(self):
        docker_run = Mock()

        scope = Scope('scope')
        with create_harness(docker_run) as harness:
            application = Mock()
            application.config = harness.config

            docker_run.run_in_docker.side_effect = Exception()
            with self.assertRaises(Exception):
                harness.component_factory.call(make, scope, application)


def create_harness(docker_run=Mock(), image='abs.u16'):
    config = ConfigManager()
    config.set(MAKE_ARGUMENTS, ('arg1', '--opt2'))
    config.set(IMAGE_OPTION, image)

    return ExtensionTestHarness(
        MakeExtension,
        config=config,
        components=[ComponentMock('DockerRun', docker_run)],
    )
