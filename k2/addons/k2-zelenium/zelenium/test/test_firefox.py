import os
import subprocess
import unittest
from unittest.mock import ANY, MagicMock, patch

from ..firefox import FirefoxError, _get_geckodriver_path, _verify_that_firefox_is_installed, \
    _verify_that_firefox_is_the_minimum_required_version


class TestVerifyThatFirefoxIsInstalledFirefox(unittest.TestCase):

    def test_raises_firefox_error_on_error(self):
        with patch('subprocess.check_call', side_effect=subprocess.CalledProcessError(ANY, ANY)):
            with self.assertRaises(FirefoxError):
                _verify_that_firefox_is_installed()

    def test_does_not_raise_on_success(self):
        with patch('subprocess.check_call'):
            _verify_that_firefox_is_installed()


class TestVerifyThatFirefixIsTheMinimumRequiredVersion(unittest.TestCase):

    def test_raises_firefox_error_on_error(self):
        version = 'Lynx Version 2.8.9dev.8 (21 Dec 2015)'.encode('utf-8')
        with patch('subprocess.check_output', new=MagicMock(return_value=version)):
            with self.assertRaises(FirefoxError):
                _verify_that_firefox_is_the_minimum_required_version()

    def test_raises_firefox_error_if_too_old(self):
        version = 'Mozilla Firefox 54.0.0'.encode('utf-8')
        with patch('subprocess.check_output', new=MagicMock(return_value=version)):
            with self.assertRaises(FirefoxError):
                _verify_that_firefox_is_the_minimum_required_version()

    def test_does_not_raise_on_success(self):
        version = 'Mozilla Firefox 58.0.2'.encode('utf-8')
        with patch('subprocess.check_output', new=MagicMock(return_value=version)):
            _verify_that_firefox_is_the_minimum_required_version()


def test_get_geckodriver_path():
    assert os.path.join('zelenium', 'zelenium', 'bin', 'geckodriver') in _get_geckodriver_path()
