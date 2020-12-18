import unittest
from unittest.mock import patch

from zaf.commands.command import CommandId
from zaf.config.manager import ConfigManager
from zaf.config.options import ConfigOption, ConfigOptionId
from zaf.config.types import Count, Flag

from ..click import ClickParseCli


class TestCompleteParser(unittest.TestCase):

    def setUp(self):
        self.plugin = ClickParseCli({}, {})
        self.config = ConfigManager()

    def test_exit_when_required_option_does_not_exist(self):
        with patch('sys.argv', ['zaf', 'command']):
            with self.assertRaises(SystemExit):
                self.plugin.get_config(self.config, [REQUIRED], {COMMAND: []})

    def test_do_not_exit_when_required_option_exists(self):
        with patch('sys.argv', ['zaf', '--required', 'required', 'command']):
            self.plugin.get_config(self.config, [REQUIRED], {COMMAND: []})

    def test_default_value_taken_from_config(self):
        self.config.set(REQUIRED.option_id, 'required')
        with patch('sys.argv', ['zaf', 'command']):
            self.plugin.get_config(self.config, [REQUIRED], {COMMAND: []})

    def test_default_value_not_included_in_result(self):
        self.config.set(REQUIRED.option_id, 'required')
        with patch('sys.argv', ['zaf', '--required', 'required', 'command']):
            extension_config = self.plugin.get_config(self.config, [REQUIRED], {COMMAND: []})
            self.assertNotIn('required', extension_config.config)

    def test_value_included_in_result_when_different_than_default(self):
        self.config.set(REQUIRED.option_id, 'required')
        with patch('sys.argv', ['zaf', '--required', 'required2', 'command']):
            extension_config = self.plugin.get_config(self.config, [REQUIRED], {COMMAND: []})
            self.assertEqual(extension_config.config['required'], 'required2')

    def test_exit_when_required_command_option_does_not_exist(self):
        with patch('sys.argv', ['zaf', 'command']):
            with self.assertRaises(SystemExit):
                self.plugin.get_config(self.config, [], {COMMAND: [REQUIRED]})

    def test_do_not_exit_when_required_command_option_exists(self):
        with patch('sys.argv', ['zaf', 'command', '--required', 'required']):
            self.plugin.get_config(self.config, [], {COMMAND: [REQUIRED]})

    def test_default_value_taken_from_config_for_command_option(self):
        self.config.set(REQUIRED.option_id, 'required')
        with patch('sys.argv', ['zaf', 'command']):
            self.plugin.get_config(self.config, [], {COMMAND: [REQUIRED]})

    def test_command_option_value_included_in_result_when_different_than_default(self):
        self.config.set(REQUIRED.option_id, 'required')
        with patch('sys.argv', ['zaf', 'command', '--required', 'required2']):
            extension_config = self.plugin.get_config(self.config, [], {COMMAND: [REQUIRED]})
            self.assertEqual(extension_config.config['required'], 'required2')

    def test_command_option_with_entity_dependency(self):
        self.config.set(ENTITY_IDS, ['entity1', 'entity2'])
        with patch('sys.argv', ['zaf', 'command', '--entities-entity1@dependent', 'dependent1',
                                '--entities-entity2@dependent', 'dependent2']):
            extension_config = self.plugin.get_config(self.config, [], {COMMAND: [DEPENDENT]})
            self.assertEqual(extension_config.config['entities.entity1.dependent'], 'dependent1')
            self.assertEqual(extension_config.config['entities.entity2.dependent'], 'dependent2')

    def test_command_option_with_single_value_entity_dependency(self):
        self.config.set(SINGLE_ENTITY_ID, 'entity1')
        with patch('sys.argv', ['zaf', 'command', '--single-entity1@dependent', 'dependent1']):
            extension_config = self.plugin.get_config(
                self.config, [], {
                    COMMAND: [SINGLE_DEPENDENT]
                })
            self.assertEqual(extension_config.config['single.entity1.dependent'], 'dependent1')

    def test_missing_required_argument(self):
        with patch('sys.argv', ['zaf', 'command']):
            with self.assertRaises(SystemExit):
                self.plugin.get_config(
                    self.config, [], {
                        COMMAND: [ConfigOption(REQUIRED_ARGUMENT, required=True)]
                    })

    def test_missing_required_argument_with_default_value_is_not_parsed_and_default_value_is_kept(
            self):
        self.config.set(REQUIRED_ARGUMENT, 'DEFAULT_ARG')
        with patch('sys.argv', ['zaf', 'command']):
            extension_config = self.plugin.get_config(
                self.config, [], {
                    COMMAND: [ConfigOption(REQUIRED_ARGUMENT, required=True)]
                })
            self.assertNotIn('required.arg', extension_config)

    def test_command_required_argument_exist(self):
        with patch('sys.argv', ['zaf', 'command', 'ARG']):
            extension_config = self.plugin.get_config(
                self.config, [], {
                    COMMAND: [ConfigOption(REQUIRED_ARGUMENT, required=True)]
                })
            self.assertEqual(extension_config.config['required.arg'], 'ARG')


