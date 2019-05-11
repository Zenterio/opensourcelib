from zaf.config.options import ConfigOptionId
from zaf.messages.message import EndpointId, MessageId

TEST_SOURCES = ConfigOptionId(
    'test.sources',
    'One or more test sources. Can be files, modules, classes etc',
    multiple=True,
    argument=True)

FINDER_ENDPOINT = EndpointId('testfinder', """\
The test finder
""")

FIND_TEST_CASES = MessageId(
    'FIND_TEST_CASES', """\
Request to find test cases.

returns: List of TestCase
""")
