import logging

from k2.runner.decorator import disabled
from k2.runner.exceptions import SkipException

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def test_success():
    """Test that test cases can be successful."""
    pass


def test_failure():
    """Test that test cases can fail with failure verdict."""
    raise AssertionError('Failed')


def test_error():
    """Test that test cases can fail with error verdict."""
    raise ValueError('ERROR occurred')


def test_skip():
    """Test that test cases can be skipped."""
    raise SkipException('Should be skipped')


@disabled('This testcase is disabled')
def test_ignored():
    """Should not be executed."""
    raise ValueError('This should not happen')
