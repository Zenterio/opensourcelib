from unittest import TestCase
from unittest.mock import patch

from zaf.builtin.unittest.harness import ExtensionTestHarness
from zaf.config.manager import ConfigManager

from ..zelenium import ZELENIUM_ENABLED, ZELENIUM_FIREFOX, ZELENIUM_HEADLESS, Zelenium


class TestZelenium(TestCase):

    @staticmethod
    def create_harness(headless=True, firefox_enabled=False):
        config = ConfigManager()
        config.set(ZELENIUM_ENABLED, True)
        config.set(ZELENIUM_HEADLESS, headless)
        config.set(ZELENIUM_FIREFOX, firefox_enabled)

        return ExtensionTestHarness(Zelenium, config=config)

    def test_headless_mode_can_be_enabled(self):
        with TestZelenium.create_harness(headless=True) as harness:
            assert harness.extension._headless is True

    def test_headless_mode_can_be_disabled(self):
        with TestZelenium.create_harness(headless=False) as harness:
            assert harness.extension._headless is False

    def test_firefox_webdriver_component_is_registered_if_enabled(self):
        with patch('zelenium.firefox._verify_that_firefox_is_installed'), \
             patch('zelenium.firefox._verify_that_firefox_is_the_minimum_required_version'), \
             TestZelenium.create_harness(firefox_enabled=True) as harness:
            assert 'Webdriver' in harness.component_registry
            assert 'FirefoxWebdriver' in harness.component_registry

    def test_firefox_webdriver_component_is_not_registed_if_disabled(self):
        with TestZelenium.create_harness(firefox_enabled=False) as harness:
            assert 'Webdriver' not in harness.component_registry
            assert 'FirefoxWebdriver' not in harness.component_registry
