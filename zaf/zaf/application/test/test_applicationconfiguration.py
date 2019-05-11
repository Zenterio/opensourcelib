import unittest

from zaf import __version__
from zaf.application import APPLICATION_NAME, APPLICATION_VERSION, ENTRYPOINT_NAME
from zaf.config.manager import ConfigManager
from zaf.extensions import EXTENSION_ENABLED

from ..application import ApplicationConfiguration


class ApplicationConfigurationTest(unittest.TestCase):

    def apply_configuration(self, **kwargs):
        cfg = ApplicationConfiguration('NAME', **kwargs)
        cm = ConfigManager()
        cfg.apply_configuration(cm)
        return cm

    def test_name_sets_application_name(self):
        cm = self.apply_configuration()
        self.assertEqual(cm.get(APPLICATION_NAME), 'NAME')

    def test_cli_disables_click(self):
        cm = self.apply_configuration(cli=False)
        self.assertEqual(cm.get(EXTENSION_ENABLED, entity='click'), False)

    def test_click_enabled_by_default(self):
        cm = self.apply_configuration()
        self.assertEqual(cm.get(EXTENSION_ENABLED, entity='click'), True)

    def test_entrypoint_defaults_to_name(self):
        cm = self.apply_configuration()
        self.assertEqual(cm.get(ENTRYPOINT_NAME), 'NAME')

    def test_entrypoint_sets_application_entrypoint(self):
        cm = self.apply_configuration(entrypoint='ep')
        self.assertEqual(cm.get(ENTRYPOINT_NAME), 'ep')

    def test_version_defaults_to_zaf_version(self):
        cm = self.apply_configuration()
        self.assertEqual(cm.get(APPLICATION_VERSION), __version__)

    def test_version_sets_application_version(self):
        cm = self.apply_configuration(version='2.45')
        self.assertEqual(cm.get(APPLICATION_VERSION), '2.45')
