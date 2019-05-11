import re
import unittest
from unittest.mock import patch

from zaf.builtin.config.validator import ConfigurationValidator
from zaf.commands import COMMAND
from zaf.commands.command import CommandId
from zaf.config.manager import ConfigManager
from zaf.config.options import ConfigOption, ConfigOptionId
from zaf.config.types import Choice, ConfigChoice, Flag, Path


class TestValidator(unittest.TestCase):

    def setUp(self):
        self.validator = ConfigurationValidator()

    def test_validate_none_value(self):
        self.assert_validate_ok(STR_OPTION, None)

    def test_validate_str_option(self):
        self.assert_validate_ok(STR_OPTION, 'str')

    def test_validate_str_option_fails(self):
        self.assert_validate_fails(
            STR_OPTION, 1, "Option 'str.option' has unexpected type 'int', expected 'str'")

    def test_validate_int_option(self):
        self.assert_validate_ok(INT_OPTION, 1)

    def test_validate_int_option_fails(self):
        self.assert_validate_fails(
            INT_OPTION, 'str', "Option 'int.option' has unexpected type 'str', expected 'int'")

    def test_validate_int_option_fails_on_float(self):
        self.assert_validate_fails(
            INT_OPTION, 1.0, "Option 'int.option' has unexpected type 'float', expected 'int'")

    def test_validate_float_option(self):
        self.assert_validate_ok(FLOAT_OPTION, 1.0)

    def test_validate_float_option_accepts_int_values(self):
        self.assert_validate_ok(FLOAT_OPTION, 1)

    def test_validate_float_option_fails(self):
        self.assert_validate_fails(
            FLOAT_OPTION, 'str',
            "Option 'float.option' has unexpected type 'str', expected 'float'")

    def test_validate_bool_option(self):
        self.assert_validate_ok(BOOL_OPTION, True)

    def test_validate_bool_option_fails(self):
        self.assert_validate_fails(
            BOOL_OPTION, 'str', "Option 'bool.option' has unexpected type 'str', expected 'bool'")

    def test_validate_flag_option(self):
        self.assert_validate_ok(FLAG_OPTION, True)

    def test_validate_flag_option_fails(self):
        self.assert_validate_fails(
            FLAG_OPTION, 'string',
            "Flag 'flag.option' has value 'string' of unexpected type 'str', expected 'bool'")

    def test_validate_path_option(self):
        with patch('os.path.exists', return_value=True):
            self.assert_validate_ok(PATH_OPTION, '/path/to/file')

    def test_validate_path_option_fails(self):
        self.assert_validate_fails(
            PATH_OPTION, 1, "Path has value '1' of unexpected type 'int', expected 'str'")

    def test_validate_path_option_fails_if_expected_path_does_not_exists(self):
        with patch('os.path.exists', return_value=False):
            self.assert_validate_fails(
                PATH_OPTION, '/path/to/file',
                "Path '/path/to/file' for 'path.option' does not exist")

    def test_validate_choice_option(self):
        self.assert_validate_ok(CHOICE_OPTION, '1')

    def test_validate_choice_option_fails(self):
        self.assert_validate_fails(
            CHOICE_OPTION, 1,
            "Choice 'choice.option' has value '1' of unexpected type 'int', expected 'str'")

    def test_validate_choice_option_fails_if_choice_is_not_valid(self):
        self.assert_validate_fails(
            CHOICE_OPTION, '3', "'3' is not a valid Choice for 'choice.option', expected '1, 2'")

    def test_validate_config_choice_option(self):
        self.assert_validate_ok(
            CONFIG_CHOICE_OPTION, '1', '', options={
                MULTIPLE_STR_OPTION: ['1', '2']
            })

    def test_validate_config_choice_option_fails(self):
        self.assert_validate_fails(
            CONFIG_CHOICE_OPTION, 1,
            "ConfigChoice 'config.choice.option' has value '1' of unexpected type 'int', expected 'str'"
        )

    def test_validate_config_choice_option_fails_if_choice_is_not_valid(self):
        self.assert_validate_fails(
            CONFIG_CHOICE_OPTION,
            '3',
            "'3' is not a valid ConfigChoice for 'config.choice.option', expected '1, 2'",
            options={
                MULTIPLE_STR_OPTION: ['1', '2']
            })

    def test_validate_entity_config_option(self):
        self.assert_validate_ok(ENTITY_OPTION, 'entity')

    def test_validate_entity_option_containing_upper_case(self):
        self.assert_validate_fails(
            ENTITY_OPTION, 'A',
            "'A' is not a valid Entity entity.option, entity names must be lower case.")

    def test_validate_entity_option_containing_dash(self):
        self.assert_validate_fails(
            ENTITY_OPTION, '-',
            "'-' is not a valid Entity entity.option, entity names must not contain '-'")

    def test_validate_entity_option_containing_underscore(self):
        self.assert_validate_fails(
            ENTITY_OPTION, '_',
            "'_' is not a valid Entity entity.option, entity names must not contain '_'")

    def test_validate_entity_config_option_fails(self):
        self.assert_validate_fails(
            ENTITY_OPTION, 1,
            "Entity 'entity.option' has value '1' of unexpected type 'int', expected 'str'")

    def test_validate_at_entity_config_option(self):
        self.assert_validate_ok(
            AT_ENTITY_OPTION, 'at_entity', entity='entity', options={
                ENTITY_OPTION: 'entity'
            })

    def test_validate_at_entity_config_option_fails_when_entity_is_of_wrong_type(self):
        self.assert_validate_fails(
            AT_ENTITY_OPTION,
            'at_entity',
            "Entity 'entity.option' has value '1' of unexpected type 'int', expected 'str'",
            entity='entity',
            options={
                ENTITY_OPTION: 1
            })

    def test_validate_at_multiple_entity_config_option(self):
        self.assert_validate_ok(
            AT_MULTIPLE_ENTITY_OPTION,
            'at_entity',
            entity='entity1',
            options={
                MULTIPLE_ENTITY_OPTION: ['entity1', 'entity2']
            })

    def test_transform_does_not_affect_validate(self):
        self.assert_validate_ok(TRANSFORM_OPTION, '2')

    def test_transform_does_not_affect_validate_for_choices(self):
        self.assert_validate_ok(TRANSFORM_CHOICE_OPTION, '2')

    def test_transform_at_entity_option_does_not_affect_validate(self):
        self.assert_validate_ok(
            TRANSFORM_AT_ENTITY_OPTION, '1', entity='entity', options={
                ENTITY_OPTION: 'entity'
            })

    def test_transform_at_multiple_entity_option_does_not_affect_validate(self):
        self.assert_validate_ok(
            TRANSFORM_AT_MULTIPLE_ENTITY_OPTION,
            1,
            entity='entity1',
            options={
                MULTIPLE_ENTITY_OPTION: ['entity1', 'entity2']
            })

    def test_validate_at_entity_option_with_transform(self):
        self.assert_validate_ok(
            AT_TRANSFORMED_ENTITY_OPTION,
            'at_entity',
            entity='11',
            options={
                TRANSFORMED_ENTITY_OPTION: ['1', '2']
            })

    def assert_validate_ok(self, option, value, entity=None, options={}):
        config = create_config(
            {
                option.option_id: value,
                COMMAND: 'cmd'
            }, entity=entity, additional_options=options)
        self.validator.get_config(config, [option], {CMD: []})
        self.validator.get_config(config, [], {CMD: [option]})

    def assert_validate_fails(self, option, value, message, entity=None, options={}):
        config = create_config(
            {
                option.option_id: value,
                COMMAND: 'cmd'
            }, entity=entity, additional_options=options)
        regex = '^{msg}$'.format(msg=re.escape(message))
        all_options = [option]
        all_options.extend(options.keys())
        with self.assertRaisesRegex(TypeError, regex):
            self.validator.get_config(config, all_options, {CMD: []})
        with self.assertRaisesRegex(TypeError, regex):
            self.validator.get_config(config, [], {CMD: all_options})