class TestFlag(unittest.TestCase):

    def setUp(self):
        self.plugin = ClickParseCli({}, {})
        self.config = ConfigManager()

    def test_flag_value_included_in_result_when_true_and_default_is_false(self):
        self.config.set(FLAG.option_id, False)
        with patch('sys.argv', ['zaf', '--flag', 'command']):
            extension_config = self.plugin.get_config(self.config, [FLAG], {COMMAND: []})
            self.assertIn('flag', extension_config.config)

    def test_flag_value_included_in_result_when_true_and_default_is_none(self):
        self.config.set(FLAG.option_id, None)
        with patch('sys.argv', ['zaf', '--flag', 'command']):
            extension_config = self.plugin.get_config(self.config, [FLAG], {COMMAND: []})
            self.assertIn('flag', extension_config.config)

    def test_flag_value_not_included_in_result_when_true_and_default_is_true(self):
        self.config.set(FLAG.option_id, True)
        with patch('sys.argv', ['zaf', '--flag', 'command']):
            extension_config = self.plugin.get_config(self.config, [FLAG], {COMMAND: []})
            self.assertNotIn('flag', extension_config.config)

    def test_flag_value_included_in_result_when_false_and_default_is_true(self):
        self.config.set(FLAG.option_id, True)
        with patch('sys.argv', ['zaf', '--no-flag', 'command']):
            extension_config = self.plugin.get_config(self.config, [FLAG], {COMMAND: []})
            self.assertIn('flag', extension_config.config)

    def test_flag_value_included_in_result_when_false_and_default_is_none(self):
        self.config.set(FLAG.option_id, None)
        with patch('sys.argv', ['zaf', '--no-flag', 'command']):
            extension_config = self.plugin.get_config(self.config, [FLAG], {COMMAND: []})
            self.assertIn('flag', extension_config.config)

    def test_flag_value_not_included_in_result_when_false_and_default_is_false(self):
        self.config.set(FLAG.option_id, False)
        with patch('sys.argv', ['zaf', '--no-flag', 'command']):
            extension_config = self.plugin.get_config(self.config, [FLAG], {COMMAND: []})
            self.assertNotIn('flag', extension_config.config)

    def test_flag_value_not_included_in_result_when_not_given_and_default_is_true(self):
        self.config.set(FLAG.option_id, True)
        with patch('sys.argv', ['zaf', 'command']):
            extension_config = self.plugin.get_config(self.config, [FLAG], {COMMAND: []})
            self.assertNotIn('flag', extension_config.config)

    def test_flag_value_not_included_in_result_when_not_given_and_default_is_false(self):
        self.config.set(FLAG.option_id, False)
        with patch('sys.argv', ['zaf', 'command']):
            extension_config = self.plugin.get_config(self.config, [FLAG], {COMMAND: []})
            self.assertNotIn('flag', extension_config.config)

    def test_flag_value_not_included_in_result_when_not_given_and_default_is_none(self):
        self.config.set(FLAG.option_id, None)
        with patch('sys.argv', ['zaf', 'command']):
            extension_config = self.plugin.get_config(self.config, [FLAG], {COMMAND: []})
            self.assertNotIn('flag', extension_config.config)

    def test_command_flag_value_included_in_result_when_true_and_default_is_false(self):
        self.config.set(FLAG.option_id, False)
        with patch('sys.argv', ['zaf', 'command', '--flag']):
            extension_config = self.plugin.get_config(self.config, [], {COMMAND: [FLAG]})
            self.assertIn('flag', extension_config.config)

    def test_command_flag_value_included_in_result_when_true_and_default_is_none(self):
        self.config.set(FLAG.option_id, None)
        with patch('sys.argv', ['zaf', 'command', '--flag']):
            extension_config = self.plugin.get_config(self.config, [], {COMMAND: [FLAG]})
            self.assertIn('flag', extension_config.config)

    def test_command_flag_value_not_included_in_result_when_true_and_default_is_true(self):
        self.config.set(FLAG.option_id, True)
        with patch('sys.argv', ['zaf', 'command', '--flag']):
            extension_config = self.plugin.get_config(self.config, [], {COMMAND: [FLAG]})
            self.assertNotIn('flag', extension_config.config)

    def test_command_flag_value_included_in_result_when_false_and_default_is_true(self):
        self.config.set(FLAG.option_id, True)
        with patch('sys.argv', ['zaf', 'command', '--no-flag']):
            extension_config = self.plugin.get_config(self.config, [], {COMMAND: [FLAG]})
            self.assertIn('flag', extension_config.config)

    def test_command_flag_value_included_in_result_when_false_and_default_is_none(self):
        self.config.set(FLAG.option_id, None)
        with patch('sys.argv', ['zaf', 'command', '--no-flag']):
            extension_config = self.plugin.get_config(self.config, [], {COMMAND: [FLAG]})
            self.assertIn('flag', extension_config.config)

    def test_command_flag_value_not_included_in_result_when_false_and_default_is_false(self):
        self.config.set(FLAG.option_id, False)
        with patch('sys.argv', ['zaf', 'command', '--no-flag']):
            extension_config = self.plugin.get_config(self.config, [], {COMMAND: [FLAG]})
            self.assertNotIn('flag', extension_config.config)

    def test_command_flag_value_not_included_in_result_when_not_given_and_default_is_true(self):
        self.config.set(FLAG.option_id, True)
        with patch('sys.argv', ['zaf', 'command']):
            extension_config = self.plugin.get_config(self.config, [], {COMMAND: [FLAG]})
            self.assertNotIn('flag', extension_config.config)

    def test_command_flag_value_not_included_in_result_when_not_given_and_default_is_false(self):
        self.config.set(FLAG.option_id, False)
        with patch('sys.argv', ['zaf', 'command']):
            extension_config = self.plugin.get_config(self.config, [], {COMMAND: [FLAG]})
            self.assertNotIn('flag', extension_config.config)

    def test_command_flag_value_not_included_in_result_when_not_given_and_default_is_none(self):
        self.config.set(FLAG.option_id, None)
        with patch('sys.argv', ['zaf', 'command']):
            extension_config = self.plugin.get_config(self.config, [], {COMMAND: [FLAG]})
            self.assertNotIn('flag', extension_config.config)


