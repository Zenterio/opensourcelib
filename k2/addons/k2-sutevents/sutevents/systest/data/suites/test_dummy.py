import logging

from zaf.component.decorator import requires
from zaf.messages.dispatchers import LocalMessageQueue

from k2.sut import SUT_RESET_STARTED

logger = logging.getLogger('testcase')
logger.addHandler(logging.NullHandler())


@requires(messagebus='MessageBus')
def test_1(messagebus):
    with LocalMessageQueue(messagebus, [SUT_RESET_STARTED]) as queue:
        logger.info('test 1')
        queue.get(timeout=5)


def test_2():
    logger.info('test 2')
