import logging

from zaf.component.decorator import component, requires
from zaf.messages.dispatchers import LocalMessageQueue

from k2 import CRITICAL_ABORT
from k2.sut import SUT_RESET_DONE, SUT_RESET_STARTED
from systest.data.plugins.sut_messages.sut_messages import SYSTEST_SUT_MESSAGES_ENDPOINT

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def test_first():
    pass


@component()
@requires(messagebus='MessageBus')
def ensure_sut_reset_done_sent(messagebus):
    yield
    messagebus.trigger_event(SUT_RESET_DONE, SYSTEST_SUT_MESSAGES_ENDPOINT, data=False)


@requires(messagebus='MessageBus')
@requires(ensure_sut_reset_done_sent=ensure_sut_reset_done_sent)
def test_second(messagebus, ensure_sut_reset_done_sent):
    with LocalMessageQueue(messagebus, [CRITICAL_ABORT]) as queue:
        messagebus.trigger_event(SUT_RESET_STARTED, SYSTEST_SUT_MESSAGES_ENDPOINT, data=False)
        queue.get(timeout=10)


def test_third():
    pass