class TestSubCommand(unittest.TestCase):

    def setUp(self):
        self.plugin = ClickParseCli({}, {})
        self.config = ConfigManager()

    def test_sub_command_with_options(self):
        self.config.set(REQUIRED.option_id, None)
        self.config.set(REQUIRED_ARGUMENT, None)
        with patch('sys.argv',
                   ['zaf', 'parent', '--required', 'required', 'child', 'REQUIRED_ARGUMENT']):
            extension_config = self.plugin.get_config(
                self.config, [], {
                    PARENT_COMMAND: [REQUIRED],
                    CHILD_COMMAND: [ConfigOption(REQUIRED_ARGUMENT, required=True)]
                })
            self.assertIn('required', extension_config.config)
            self.assertIn('required.arg', extension_config.config)
            self.assertEqual(extension_config.config['internal.command'], 'child')

    def test_sub_sub_command_with_options(self):
        self.config.set(REQUIRED.option_id, None)
        self.config.set(REQUIRED_ARGUMENT, None)
        self.config.set(FLAG.option_id, False)
        with patch('sys.argv', ['zaf', 'parent', '--required', 'required', 'child',
                                'REQUIRED_ARGUMENT', 'grandchild', '--flag']):
            extension_config = self.plugin.get_config(
                self.config, [], {
                    PARENT_COMMAND: [REQUIRED],
                    CHILD_COMMAND: [ConfigOption(REQUIRED_ARGUMENT, required=True)],
                    GRAND_CHILD_COMMAND: [FLAG],
                })
            self.assertIn('required', extension_config.config)
            self.assertIn('required.arg', extension_config.config)
            self.assertIn('flag', extension_config.config)
            self.assertEqual(extension_config.config['internal.command'], 'grandchild')

    def test_options_short_name(self):
        self.config.set(REQUIRED.option_id, None)
        self.config.set(REQUIRED_ARGUMENT, None)
        self.config.set(FLAG.option_id, False)
        with patch('sys.argv', ['zaf', 'parent', '--required', 'required', 'child',
                                'REQUIRED_ARGUMENT', 'grandchild', '--flag']):
            extension_config = self.plugin.get_config(
                self.config, [], {
                    PARENT_COMMAND: [REQUIRED],
                    CHILD_COMMAND: [ConfigOption(REQUIRED_ARGUMENT, required=True)],
                    GRAND_CHILD_COMMAND: [FLAG],
                })
            self.assertIn('required', extension_config.config)
            self.assertIn('required.arg', extension_config.config)
            self.assertIn('flag', extension_config.config)
            self.assertEqual(extension_config.config['internal.command'], 'grandchild')


