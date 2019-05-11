from zaf.config.options import ConfigOptionId
from zaf.messages.message import EndpointId, MessageId

SCHEDULER_ENDPOINT = EndpointId(
    'scheduler', """\
    Handles the scheduling of test cases.
    The run queue can be modified during the run using a set of messages.
    """)

TESTS_INCLUDE = ConfigOptionId(
    'tests.include',
    'Include test cases where the start of the qualified name matches this value. '
    'Syntax is "package[.module[[.class].testcase]]."',
    multiple=True,
)

TESTS_INCLUDE_REGEX = ConfigOptionId(
    'tests.include.regex',
    'Include test cases where the qualified name matches this regex.',
    multiple=True,
)

TESTS_EXCLUDE = ConfigOptionId(
    'tests.exclude',
    'Exclude test cases where the start of the qualified name matches this value. '
    'Syntax is "package[.module[[.class].testcase]]."',
    multiple=True,
)

TESTS_EXCLUDE_REGEX = ConfigOptionId(
    'tests.exclude.regex',
    'Exclude test cases where the qualified name matches this regex.',
    multiple=True,
)

SCHEDULE_NEXT_TEST = MessageId(
    'SCHEDULE_NEXT_TEST', """\
    Request that the scheduler schedules the next test case to be run.

    data: None
    returns: TestCaseDefinition
    """)

ADD_TEST_CASES = MessageId(
    'ADD_TEST_CASES', """\
    Message that can be sent to the test scheduler to add test cases to the run queue.
    Test cases will not be added if ABORT or CRITICAL_ABORT messages have been received by the scheduler.

    data: List of TestCaseDefinition
    """)

REMOVE_TEST_CASES = MessageId(
    'REMOVE_TEST_CASES', """\
    Message that can be sent to the test scheduler to remove test cases from the run queue.
    Returns the removed test cases.

    data: List of TestCaseDefinition
    returns: List of TestCaseDefinition
    """)

CLEAR_RUN_QUEUE = MessageId(
    'CLEAR_RUN_QUEUE', """\
    Message that can be sent to the test scheduler to clear the run queue.
    This also returns all the removed test cases.

    data: None
    returns: List of TestCaseDefinition
    """)

GET_CURRENT_RUN_QUEUE = MessageId(
    'GET_CURRENT_RUN_QUEUE', """\
    Message that can be sent to the test scheduler to request the current run queue.

    data: None
    returns: List of TestCaseDefinition
    """)

GET_LAST_SCHEDULED_TEST = MessageId(
    'GET_LAST_SCHEDULED_TEST', """\
    Message that can be sent to the test scheduler to request the last scheduled test case.

    data: None
    returns: TestCaseDefinition
    """)

RUN_QUEUE_INITIALIZED = MessageId(
    'RUN_QUEUE_INITIALIZED', """\
    Event that is sent from the scheduler when a the run queue is first initialized
    Subscribing with a CallbackDispatcher to this message makes it possible to modify the run queue before
    the first test case is scheduled

    data: Complete run queue as a list of TestCaseDefinition
    """)

RUN_QUEUE_MODIFIED = MessageId(
    'RUN_QUEUE_MODIFIED', """\
    Event that is sent from the scheduler when a the run queue is modified

    data: Complete run queue as a list of TestCaseDefinition
    """)

RUN_QUEUE_EMPTY = MessageId(
    'RUN_QUEUE_EMPTY', """\
    Event that is sent from the scheduler when a test case is about to be scheduled
    but the run queue is empty.
    Subscribing with a CallbackDispatcher to this message makes it possible to add new test cases
    to the run queue with the ADD_TEST_CASES request to continue the test run.

    data: None
    """)

SCHEDULING_NEXT_TEST = MessageId(
    'SCHEDULING_NEXT_TEST', """\
    Event that is sent from the scheduler when a test case is about to be scheduled.
    Subscribing with a CallbackDispatcher to this message makes it possible to
    manipulate the run queue before the next test is scheduled.

    data: None
    """)
