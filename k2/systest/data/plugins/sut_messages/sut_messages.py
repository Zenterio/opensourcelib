from zaf.extensions.extension import AbstractExtension, CommandExtension
from zaf.messages.message import EndpointId

from k2.sut import SUT_RESET_DONE, SUT_RESET_EXPECTED, SUT_RESET_NOT_EXPECTED, SUT_RESET_STARTED

SYSTEST_SUT_MESSAGES_ENDPOINT = EndpointId('sutmessages', '')


@CommandExtension(
    name='sutmessages',
    extends=['sut'],
    endpoints_and_messages={
        SYSTEST_SUT_MESSAGES_ENDPOINT:
        [SUT_RESET_STARTED, SUT_RESET_DONE, SUT_RESET_EXPECTED, SUT_RESET_NOT_EXPECTED]
    })
class SutMessagesExtension(AbstractExtension):
    """
    Defines endpoints and messages for sutevents for use by the systests.

    Enabling this in a systest will make sure that the endpoint and messages are defined
    so that dispatchers will be registered correctly.
    """
    pass
