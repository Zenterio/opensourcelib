from zaf.config.options import ConfigOptionId
from zaf.config.types import Choice

REPORTS_TEXT = ConfigOptionId(
    'reports.text',
    'Print test results in human readable text format',
    option_type=bool,
    default=True)

REPORTS_TEXT_OUTPUT = ConfigOptionId(
    'reports.text.output',
    'Output location(s), default stdout',
    option_type=str,
    multiple=True,
    default=['-'])

REPORTS_TEXT_SHOW_OWNER = ConfigOptionId(
    'reports.text.show.owner', 'Show the owner of test cases. ', option_type=bool, default=False)

REPORTS_TEXT_TEMPLATE = ConfigOptionId(
    'reports.text.format',
    'Choose how much to print. ',
    option_type=Choice(['full', 'brief', 'summary']),
    default='full')
