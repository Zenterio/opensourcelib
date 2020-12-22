from zaf.config.options import ConfigOptionId

GTEST_binaryid = ConfigOptionId(
    'ids',
    """The gtest binary runner instance to use""",
    multiple=True,
    entity=True,
    namespace='gtest')

GTEST_BINARY_PATH = ConfigOptionId(
    'binary', """Path to the gtest binary to run""", at=GTEST_binaryid)

GTEST_TIMEOUT = ConfigOptionId(
    'timeout',
    """How long the gtest executable is allowed to run in seconds""",
    default=60,
    option_type=int,
    at=GTEST_binaryid)

GTEST_XML_REPORT_PATH = ConfigOptionId(
    'report.xml.path',
    """If specified and the gtest binary support the '--gtest-output=xml' flag, write the report to this path""",
    at=GTEST_binaryid)

GTEST_FILTER = ConfigOptionId(
    'filter',
    """Run only the tests whose name matches one of the positive patterns but
    none of the negative patterns. '?' matches any single character; '*'
    matches any substring; ':' separates two patterns.""",
    at=GTEST_binaryid)

GTEST_USE_SERIAL = ConfigOptionId(
    'use_serial',
    """Start the binary using a serial connection. Needed if the binary runs in a container started via Zac""",
    default=False,
    option_type=bool,
    at=GTEST_binaryid)

GTEST_SERIAL_ENDMARK = ConfigOptionId(
    'serial_endmark',
    """The prompt or message to look for to know that the serial command has finished executing""",
    default=None,
    at=GTEST_binaryid)
