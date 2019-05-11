import unittest

from zaf.builtin.click.check_duplicates import DuplicateOptionException, \
    check_for_ambiguous_duplicates
from zaf.builtin.click.test.test_complete_parser import COMMAND
from zaf.commands.command import CommandId
from zaf.config.options import ConfigOption, ConfigOptionId

unique_id_counter = 0


class TestCheckDuplicateOptions(unittest.TestCase):

    def test_framework_options_with_same_name_raises_duplicate_option_exception(self):
        with self.assertRaises(DuplicateOptionException):
            check_for_ambiguous_duplicates('zaf', [option('name'), option('name')], {})

    def test_framework_options_with_name_same_as_short_alias_raises_duplicate_option_exception(
            self):
        with self.assertRaises(DuplicateOptionException):
            check_for_ambiguous_duplicates(
                'zaf', [option('name'), option('name', namespace='namespace')], {})

    def test_framework_options_with_same_short_name_raises_duplicate_option_exception(self):
        with self.assertRaises(DuplicateOptionException):
            check_for_ambiguous_duplicates(
                'zaf', [option('name1', short_name='n'),
                        option('name2', short_name='n')], {})

    def test_framework_option_with_same_name_as_command_option_raises_duplicate_option_exception(
            self):
        with self.assertRaises(DuplicateOptionException):
            check_for_ambiguous_duplicates('zaf', [option('name')], {COMMAND: [option('name')]})

    def test_framework_options_with_same_name_as_command_option_short_alias_raises_duplicate_option_exception(
            self):
        with self.assertRaises(DuplicateOptionException):
            check_for_ambiguous_duplicates(
                'zaf', [option('name')], {
                    COMMAND: [option('name', namespace='namespace')]
                })

    def test_framework_options_with_same_short_alias_as_command_option_name_raises_duplicate_option_exception(
            self):
        with self.assertRaises(DuplicateOptionException):
            check_for_ambiguous_duplicates(
                'zaf', [option('name', namespace='namespace')], {
                    COMMAND: [option('name')]
                })

    def test_framework_options_with_short_name_as_command_option_raises_duplicate_option_exception(
            self):
        with self.assertRaises(DuplicateOptionException):
            check_for_ambiguous_duplicates(
                'zaf', [option('name1', short_name='n')], {
                    COMMAND: [option('name2', short_name='n')]
                })

    def test_commands_options_on_same_command_with_same_name_raises_duplicate_option_exception(
            self):
        with self.assertRaises(DuplicateOptionException):
            check_for_ambiguous_duplicates('zaf', [], {COMMAND: [option('name'), option('name')]})

    def test_commands_options_on_same_command_with_name_same_as_short_alias_raises_duplicate_option_exception(
            self):
        with self.assertRaises(DuplicateOptionException):
            check_for_ambiguous_duplicates(
                'zaf', [], {
                    COMMAND: [option('name'), option('name', namespace='namespace')]
                })

    def test_commands_options_on_same_command_with_same_short_name_raises_duplicate_option_exception(
            self):
        with self.assertRaises(DuplicateOptionException):
            check_for_ambiguous_duplicates(
                'zaf', [], {
                    COMMAND: [option('name1', short_name='n'),
                              option('name2', short_name='n')]
                })

    def test_commands_options_on_different_commands_with_same_name_does_not_raise_exception(self):
        check_for_ambiguous_duplicates(
            'zaf', [], {
                COMMAND: [option('name')],
                COMMAND2: [option('name')]
            })

    def test_commands_options_on_different_commands_with_name_same_as_short_alias_does_not_raise_exception(
            self):
        check_for_ambiguous_duplicates(
            'zaf', [], {
                COMMAND: [option('name')],
                COMMAND2: [option('name', namespace='namespace')]
            })

    def test_commands_options_on_different_commands_with_same_short_name_does_not_raise_exception(
            self):
        check_for_ambiguous_duplicates(
            'zaf', [], {
                COMMAND: [option('name1', short_name='n')],
                COMMAND2: [option('name2', short_name='n')]
            })


def option(name, namespace=None, short_name=None):
    global unique_id_counter
    unique_id_counter += 1
    return ConfigOption(
        ConfigOptionId(
            name,
            str(unique_id_counter),
            namespace=namespace,
            short_alias=bool(namespace),
            short_name=short_name),
        required=True)


COMMAND2 = CommandId('command2', '', callable=None, config_options=[])