def create_config(options, entity=None, additional_options={}):
    config = ConfigManager()
    for option_id, value in options.items():
        key = config._option_key(option_id, entity)
        config._config[key].add(value, 1, '')
    for option, value in additional_options.items():
        key = config._option_key(option.option_id)
        config._config[key].add(value, 1, '')
    return config


CMD = CommandId('cmd', '', None, [])
MULTIPLE_STR_OPTION = ConfigOption(
    ConfigOptionId('multiple.str.option', '', multiple=True), required=False)
STR_OPTION = ConfigOption(ConfigOptionId('str.option', ''), required=False)
INT_OPTION = ConfigOption(ConfigOptionId('int.option', '', option_type=int), required=False)
FLOAT_OPTION = ConfigOption(ConfigOptionId('float.option', '', option_type=float), required=False)
BOOL_OPTION = ConfigOption(ConfigOptionId('bool.option', '', option_type=bool), required=False)
FLAG_OPTION = ConfigOption(ConfigOptionId('flag.option', '', option_type=Flag()), required=False)
PATH_OPTION = ConfigOption(
    ConfigOptionId('path.option', '', option_type=Path(exists=True)), required=False)
CHOICE_OPTION = ConfigOption(
    ConfigOptionId('choice.option', '', option_type=Choice(['1', '2'])), required=False)
CONFIG_CHOICE_OPTION = ConfigOption(
    ConfigOptionId(
        'config.choice.option', '', option_type=ConfigChoice(MULTIPLE_STR_OPTION.option_id)),
    required=False)
TRANSFORM_OPTION = ConfigOption(
    ConfigOptionId('transform.option', '', transform=lambda s: int(s)), required=False)
TRANSFORM_CHOICE_OPTION = ConfigOption(
    ConfigOptionId('transform.option', '', option_type=Choice(['1', '2']), transform=lambda s: 3),
    required=False)
ENTITY_OPTION = ConfigOption(ConfigOptionId('entity.option', '', entity=True), required=False)
AT_ENTITY_OPTION = ConfigOption(
    ConfigOptionId('at.entity.option', '', at=ENTITY_OPTION.option_id), required=False)
TRANSFORM_AT_ENTITY_OPTION = ConfigOption(
    ConfigOptionId('transform.at.entity.option', '', at=ENTITY_OPTION.option_id, transform=int),
    required=False)
MULTIPLE_ENTITY_OPTION = ConfigOption(
    ConfigOptionId('multiple.entity.option', '', entity=True, multiple=True), required=False)
AT_MULTIPLE_ENTITY_OPTION = ConfigOption(
    ConfigOptionId('multiple.at.entity.option', '', at=MULTIPLE_ENTITY_OPTION.option_id),
    required=False)
TRANSFORM_AT_MULTIPLE_ENTITY_OPTION = ConfigOption(
    ConfigOptionId(
        'transform.at.entity.option',
        '',
        option_type=int,
        at=MULTIPLE_ENTITY_OPTION.option_id,
        transform=str),
    required=False)
TRANSFORMED_ENTITY_OPTION = ConfigOption(
    ConfigOptionId(
        'transformed.entity.option', '', entity=True, transform=lambda s: ''.join(s * 2)),
    required=False)
AT_TRANSFORMED_ENTITY_OPTION = ConfigOption(
    ConfigOptionId('at.transformed.entity.option', '', at=TRANSFORMED_ENTITY_OPTION.option_id),
    required=False)
