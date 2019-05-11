from zaf.config.options import ConfigOptionId
from zaf.messages.message import EndpointId, MessageId

EXTENSION_NAME = 'testrunner'

RUNNER_ENDPOINT = EndpointId('runner', """\
    The K2 default test runner
    """)

TEST_RUN_STARTED = MessageId(
    'TEST_RUN_STARTED', """\
    Message that is triggered when the test runner has started.

    data: k2.runner.messages.TestRunStarted
    """)

TEST_RUN_FINISHED = MessageId(
    'TEST_RUN_FINISHED', """\
    Message that is triggered when the test runner has finished.

    data: k2.runner.messages.TestRunFinished
    """)

TEST_CASE_STARTED = MessageId(
    'TEST_CASE_STARTED', """\
    Message that is triggered when the test case is started.

    data: k2.runner.messages.TestCaseStarted
    """)

TEST_CASE_FINISHED = MessageId(
    'TEST_CASE_FINISHED', """\
    Message that is triggered when the test case is completed.

    data: k2.runner.messages.TestCaseFinished
    """)

TEST_CASE_SKIPPED = MessageId(
    'TEST_CASE_SKIPPED', """\
    Message that is triggered when test cases are skipped.

    data: k2.runner.messages.TestCaseSkipped
    """)

ABORT_TEST_CASE_REQUEST = MessageId(
    'ABORT_TEST_CASE_REQUEST', """\
    Request that execution of the specified test case is immediately aborted.

    data: k2.runner.messages.AbortTestCaseRequest
    """)

RUNNER_SUITE_NAME = ConfigOptionId('suite.name', 'Test suite name', default='suite')
RUNNER_PARALLEL_WORKERS = ConfigOptionId(
    'parallel.workers', 'Number of parallel workers', default=1, option_type=int)
