"""
Provides the unittest command.

The unittest command can be used to run unit tests for an extension, or a
specific Python file using the zaf environment.

The idea is to not require a special environment to develop plugins but instead
to be able to use the installed zaf as the development environment.
"""
import sys

from zaf.application import APPLICATION_NAME, APPLICATION_ROOT
from zaf.builtin.unittest import coverage, packages
from zaf.commands.command import CommandId
from zaf.config.options import ConfigOption, ConfigOptionId
from zaf.config.types import Flag
from zaf.extensions.extension import FrameworkExtension

UNIT_TEST_PATTERN = r'^Test|^test_|\.test_|\.test\.'


def unittest(core):
    """
    Run unittest for extensions.

    Example to run unittest for all loaded extensions::

        zaf unittest

    To run unit tests for a specific addon::

        zaf unittest myaddon

    To run unit tests for a specific plugin first of all Zaf needs to be able to find it.
    This is done using the normal --plugins-paths option to the Zaf command and then
    to only run unittests for the wanted extension the name of the extension is used as
    an argument::

        zaf --plugins-paths path/to/my/plugin unittest myplugin

    The unittest command supports coverage measurements using the python coverage package.
    This can be enabled with the --coverage-enabled flag.
    """

    # local import because nose uses pkg_resources that is very slow to import
    import nose.core

    config = core.config

    application_name = config.get(APPLICATION_NAME)
    application_package = config.get(APPLICATION_ROOT)

    extension_names = config.get(EXTENSION_NAMES)
    tests = config.get(TESTS)
    report_enabled = config.get(REPORT_ENABLED)
    report_file = config.get(REPORT_FILE)
    coverage_enabled = core.config.get(COVERAGE_ENABLED)
    verbose = core.config.get(DETAILS)
    exclude_systests = core.config.get(EXCLUDE_SYSTESTS)

    matching_packages = packages.find_packages(
        extension_names, core.extension_manager, application_name, application_package)
    command = create_nose_command(
        matching_packages, verbose, tests, report_enabled, report_file, exclude_systests)

    if coverage_enabled:
        coverage_file = core.config.get(COVERAGE_FILE)
        xml_enabled = core.config.get(COVERAGE_XML_ENABLED)
        xml_file = core.config.get(COVERAGE_XML_FILE)
        with coverage.coverage(matching_packages, sys.stdout, coverage_file, xml_enabled, xml_file):
            result = nose.core.run(argv=command)
    else:
        result = nose.core.run(argv=command)

    return 0 if result else 1


def create_nose_command(
        packages,
        verbose=False,
        tests=None,
        report_enabled=False,
        report_file=None,
        exclude_systests=True):
    command = [
        'nosetests',
        '-m',
        UNIT_TEST_PATTERN,
        '--detailed-errors',
        '--logging-clear-handlers',
        '--logging-datefmt=%H:%M:%S',
        '--logging-format=%(asctime)s.%(msecs)03d %(levelname)s:%(message)s',
    ]

    if exclude_systests:
        command.extend([
            '--exclude-path',
            '*systest*',
        ])

    if report_enabled:
        command.append('--with-xunit')
        if report_file:
            command.extend(['--xunit-file', report_file])

    if verbose:
        command.extend(['-v', '--with-timer'])

    if tests:
        command.extend(tests)
    else:
        command.extend(packages)

    return command


EXTENSION_NAMES = ConfigOptionId(
    'extension.names', 'The extension to run unittests for', argument=True, multiple=True)

REPORT_ENABLED = ConfigOptionId(
    'report.enabled',
    'Generate a test report',
    option_type=Flag(),
    default=False,
    namespace='unittest',
    short_alias=True)

REPORT_FILE = ConfigOptionId(
    'report.file',
    'File name of the test report',
    default='nosetests.xml',
    namespace='unittest',
    short_alias=True)

COVERAGE_ENABLED = ConfigOptionId(
    'coverage.enabled',
    'Run unittests with coverage',
    option_type=Flag(),
    default=False,
    namespace='unittest',
    short_alias=True)

COVERAGE_FILE = ConfigOptionId(
    'coverage.file',
    'File name of coverage file',
    default='.coverage',
    namespace='unittest',
    short_alias=True)

COVERAGE_XML_ENABLED = ConfigOptionId(
    'coverage.xml.enabled',
    'Enabled XML coverage file',
    option_type=Flag(),
    default=False,
    namespace='unittest',
    short_alias=True)

COVERAGE_XML_FILE = ConfigOptionId(
    'coverage.xml.file',
    'File name of XML coverage file',
    default='coverage.xml',
    namespace='unittest',
    short_alias=True)

DETAILS = ConfigOptionId(
    'details',
    'Detailed output for unit tests',
    option_type=Flag(),
    default=False,
    namespace='unittest',
    short_alias=True)

EXCLUDE_SYSTESTS = ConfigOptionId(
    'exclude.systest',
    'Exclude paths used for system tests when finding unit tests',
    option_type=Flag(),
    default=True,
    namespace='unittest',
    short_alias=True)

TESTS = ConfigOptionId(
    'tests', (
        'A module, package, directory, file or class with tests. '
        'A specific test case can be identified by appending :<test>. '
        'This can be given multiple times and it overrides the extension name argument'),
    multiple=True,
    namespace='unittest',
    short_alias=True)

UNITTEST_COMMAND = CommandId(
    'unittest',
    unittest.__doc__,
    unittest,
    config_options=[
        ConfigOption(EXTENSION_NAMES, required=False),
        ConfigOption(REPORT_ENABLED, required=False),
        ConfigOption(REPORT_FILE, required=False),
        ConfigOption(COVERAGE_ENABLED, required=False),
        ConfigOption(COVERAGE_FILE, required=False),
        ConfigOption(COVERAGE_XML_ENABLED, required=False),
        ConfigOption(COVERAGE_XML_FILE, required=False),
        ConfigOption(DETAILS, required=False),
        ConfigOption(EXCLUDE_SYSTESTS, required=False),
        ConfigOption(TESTS, required=False)
    ],
    hidden=True,
)


@FrameworkExtension(name='unittestcommand', commands=[UNITTEST_COMMAND])
class UnittestCommand():
    """Provides the unittest command."""

    def __init__(self, config, instances):
        pass
