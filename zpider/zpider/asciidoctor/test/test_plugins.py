import unittest
from unittest.mock import Mock, patch

from zaf.builtin.unittest.harness import ExtensionTestHarness
from zaf.config.manager import ConfigManager
from zaf.messages.message import EndpointId

from zpider.asciidoctor import GET_ASCIIDOCTOR_OPTIONS, PLUGIN_DIRS
from zpider.asciidoctor.plugins import INTERNAL_PLUGIN_DIRECTORY, AsciidoctorPlugins


class TestPluginsExtension(unittest.TestCase):

    def test_find_plugins_directory(self):
        with _create_harness() as harness:
            self.assertEqual(['/path/to/plugins'], list(harness.extension._plugins_dirs))

    def test_get_plugins_called_using_request(self):
        with _create_harness() as harness, \
                patch('os.listdir', return_value=[]):
            futures = harness.messagebus.send_request(GET_ASCIIDOCTOR_OPTIONS)
            futures.wait(timeout=1)
            self.assertIn('-r ', futures[0].result())

    def test_standard_plugins_are_automatically_added(self):
        with _create_harness() as harness, \
                patch('os.listdir', return_value=[]):
            self.assertIn('-r asciidoctor-diagram', harness.extension.get_plugins(Mock()))

    def test_internal_plugins_automatically_added(self):
        with _create_harness() as harness, \
                patch('os.listdir', return_value=[]) as listdir_mock:
            harness.extension.get_plugins(Mock())
            listdir_mock.assert_any_call(INTERNAL_PLUGIN_DIRECTORY)

    def test_rb_files_in_plugin_dirs_considered_plugins(self):
        with _create_harness() as harness, \
                patch('os.listdir', return_value=['a.rb', 'b.txt']):
            self.assertIn('-r /path/to/plugins/a.rb', harness.extension.get_plugins(Mock()))

            self.assertNotIn('b.txt', harness.extension.get_plugins(Mock()))


OPTIONS_ENDPOINT = EndpointId('OPTIONS_ENDPOINT', '')


def _create_harness():
    config = ConfigManager()
    with patch('os.path.exists', return_value=True):
        config.set(PLUGIN_DIRS, ['/path/to/plugins'])

    return ExtensionTestHarness(
        AsciidoctorPlugins,
        config=config,
    )
