import os
import unittest
from unittest.mock import patch

from zaf.config.manager import ConfigManager
from zaf.config.options import ConfigOption
from zaf.extensions import PLUGINS_PATHS

from ..click import ClickInitPluginPath


class TestPartialParsers(unittest.TestCase):

    def setUp(self):
        self.plugin = ClickInitPluginPath({}, {})
        self.config = ConfigManager()
        self.config.set_default_values([PLUGINS_PATHS])
        self.option = ConfigOption(PLUGINS_PATHS, required=False)

    def test_plugin_paths_returned_when_exists(self):
        # PLUGINS_PATH checks that paths exist
        path = __file__
        path2 = os.getcwd()
        with patch('sys.argv', ['zaf', '--plugins-paths', path, '--plugins-paths', path2]):
            extension_config = self.plugin.get_config(self.config, [self.option], {})
            self.assertEqual(extension_config.config['plugins.paths'], (path, path2))

    def test_plugin_paths_not_returned_if_same_as_default(self):
        with patch('sys.argv', ['zaf']):
            extension_config = self.plugin.get_config(self.config, [self.option], {})
            self.assertNotIn('plugins-paths', extension_config.config)
