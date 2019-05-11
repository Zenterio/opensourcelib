import os
import subprocess

from zaf.component.decorator import component

import zelenium


class FirefoxError(Exception):
    pass


def register_firefox_webdriver_component(component_manager, headless=True):
    from selenium import webdriver
    from selenium.webdriver.firefox.options import Options

    _verify_that_firefox_is_installed()
    _verify_that_firefox_is_the_minimum_required_version()

    def firefox_webdriver():
        options = Options()
        if headless is True:
            options.add_argument('-headless')
        return webdriver.Firefox(executable_path=_get_geckodriver_path(), firefox_options=options)

    register_webdriver_component = component(name='Webdriver', can=['firefox'])
    register_firefox_webdriver_component = component(name='FirefoxWebdriver')
    register_webdriver_component(firefox_webdriver, component_manager)
    register_firefox_webdriver_component(firefox_webdriver, component_manager)


def _verify_that_firefox_is_installed():
    try:
        subprocess.check_call(('which', 'firefox'))
    except subprocess.CalledProcessError:
        raise FirefoxError(
            'Could not find the "firefox" executable. Please make sure Firefox is installed '
            'and available to your PATH.') from None


def _verify_that_firefox_is_the_minimum_required_version():
    try:
        output = subprocess.check_output(('firefox', '-version')).decode('utf-8')
        version = output.strip().split(' ')[-1]
        major_version = int(version.split('.')[0])
    except Exception:
        raise FirefoxError(
            'Unable to parse Firefox version information. Please make sure it is possible '
            'to run "firefox -version" on your system and that it produces output like '
            '"Mozilla Firefox 58.0.2".') from None

    if not major_version > 55:
        raise FirefoxError(
            'The K2 bundled version of "geckodriver" used for interacting with Firefox '
            'requires Firefox version 55 or later. Please upgrade.') from None


def _get_geckodriver_path():
    return os.path.join(zelenium.__path__[0], 'bin', 'geckodriver')
