from zaf.config.options import ConfigOptionId
from zaf.messages.message import MessageId

SUT_RECOVERY_PERFORM = MessageId(
    'SUT_RECOVERY_PERFORM', """\
    Perform a sut recovery. Send with endpoint_id=None and entity=sut_id.
    Raise exception if recovery is unsuccessful
    """)

SUT_RECOVERY_STARTED = MessageId(
    'SUT_RECOVERY_STARTED', """\
    Event indicating the recovery has been started.
    """)

SUT_RECOVERY_COMPLETED = MessageId(
    'SUT_RECOVERY_COMPLETED', """\
    Event indicating the recovery has been completed.
    """)

SUT_RESET_EXPECTED = MessageId(
    'SUT_RESET_EXPECTED', """\
    Event indicating that one or multiple expected reset(s) will be initiated.
    The event should be triggered by any module/extension that intentionally resets the system under test.
    This to allow extensions that trigger SUT_RESET_STARTED and SUT_RESET_DONE to take that into account.
    """)

SUT_RESET_NOT_EXPECTED = MessageId(
    'SUT_RESET_NOT_EXPECTED', """\
    Event indicating no more reset(s) are expected and should be treated as failures.
    The event should be triggered by any module/extension that intentionally resets the system under test.
    This to allow extensions that trigger SUT_RESET_STARTED and SUT_RESET_DONE to take that into account.
    """)

SUT_RESET_STARTED = MessageId(
    'SUT_RESET_STARTED', """\
    Event triggered when reset of sut has started

    Data: True/False indicating if the reset was expected or not
    """)

SUT_RESET_DONE = MessageId(
    'SUT_RESET_DONE', """\
    Event triggered when reset of sut has finished

    Data: True/False indicating if the reset was expected or not
    """)

SUT = ConfigOptionId(
    'ids', 'The SUT instances to use', multiple=True, entity=True, namespace='suts')

SUT_IP = ConfigOptionId('ip', 'IP number to the SUT', at=SUT)

SUT_ADD_CANS = ConfigOptionId('add.can', 'Adds a can to the SUT', at=SUT, multiple=True)

SUT_RESET_STARTED_TIMEOUT = ConfigOptionId(
    'resetstarted.timeout',
    'Timeout when waiting for SUT to indicate that the SUT has started reset',
    at=SUT,
    option_type=int,
    default=60)

SUT_RESET_DONE_TIMEOUT = ConfigOptionId(
    'resetdone.timeout',
    'Timeout when waiting for SUT to indicate that the SUT reset is completed',
    at=SUT,
    option_type=int,
    default=120)
