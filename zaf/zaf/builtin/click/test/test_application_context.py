import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

from zaf.application import APPLICATION_CONTEXT, ApplicationContext
from zaf.commands.command import CommandId
from zaf.config.manager import ConfigManager
from zaf.config.options import ConfigOption, ConfigOptionId

from ..click import ClickParseCli


class TestApplicationContext(unittest.TestCase):

    def setUp(self):
        self.plugin = ClickParseCli({}, {})
        self.config = ConfigManager()
        self.options = [OPTION_INTERNAL, OPTION_EXTENDABLE, OPTION_NONE]
        self.commands_with_options = {
            COMMAND_INTERNAL: [OPTION_INTERNAL, OPTION_EXTENDABLE, OPTION_NONE],
            COMMAND_EXTENDABLE: [OPTION_INTERNAL, OPTION_EXTENDABLE, OPTION_NONE],
            COMMAND_NONE: [OPTION_INTERNAL, OPTION_EXTENDABLE, OPTION_NONE],
        }

    def test_internal_options_not_included_on_cli(self):
        self.config.set(APPLICATION_CONTEXT, ApplicationContext.EXTENDABLE.name)
        self.assert_not_in_help('internaloption')

    def test_internal_commands_not_included_on_cli(self):
        self.config.set(APPLICATION_CONTEXT, ApplicationContext.EXTENDABLE.name)
        self.assert_not_in_help('internalcommand')

    def test_extendable_options_not_included_on_cli_in_standalone_application(self):
        self.config.set(APPLICATION_CONTEXT, ApplicationContext.STANDALONE.name)
        self.assert_not_in_help('extendableoption')

    def test_extendable_commands_not_included_on_cli_in_standalone_application(self):
        self.config.set(APPLICATION_CONTEXT, ApplicationContext.STANDALONE.name)
        self.assert_not_in_help('extendablecommand')

    def test_extendable_options_included_on_cli_in_extendable_application(self):
        self.config.set(APPLICATION_CONTEXT, ApplicationContext.EXTENDABLE.name)
        self.assert_in_help('extendableoption')

    def test_extendable_commands_included_on_cli_in_extendable_application(self):
        self.config.set(APPLICATION_CONTEXT, ApplicationContext.EXTENDABLE.name)
        self.assert_in_help('extendablecommand')

    def test_none_options_included_on_cli_in_standalone_application(self):
        self.config.set(APPLICATION_CONTEXT, ApplicationContext.STANDALONE.name)
        self.assert_in_help('noneoption')

    def test_none_commands_included_on_cli_in_standalone_application(self):
        self.config.set(APPLICATION_CONTEXT, ApplicationContext.STANDALONE.name)
        self.assert_in_help('nonecommand')

    def assert_not_in_help(self, string):
        self.assert_in_help(string, not_in=True)

    def assert_in_help(self, string, not_in=False):
        help_output = StringIO()

        with patch('sys.argv', ['zaf', '--full-help']), \
                self.assertRaises(SystemExit),\
                redirect_stdout(help_output):
            self.plugin.get_config(self.config, self.options, self.commands_with_options)

        if not_in:
            self.assertNotIn(string, help_output.getvalue(), msg=help_output.getvalue())
        else:
            self.assertIn(string, help_output.getvalue(), msg=help_output.getvalue())


COMMAND_INTERNAL = CommandId(
    'internalcommand',
    '',
    callable=None,
    config_options=[],
    application_contexts=ApplicationContext.INTERNAL)
COMMAND_EXTENDABLE = CommandId(
    'extendablecommand',
    '',
    callable=None,
    config_options=[],
    application_contexts=ApplicationContext.EXTENDABLE)
COMMAND_NONE = CommandId('nonecommand', '', callable=None, config_options=[])
OPTION_INTERNAL = ConfigOption(
    ConfigOptionId('internaloption', '', application_contexts=ApplicationContext.INTERNAL),
    required=False)
OPTION_EXTENDABLE = ConfigOption(
    ConfigOptionId('extendableoption', '', application_contexts=ApplicationContext.EXTENDABLE),
    required=False)
OPTION_NONE = ConfigOption(ConfigOptionId('noneoption', ''), required=False)
