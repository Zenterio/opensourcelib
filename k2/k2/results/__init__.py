from zaf.messages.message import EndpointId, MessageId

RESULTS_ENDPOINT = EndpointId(
    'results', """\
    Collects test results and triggers TEST_RESULTS_COLLECTED when test run is completed
    """)

TEST_RESULTS_COLLECTED = MessageId(
    'TEST_RESULTS_COLLECTED', """\
    Message that is triggered when the test run is completed with a complete collection of the test results

    data: k2.results.results.TestResult
    """)
