from zaf.config.options import ConfigOptionId

CONSOLE_binaryid = ConfigOptionId(
    'ids',
    """The console binary runner instance to use""",
    multiple=True,
    entity=True,
    namespace='console.binary')

CONSOLE_BINARY_PATH = ConfigOptionId('binary', """Path to the binary to run""", at=CONSOLE_binaryid)

CONSOLE_BINARY_TIMEOUT = ConfigOptionId(
    'timeout',
    """How long the executable is allowed to run in seconds""",
    default=60,
    option_type=int,
    at=CONSOLE_binaryid)

CONSOLE_BINARY_PASSED_PATTERN = ConfigOptionId(
    'passed.pattern',
    """Regular expression that when seen in the console log consitutes a passed test""",
    multiple=True,
    at=CONSOLE_binaryid)

CONSOLE_BINARY_FAILED_PATTERN = ConfigOptionId(
    'failed.pattern',
    """Regular expression that when seen in the console log constitutes a failed test""",
    multiple=True,
    at=CONSOLE_binaryid)

CONSOLE_BINARY_ERROR_PATTERN = ConfigOptionId(
    'error.pattern',
    """Regular expression that when seen in the console log constitutes an errored test""",
    multiple=True,
    at=CONSOLE_binaryid)

CONSOLE_BINARY_PENDING_PATTERN = ConfigOptionId(
    'pending.pattern',
    """Regular expression that when seen in the console log constitutes an pending test""",
    multiple=True,
    at=CONSOLE_binaryid)

CONSOLE_BINARY_SKIPPED_PATTERN = ConfigOptionId(
    'skipped.pattern',
    """Regular expression that when seen in the console log constitutes a skipped test""",
    multiple=True,
    at=CONSOLE_binaryid)

CONSOLE_BINARY_IGNORED_PATTERN = ConfigOptionId(
    'ignored.pattern',
    """Regular expression that when seen in the console log constitutes an ignored test""",
    multiple=True,
    at=CONSOLE_binaryid)
