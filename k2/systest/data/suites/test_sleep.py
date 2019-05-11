import logging
from time import sleep

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def test_that_prints_start_and_sleeps():
    logger.info('Running my test case')
    print('Test case 1 started', flush=True)
    for i in range(0, 50):
        sleep(0.1)


def test_that_sleeps():
    logger.info('Running my test case')
    for i in range(0, 50):
        sleep(0.1)
