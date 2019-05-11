import unittest
from unittest.mock import patch

from zaf.application import ApplicationContext
from zaf.commands.command import CommandId
from zaf.component.decorator import component, requires

from ..application import Application, ApplicationConfiguration


def returns_none(*args):
    return None


def returns_one(*args):
    return 1


def returns_zero(*args):
    return 0


@requires(component='Component')
def command_with_requires(application, component):
    return component.get_value()


NONE_COMMAND = CommandId('None', 'Returns none', returns_none, [])
ONE_COMMAND = CommandId('One', 'Returns one', returns_one, [])
ZERO_COMMAND = CommandId('Zero', 'Returns zero', returns_zero, [])
REQUIRES_COMMAND = CommandId('Requires', 'Returns component value', command_with_requires, [])


class ApplicationExitCodeTest(unittest.TestCase):

    def test_exit_code_zero_on_success(self):
        with patch('sys.argv', ['test', 'noop']):
            app = Application(
                ApplicationConfiguration('test', application_context=ApplicationContext.EXTENDABLE))
            app.run()
            self.assertEqual(app.exit_code, 0, 'exit code should be zero on success')

    def test_exit_code_zero_if_command_return_none(self):
        with patch('sys.argv', ['test', 'noop']):
            with Application(ApplicationConfiguration(
                    'test', application_context=ApplicationContext.EXTENDABLE)) as app:
                app.command = NONE_COMMAND
                exit_code = app.execute_command()
                self.assertEqual(exit_code, 0, 'exit code should be zero if command returns None')

    def test_exit_code_zero_if_command_return_zero(self):
        with patch('sys.argv', ['test', 'noop']):
            with Application(ApplicationConfiguration(
                    'test', application_context=ApplicationContext.EXTENDABLE)) as app:
                app.command = ZERO_COMMAND
                exit_code = app.execute_command()
                self.assertEqual(exit_code, 0, 'exit code should be zero if command returns zero')

    def test_exit_code_one_if_command_return_one(self):
        with patch('sys.argv', ['test', 'noop']):
            with Application(ApplicationConfiguration(
                    'test', application_context=ApplicationContext.EXTENDABLE)) as app:
                app.command = ONE_COMMAND
                exit_code = app.execute_command()
                self.assertEqual(exit_code, 1, 'exit code should be one if command returns one')

    def test_requires_on_command_callable(self):
        with patch('sys.argv', ['test', 'noop']):
            with Application(ApplicationConfiguration(
                    'test', application_context=ApplicationContext.EXTENDABLE)) as app:

                class Component(object):

                    def get_value(self):
                        return 3

                component('Component')(Component, app.component_manager)

                app.command = REQUIRES_COMMAND
                exit_code = app.execute_command()
                self.assertEqual(exit_code, 3, 'exit code should be one if command returns one')