class TestShortAlias(unittest.TestCase):

    def setUp(self):
        self.plugin = ClickParseCli({}, {})
        self.config = ConfigManager()

    def test_long_option_can_be_used_when_option_id_specifies_short_alias(self):
        self.config.set(SHORT_ALIAS_OPTION.option_id, None)
        with patch('sys.argv', ['zaf', '--namespace-short-alias', 'value', 'command']):
            extension_config = self.plugin.get_config(
                self.config, [SHORT_ALIAS_OPTION], {
                    COMMAND: []
                })
            self.assertIn('namespace.short.alias', extension_config.config)

    def test_short_alias_can_be_used_when_option_id_specifies_short_alias(self):
        self.config.set(SHORT_ALIAS_OPTION.option_id, None)
        with patch('sys.argv', ['zaf', '--short-alias', 'value', 'command']):
            extension_config = self.plugin.get_config(
                self.config, [SHORT_ALIAS_OPTION], {
                    COMMAND: []
                })
            self.assertIn('namespace.short.alias', extension_config.config)

    def test_command_long_option_can_be_used_when_option_id_specifies_short_alias(self):
        self.config.set(SHORT_ALIAS_OPTION.option_id, None)
        with patch('sys.argv', ['zaf', 'command', '--namespace-short-alias', 'value']):
            extension_config = self.plugin.get_config(
                self.config, [], {
                    COMMAND: [SHORT_ALIAS_OPTION]
                })
            self.assertIn('namespace.short.alias', extension_config.config)

    def test_command_short_alias_can_be_used_when_option_id_specifies_short_alias(self):
        self.config.set(SHORT_ALIAS_OPTION.option_id, None)
        with patch('sys.argv', ['zaf', 'command', '--short-alias', 'value']):
            extension_config = self.plugin.get_config(
                self.config, [], {
                    COMMAND: [SHORT_ALIAS_OPTION]
                })
            self.assertIn('namespace.short.alias', extension_config.config)

    def test_long_flag_can_be_used_when_option_id_specifies_short_alias(self):
        self.config.set(SHORT_ALIAS_FLAG.option_id, False)
        with patch('sys.argv', ['zaf', '--namespace-short-alias', 'command']):
            extension_config = self.plugin.get_config(
                self.config, [SHORT_ALIAS_FLAG], {
                    COMMAND: []
                })
            self.assertIn('namespace.short.alias', extension_config.config)

    def test_long_no_flag_can_be_used_when_option_id_specifies_short_alias(self):
        self.config.set(SHORT_ALIAS_FLAG.option_id, True)
        with patch('sys.argv', ['zaf', '--no-namespace-short-alias', 'command']):
            extension_config = self.plugin.get_config(
                self.config, [SHORT_ALIAS_FLAG], {
                    COMMAND: []
                })
            self.assertIn('namespace.short.alias', extension_config.config)

    def test_short_alias_flag_can_be_used_when_option_id_specifies_short_alias(self):
        self.config.set(SHORT_ALIAS_FLAG.option_id, False)
        with patch('sys.argv', ['zaf', '--namespace-short-alias', 'command']):
            extension_config = self.plugin.get_config(
                self.config, [SHORT_ALIAS_FLAG], {
                    COMMAND: []
                })
            self.assertIn('namespace.short.alias', extension_config.config)

    def test_short_alias_no_flag_can_be_used_when_option_id_specifies_short_alias(self):
        self.config.set(SHORT_ALIAS_FLAG.option_id, True)
        with patch('sys.argv', ['zaf', '--no-short-alias', 'command']):
            extension_config = self.plugin.get_config(
                self.config, [SHORT_ALIAS_FLAG], {
                    COMMAND: []
                })
            self.assertIn('namespace.short.alias', extension_config.config)

    def test_command_long_flag_can_be_used_when_option_id_specifies_short_alias(self):
        self.config.set(SHORT_ALIAS_FLAG.option_id, False)
        with patch('sys.argv', ['zaf', 'command', '--namespace-short-alias']):
            extension_config = self.plugin.get_config(
                self.config, [], {
                    COMMAND: [SHORT_ALIAS_FLAG]
                })
            self.assertIn('namespace.short.alias', extension_config.config)

    def test_command_long_no_flag_can_be_used_when_option_id_specifies_short_alias(self):
        self.config.set(SHORT_ALIAS_FLAG.option_id, True)
        with patch('sys.argv', ['zaf', 'command', '--no-namespace-short-alias']):
            extension_config = self.plugin.get_config(
                self.config, [], {
                    COMMAND: [SHORT_ALIAS_FLAG]
                })
            self.assertIn('namespace.short.alias', extension_config.config)

    def test_command_short_alias_flag_can_be_used_when_option_id_specifies_short_alias(self):
        self.config.set(SHORT_ALIAS_FLAG.option_id, False)
        with patch('sys.argv', ['zaf', 'command', '--namespace-short-alias']):
            extension_config = self.plugin.get_config(
                self.config, [], {
                    COMMAND: [SHORT_ALIAS_FLAG]
                })
            self.assertIn('namespace.short.alias', extension_config.config)

    def test_command_short_alias_no_flag_can_be_used_when_option_id_specifies_short_alias(self):
        self.config.set(SHORT_ALIAS_FLAG.option_id, True)
        with patch('sys.argv', ['zaf', 'command', '--no-short-alias']):
            extension_config = self.plugin.get_config(
                self.config, [], {
                    COMMAND: [SHORT_ALIAS_FLAG]
                })
            self.assertIn('namespace.short.alias', extension_config.config)


