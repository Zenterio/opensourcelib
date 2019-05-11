import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def test_first():
    pass


def test_second():
    assert False, 'This test fails intentionally'


def test_third():
    pass
