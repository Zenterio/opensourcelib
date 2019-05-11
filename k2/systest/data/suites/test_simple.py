import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def test_my_test_case():
    logger.info('Running my test case')


def test_my_other_test_case():
    logger.info('Running my other test case')
