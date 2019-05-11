from zaf.config.options import ConfigOptionId

ZELENIUM_ENABLED = ConfigOptionId(
    'zelenium.enabled', 'Should the Zelenium addon be enabled', option_type=bool, default=False)

ZELENIUM_HEADLESS = ConfigOptionId(
    'zelenium.headless', 'Should the browser run in headless mode', option_type=bool, default=True)

ZELENIUM_FIREFOX = ConfigOptionId(
    'zelenium.firefox',
    'Should support for the Firefox browser be enabled',
    option_type=bool,
    default=True)
