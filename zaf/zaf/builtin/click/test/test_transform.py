import unittest
from unittest.mock import patch

from zaf.commands.command import CommandId
from zaf.config.manager import ConfigManager
from zaf.config.options import ConfigOption, ConfigOptionId
from zaf.config.types import Choice

from ..click import ClickParseCli


class TestTransform(unittest.TestCase):

    def setUp(self):
        self.plugin = ClickParseCli({}, {})
        self.config = ConfigManager()

    def test_default_values_for_options_with_transform_treated_as_normal_options(self):
        with patch('sys.argv', ['zaf', 'command']):
            extension_config = self.plugin.get_config(
                self.config, [ConfigOption(TRANSFORM, required=False)], {
                    COMMAND: []
                })
            self.assertNotIn('transform', extension_config.config)

    def test_transform_not_performed_on_default_value_by_using_incompatible_types(self):
        with patch('sys.argv', ['zaf', 'command']):
            extension_config = self.plugin.get_config(
                self.config, [ConfigOption(TRANSFORM_TO_OTHER_TYPE, required=False)], {
                    COMMAND: []
                })
            self.assertNotIn('transform', extension_config.config)

    def test_transform_not_performed_on_default_value_by_using_invalid_choice(self):
        with patch('sys.argv', ['zaf', 'command']):
            extension_config = self.plugin.get_config(
                self.config, [ConfigOption(TRANSFORM_FROM_CHOICE, required=False)], {
                    COMMAND: []
                })
            self.assertNotIn('transform', extension_config.config)


COMMAND = CommandId('command', '', callable=None, config_options=[])
TRANSFORM = ConfigOptionId('transform', '', default='original', transform=lambda s: 'transformed')
TRANSFORM_TO_OTHER_TYPE = ConfigOptionId(
    'transform.to.other.type',
    '',
    default=2.3,
    option_type=float,
    transform=lambda s: 'transformed')
TRANSFORM_FROM_CHOICE = ConfigOptionId(
    'transform.to.other.type',
    '',
    default='1',
    option_type=Choice(['1', '2', '3']),
    transform=lambda s: '4')
