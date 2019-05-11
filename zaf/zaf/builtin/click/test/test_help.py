import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

from zaf.commands.command import CommandId
from zaf.config.manager import ConfigManager
from zaf.config.options import ConfigOption, ConfigOptionId

from ..click import ClickParseCli


class TestHelp(unittest.TestCase):

    def setUp(self):
        self.plugin = ClickParseCli({}, {})
        self.config = ConfigManager()

    def test_exit_with_exit_code_0_when_help(self):
        with patch('sys.argv', ['zaf', '--help']), \
                self.assertRaises(SystemExit) as e:
            self.plugin.get_config(self.config, [], {COMMAND: []})
            self.assertEqual(e.code, 0)

    def test_exit_with_exit_code_0_when_help_on_command(self):
        with patch('sys.argv', ['zaf', 'mycommand', '--help']), \
                self.assertRaises(SystemExit) as e:
            self.plugin.get_config(self.config, [], {COMMAND: []})
            self.assertEqual(e.code, 0)

    def test_help_includes_command(self):
        self.assert_in_help('mycommand', [], {COMMAND: []})

    def test_help_includes_option(self):
        self.assert_in_help('requiredoption', [OPTION_REQUIRED], {})

    def test_help_on_command_includes_command_option(self):
        self.assert_in_help('requiredoption', [], {COMMAND: [OPTION_REQUIRED]}, command='mycommand')

    def test_help_indicates_that_a_required_option_without_default_value_is_required(self):
        self.assert_in_help('[required]', [OPTION_REQUIRED], {})

    def test_help_indicates_that_a_required_command_option_without_default_value_is_required(self):
        self.assert_in_help('[required]', [], {COMMAND: [OPTION_REQUIRED]}, command='mycommand')

    def test_help_does_not_indicate_that_a_required_option_with_default_value_is_required(self):
        self.assert_not_in_help('[required]', [OPTION_REQUIRED_WITH_DEFAULT], {})

    def test_help_does_indicate_that_a_required_command_option_with_default_value_is_required(self):
        self.assert_not_in_help(
            '[required]', [], {COMMAND: [OPTION_REQUIRED_WITH_DEFAULT]}, command='mycommand')

    def test_help_indicates_option_default_value(self):
        self.assert_in_help('[default: mydefault]', [OPTION_WITH_DEFAULT], {})

    def test_help_indicates_command_option_default_value(self):
        self.assert_in_help(
            '[default: mydefault]', [], {COMMAND: [OPTION_WITH_DEFAULT]}, command='mycommand')

    def test_hidden_command_not_shown_in_help(self):
        self.assert_not_in_help('myhiddencommand', [], {COMMAND_HIDDEN: []})

    def test_hidden_command_shown_in_full_help(self):
        self.assert_in_help('myhiddencommand', [], {COMMAND_HIDDEN: []}, full_help=True)

    def test_hidden_option_not_shown_in_help(self):
        self.assert_not_in_help('hiddenoption', [OPTION_HIDDEN], {})

    def test_hidden_option_shown_in_full_help(self):
        self.assert_in_help('hiddenoption', [OPTION_HIDDEN], {}, full_help=True)

    def test_hidden_command_option_not_shown_in_help(self):
        self.assert_not_in_help('hiddenoption', [], {COMMAND: [OPTION_HIDDEN]}, command='mycommand')

    def test_hidden_command_option_shown_in_full_help(self):
        self.assert_in_help(
            'hiddenoption', [], {COMMAND: [OPTION_HIDDEN]}, command='mycommand', full_help=True)

    def assert_not_in_help(
            self, string, options, commands_with_options, command=None, full_help=False):
        self.assert_in_help(string, options, commands_with_options, command, full_help, not_in=True)

    def assert_in_help(
            self, string, options, commands_with_options, command=None, full_help=False,
            not_in=False):
        help_output = StringIO()

        argv = ['zaf']
        if command:
            argv.append(command)

        if full_help:
            argv.append('--full-help')
        else:
            argv.append('--help')

        with patch('sys.argv', argv), \
                self.assertRaises(SystemExit),\
                redirect_stdout(help_output):
            self.plugin.get_config(self.config, options, commands_with_options)

        if not_in:
            self.assertNotIn(string, help_output.getvalue(), msg=help_output.getvalue())
        else:
            self.assertIn(string, help_output.getvalue(), msg=help_output.getvalue())


COMMAND = CommandId('mycommand', '', callable=None, config_options=[])
COMMAND_HIDDEN = CommandId('myhiddencommand', '', callable=None, config_options=[], hidden=True)
OPTION_REQUIRED = ConfigOption(
    ConfigOptionId(
        'requiredoption',
        '',
    ), required=True)
OPTION_REQUIRED_WITH_DEFAULT = ConfigOption(
    ConfigOptionId('defaultrequiredoption', '', default='mydefault'), required=True)
OPTION_OPTIONAL = ConfigOption(
    ConfigOptionId(
        'optionaloption',
        '',
    ), required=False)
OPTION_WITH_DEFAULT = ConfigOption(
    ConfigOptionId('defaultoption', '', default='mydefault'), required=False)
OPTION_HIDDEN = ConfigOption(ConfigOptionId('hiddenoption', '', hidden=True), required=False)