class TestShortName(unittest.TestCase):

    def setUp(self):
        self.plugin = ClickParseCli({}, {})
        self.config = ConfigManager()

    def test_long_option_can_be_used_when_option_id_specifies_short_name(self):
        self.config.set(SHORT_NAME_OPTION.option_id, None)
        with patch('sys.argv', ['zaf', '--short-name', 'value', 'command']):
            extension_config = self.plugin.get_config(
                self.config, [SHORT_NAME_OPTION], {
                    COMMAND: []
                })
            self.assertIn('short.name', extension_config.config)

    def test_short_name_can_be_used_when_option_id_specifies_short_name(self):
        self.config.set(SHORT_NAME_OPTION.option_id, None)
        with patch('sys.argv', ['zaf', '-s', 'value', 'command']):
            extension_config = self.plugin.get_config(
                self.config, [SHORT_NAME_OPTION], {
                    COMMAND: []
                })
            self.assertIn('short.name', extension_config.config)

    def test_command_long_option_can_be_used_when_option_id_specifies_short_name(self):
        self.config.set(SHORT_NAME_OPTION.option_id, None)
        with patch('sys.argv', ['zaf', 'command', '--short-name', 'value']):
            extension_config = self.plugin.get_config(
                self.config, [], {
                    COMMAND: [SHORT_NAME_OPTION]
                })
            self.assertIn('short.name', extension_config.config)

    def test_command_short_name_can_be_used_when_option_id_specifies_short_name(self):
        self.config.set(SHORT_NAME_OPTION.option_id, None)
        with patch('sys.argv', ['zaf', 'command', '-s', 'value']):
            extension_config = self.plugin.get_config(
                self.config, [], {
                    COMMAND: [SHORT_NAME_OPTION]
                })
            self.assertIn('short.name', extension_config.config)

    def test_long_flag_can_be_used_when_option_id_specifies_short_name(self):
        self.config.set(SHORT_NAME_FLAG.option_id, False)
        with patch('sys.argv', ['zaf', '--short-name', 'command']):
            extension_config = self.plugin.get_config(self.config, [SHORT_NAME_FLAG], {COMMAND: []})
            self.assertIn('short.name', extension_config.config)

    def test_long_no_flag_can_be_used_when_option_id_specifies_short_name(self):
        self.config.set(SHORT_NAME_FLAG.option_id, True)
        with patch('sys.argv', ['zaf', '--no-short-name', 'command']):
            extension_config = self.plugin.get_config(self.config, [SHORT_NAME_FLAG], {COMMAND: []})
            self.assertIn('short.name', extension_config.config)

    def test_short_name_flag_can_be_used_when_option_id_specifies_short_name(self):
        self.config.set(SHORT_NAME_FLAG.option_id, False)
        with patch('sys.argv', ['zaf', '-s', 'command']):
            extension_config = self.plugin.get_config(self.config, [SHORT_NAME_FLAG], {COMMAND: []})
            self.assertIn('short.name', extension_config.config)

    def test_command_long_flag_can_be_used_when_option_id_specifies_short_name(self):
        self.config.set(SHORT_NAME_FLAG.option_id, False)
        with patch('sys.argv', ['zaf', 'command', '--short-name']):
            extension_config = self.plugin.get_config(self.config, [], {COMMAND: [SHORT_NAME_FLAG]})
            self.assertIn('short.name', extension_config.config)

    def test_command_long_no_flag_can_be_used_when_option_id_specifies_short_name(self):
        self.config.set(SHORT_NAME_FLAG.option_id, True)
        with patch('sys.argv', ['zaf', 'command', '--no-short-name']):
            extension_config = self.plugin.get_config(self.config, [], {COMMAND: [SHORT_NAME_FLAG]})
            self.assertIn('short.name', extension_config.config)

    def test_command_short_name_flag_can_be_used_when_option_id_specifies_short_name(self):
        self.config.set(SHORT_NAME_FLAG.option_id, False)
        with patch('sys.argv', ['zaf', 'command', '-s']):
            extension_config = self.plugin.get_config(self.config, [], {COMMAND: [SHORT_NAME_FLAG]})
            self.assertIn('short.name', extension_config.config)


