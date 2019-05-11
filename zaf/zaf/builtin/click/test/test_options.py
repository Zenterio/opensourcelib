import unittest
from unittest.mock import Mock

import click

from zaf.config.options import ConfigOption, ConfigOptionId
from zaf.config.types import Choice, ConfigChoice, Count, Flag, GlobPattern, Path

from ..click import _create_options_from_config

stroption = ConfigOption(
    ConfigOptionId('stroption', 'description for stroption', option_type=str), required=False)
multi_stroption = ConfigOption(
    ConfigOptionId(
        'multi.stroption', 'description for multi.stroption', option_type=str, multiple=True),
    required=False)
required_stroption = ConfigOption(
    ConfigOptionId('required.stroption', 'description for required.stroption', option_type=str),
    required=True)
intoption = ConfigOption(
    ConfigOptionId('intoption', 'description for intoption', option_type=int), required=False)
floatoption = ConfigOption(
    ConfigOptionId('floatoption', 'description for floatoption', option_type=float), required=False)
booloption = ConfigOption(
    ConfigOptionId('booloption', 'description for booloption', option_type=bool), required=False)
flagoption = ConfigOption(
    ConfigOptionId('flagoption', 'description for flagoption', option_type=Flag()), required=False)
pathoption = ConfigOption(
    ConfigOptionId('pathoption', 'description for pathoption', option_type=Path(exists=True)),
    required=False)
choiceoption = ConfigOption(
    ConfigOptionId('choiceoption', 'description for choiceoption', option_type=Choice(['a', 'b'])),
    required=False)
configchoiceoption = ConfigOption(
    ConfigOptionId(
        'configchoiceoption',
        'description for configchoiceoption',
        option_type=ConfigChoice(multi_stroption.option_id)),
    required=False)
globpatternoption = ConfigOption(
    ConfigOptionId(
        'globpatternoption', 'description for globpatternoption', option_type=GlobPattern()),
    required=False)
countoption = ConfigOption(
    ConfigOptionId('countoption', 'description for countoption', option_type=Count(max=3)),
    required=False)


class TestCreateOptionsFromConfig(unittest.TestCase):

    def test_create_options_with_correct_name_and_envvar(self):
        actual_options = _create_options_from_config(empty_config, [stroption, multi_stroption])
        self.assertIn('--multi-stroption', actual_options[0].opts)
        self.assertEqual(actual_options[0].envvar, 'ZAF_MULTI_STROPTION')
        self.assertIn('--stroption', actual_options[1].opts)
        self.assertEqual(actual_options[1].envvar, 'ZAF_STROPTION')

    def test_required_translated_to_click(self):
        actual_options = _create_options_from_config(empty_config, [stroption, required_stroption])

        self.assertTrue(actual_options[0].required)
        self.assertFalse(actual_options[1].required)

    def test_multiple_translated_to_click(self):
        actual_options = _create_options_from_config(empty_config, [stroption, multi_stroption])

        self.assertTrue(actual_options[0].multiple)
        self.assertFalse(actual_options[1].multiple)

    def test_types_translated_to_click(self):
        actual_options = _create_options_from_config(
            empty_config, [
                stroption, intoption, floatoption, booloption, flagoption, pathoption, choiceoption,
                configchoiceoption, globpatternoption, countoption
            ])

        # sorted by name
        self.assertEqual(actual_options[0].name, 'booloption')
        self.assertEqual(actual_options[0].type, click.BOOL)
        self.assertEqual(actual_options[1].name, 'choiceoption')
        self.assertEqual(type(actual_options[1].type), click.Choice)
        self.assertEqual(actual_options[2].name, 'configchoiceoption')
        self.assertEqual(type(actual_options[2].type), click.Choice)
        self.assertEqual(actual_options[3].name, 'countoption')
        self.assertEqual(type(actual_options[3].type), click.IntRange)
        self.assertEqual(actual_options[4].name, 'flagoption')
        self.assertEqual(actual_options[4].type, click.BOOL)
        self.assertEqual(actual_options[5].name, 'floatoption')
        self.assertEqual(actual_options[5].type, click.FLOAT)
        self.assertEqual(actual_options[6].name, 'globpatternoption')
        self.assertEqual(actual_options[6].type, click.STRING)
        self.assertEqual(actual_options[7].name, 'intoption')
        self.assertEqual(actual_options[7].type, click.INT)
        self.assertEqual(actual_options[8].name, 'pathoption')
        self.assertEqual(type(actual_options[8].type), click.Path)
        self.assertEqual(actual_options[9].name, 'stroption')
        self.assertEqual(actual_options[9].type, click.STRING)

    def test_config_used_as_default_values(self):
        config = Mock()
        config.get.return_value = 'default'
        actual_options = _create_options_from_config(config, [stroption])

        self.assertEqual(actual_options[0].default, 'default')


ctx = Mock()
empty_config = Mock()
