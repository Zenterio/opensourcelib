"""
Selenium support for K2.

Selenium is a browser automation framework that can be used to test web services.
For more information about Selenium, please see:
http://www.seleniumhq.org/

Currently supports the Firefox browser using a bundled geckodriver.
"""

import logging

from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, FrameworkExtension, get_logger_name

from zelenium import ZELENIUM_ENABLED, ZELENIUM_FIREFOX, ZELENIUM_HEADLESS

from .firefox import register_firefox_webdriver_component

logger = logging.getLogger(get_logger_name('k2', 'zelenium'))
logger.addHandler(logging.NullHandler())


@FrameworkExtension(
    name='zelenium',
    config_options=[
        ConfigOption(ZELENIUM_ENABLED, required=True),
        ConfigOption(ZELENIUM_HEADLESS, required=True),
        ConfigOption(ZELENIUM_FIREFOX, required=True),
    ],
)
class Zelenium(AbstractExtension):

    def __init__(self, config, instances):
        self._enabled = config.get(ZELENIUM_ENABLED)
        self._headless = config.get(ZELENIUM_HEADLESS)
        self._firefox_enabled = config.get(ZELENIUM_FIREFOX)

    def register_components(self, component_manager):
        if self._enabled and self._firefox_enabled:
            register_firefox_webdriver_component(component_manager, headless=self._headless)