class TestAllowUnknownOptions(unittest.TestCase):

    def setUp(self):
        self.plugin = ClickParseCli({}, {})
        self.config = ConfigManager()

    def test_command_allow_unknown_option(self):
        with patch('sys.argv', ['zaf', 'command-unknown', '--unknown']):
            self.plugin.get_config(self.config, [], {COMMAND_ALLOW_UNKNOWN: []})

    def test_command_not_allow_unknown_option(self):
        with self.assertRaises(SystemExit):
            with patch('sys.argv', ['zaf', 'command', '--unknown']):
                self.plugin.get_config(self.config, [], {COMMAND: []})

    def test_duplicate_unknown_options_are_kept(self):
        with patch('sys.argv', ['zaf', 'command-unknown', '--duplicate1', '--duplicate1', '-d',
                                '-d', 'duplicate2', 'duplicate2']):
            extension_config = self.plugin.get_config(
                self.config, [], {
                    COMMAND_ALLOW_AND_CAPTURE_UNKNOWN: [MULTIPLE_ARGUEMENTS]
                })
            self.assertEqual(
                extension_config.config['multiple.args'],
                ('--duplicate1', '--duplicate1', '-d', '-d', 'duplicate2', 'duplicate2'))


class TestCount(unittest.TestCase):

    def setUp(self):
        self.plugin = ClickParseCli({}, {})
        self.config = ConfigManager()

    def test_count_zero_will_not_override_default_value(self):
        count_option = ConfigOption(
            ConfigOptionId('count', '', option_type=Count(0, 1)), required=False)
        self.config.set(count_option.option_id, 1)

        with patch('sys.argv', ['zaf', 'command']):
            extension_config = self.plugin.get_config(self.config, [count_option], {COMMAND: []})
            self.assertNotIn('count', extension_config.config)

    def test_count_1_not_included_in_config_if_same_as_default(self):
        count_option = ConfigOption(
            ConfigOptionId('count', '', option_type=Count(0, 1)), required=False)
        self.config.set(count_option.option_id, 1)

        with patch('sys.argv', ['zaf', '--count', 'command']):
            extension_config = self.plugin.get_config(self.config, [count_option], {COMMAND: []})
            self.assertNotIn('count', extension_config.config)

    def test_count_not_zero_included_in_config_if_not_same_as_default(self):
        count_option = ConfigOption(
            ConfigOptionId('count', '', option_type=Count(0, 1)), required=False)
        self.config.set(count_option.option_id, 0)

        with patch('sys.argv', ['zaf', '--count', 'command']):
            extension_config = self.plugin.get_config(self.config, [count_option], {COMMAND: []})
            self.assertIn('count', extension_config.config)
            self.assertEqual(extension_config.config['count'], 1)

    def test_count_can_be_given_multiple_times(self):
        count_option = ConfigOption(
            ConfigOptionId('count', '', option_type=Count(0, 2)), required=False)
        self.config.set(count_option.option_id, 0)

        with patch('sys.argv', ['zaf', '--count', '--count', 'command']):
            extension_config = self.plugin.get_config(self.config, [count_option], {COMMAND: []})
            self.assertIn('count', extension_config.config)
            self.assertEqual(extension_config.config['count'], 2)

    def test_count_overrides_non_zero_default_value(self):
        count_option = ConfigOption(
            ConfigOptionId('count', '', option_type=Count(0, 2)), required=False)
        self.config.set(count_option.option_id, 1)

        with patch('sys.argv', ['zaf', '--count', '--count', 'command']):
            extension_config = self.plugin.get_config(self.config, [count_option], {COMMAND: []})
            self.assertIn('count', extension_config.config)
            self.assertEqual(extension_config.config['count'], 2)

    def test_count_clamped_to_max_value(self):
        count_option = ConfigOption(
            ConfigOptionId('count', '', option_type=Count(0, 1)), required=False)
        self.config.set(count_option.option_id, 0)

        with patch('sys.argv', ['zaf', '--count', '--count', 'command']):
            extension_config = self.plugin.get_config(self.config, [count_option], {COMMAND: []})
            self.assertIn('count', extension_config.config)
            self.assertEqual(extension_config.config['count'], 1)


