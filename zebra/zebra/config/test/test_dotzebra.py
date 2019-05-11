import unittest
from unittest.mock import Mock, patch

from zaf.builtin.unittest.harness import ExtensionTestHarness
from zaf.extensions.extension import ExtensionConfig

from zebra.config.dotzebra import DotZebraExtension


class TestDotZebra(unittest.TestCase):

    def test_find_zebra_file(self):
        zebra_file = '/path/to/zebra/file/.zebra'
        current_dir = '/path/to/zebra/file/sub/dir'

        def exists(file):
            return file == zebra_file

        with create_harness() as harness:
            with patch('os.path.exists', side_effect=exists):
                self.assertEqual(harness.extension.find_zebra_file(current_dir), zebra_file)

    def test_find_zebra_file_returns_none_if_file_not_found(self):
        current_dir = '/path/to/zebra/file/sub/dir'

        with create_harness() as harness:
            with patch('os.path.exists', return_value=False):
                self.assertEqual(harness.extension.find_zebra_file(current_dir), None)

    def test_get_config_returns_config_from_dot_zebra_file(self):
        with patch.object(DotZebraExtension, 'find_zebra_file', return_value='.zebra'), \
                patch('zebra.config.dotzebra._recursively_load_configuration',
                      return_value=ExtensionConfig({'image': 'abs.u16'}, 9)):
            with create_harness() as harness:
                self.assertEqual(
                    harness.extension.get_config(Mock(), [], {}).config['image'], 'abs.u16')

    def test_get_config_returns_empty_extension_config_if_no_file(self):
        with patch.object(DotZebraExtension, 'find_zebra_file', return_value=None):
            with create_harness() as harness:
                self.assertDictEqual(harness.extension.get_config(Mock(), [], {}).config, {})


def create_harness():
    return ExtensionTestHarness(DotZebraExtension)
