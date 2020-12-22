import logging

from zaf.component.decorator import requires

logger = logging.getLogger('testcase')
logger.addHandler(logging.NullHandler())

TIMEOUT = 10


@requires(sutevents='SutEvents')
def test_sutevents_expect_reset(sutevents):
    with sutevents.expect_reset():
        pass
