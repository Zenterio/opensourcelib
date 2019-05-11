import unittest

from zaf.builtin.unittest.harness import ExtensionTestHarness
from zaf.config.manager import ConfigManager

from zebra.logging import VERBOSE
from zebra.logging.logging import ZebraLoggingExtension


class TestZebraLogging(unittest.TestCase):

    def test_default_zebra_log_level_is_info(self):
        with create_harness() as harness:
            extension_config = harness.extension.get_config(harness.config, [], {})
            self.assertEqual(extension_config.config['log.info'], ['zebra'])
            self.assertEqual(extension_config.config['log.debug'], [])

    def test_verbosity_1_gives_zebra_log_level_debug(self):
        with create_harness(1) as harness:
            extension_config = harness.extension.get_config(harness.config, [], {})
            self.assertEqual(extension_config.config['log.info'], [])
            self.assertEqual(extension_config.config['log.debug'], ['zebra'])


def create_harness(verbosity=0):
    config = ConfigManager()
    if verbosity > 0:
        config.set(VERBOSE, verbosity)

    return ExtensionTestHarness(
        ZebraLoggingExtension,
        config=config,
    )