COMMAND = CommandId('command', '', callable=None, config_options=[])
COMMAND_ALLOW_UNKNOWN = CommandId(
    'command-unknown', '', callable=None, config_options=[], allow_unknown_options=True)
REQUIRED = ConfigOption(ConfigOptionId('required', ''), required=True)
ENTITY_IDS = ConfigOptionId('ids', '', entity=True, multiple=True, namespace='entities')
DEPENDENT = ConfigOption(ConfigOptionId('dependent', '', at=ENTITY_IDS), required=True)
REQUIRED_ARGUMENT = ConfigOptionId('required.arg', '', argument=True)
SINGLE_ENTITY_ID = ConfigOptionId('id', '', entity=True, multiple=False, namespace='single')
SINGLE_DEPENDENT = ConfigOption(ConfigOptionId('dependent', '', at=SINGLE_ENTITY_ID), required=True)
FLAG = ConfigOption(ConfigOptionId('flag', '', option_type=Flag()), required=False)
SHORT_ALIAS_OPTION = ConfigOption(
    ConfigOptionId('short.alias', '', short_alias=True, namespace='namespace'), required=False)
SHORT_ALIAS_FLAG = ConfigOption(
    ConfigOptionId('short.alias', '', option_type=Flag(), short_alias=True, namespace='namespace'),
    required=False)
SHORT_NAME_OPTION = ConfigOption(ConfigOptionId('short.name', '', short_name='s'), required=False)
SHORT_NAME_FLAG = ConfigOption(
    ConfigOptionId('short.name', '', option_type=Flag(), short_name='s'), required=False)
PARENT_COMMAND = CommandId('parent', '', callable=None, config_options=[])
CHILD_COMMAND = CommandId('child', '', callable=None, config_options=[], parent=PARENT_COMMAND)
GRAND_CHILD_COMMAND = CommandId(
    'grandchild', '', callable=None, config_options=[], parent=CHILD_COMMAND)
MULTIPLE_ARGUEMENTS = ConfigOption(
    ConfigOptionId('multiple.args', '', argument=True, multiple=True), required=True)
COMMAND_ALLOW_AND_CAPTURE_UNKNOWN = CommandId(
    'command-unknown',
    '',
    callable=None,
    config_options=[MULTIPLE_ARGUEMENTS],
    allow_unknown_options=True)
