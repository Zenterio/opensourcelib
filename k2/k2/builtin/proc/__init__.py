from zaf.config.options import ConfigOptionId
from zaf.config.types import Flag, Path

COVERAGE_ENABLED = ConfigOptionId(
    'coverage.enabled', 'Enables coverage measurement', option_type=Flag(), default=False)

COVERAGE_CONFIG_FILE = ConfigOptionId(
    'coverage.config.file',
    'Specifies a config file that will be forwarded to coverage',
    option_type=Path(exists=True))

COVERAGE_REPORT = ConfigOptionId(
    'coverage.report',
    'Specifies path of the report file.',
    option_type=Path(),
    default='.coverage')

COVERAGE_XML_REPORT = ConfigOptionId(
    'coverage.xml.report',
    'Specifies path of the xml report file.',
    option_type=Path(),
    default=None)
