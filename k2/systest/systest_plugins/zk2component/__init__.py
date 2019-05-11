from zaf.config.options import ConfigOptionId
from zaf.config.types import Flag, Path

COVERAGE_ENABLED = ConfigOptionId(
    'coverage.enabled', 'Enables coverage measurement', option_type=Flag(), default=False)

COVERAGE_CONFIG_FILE = ConfigOptionId(
    'coverage.config.file',
    'Specifies a config file that will be forwarded to coverage',
    option_type=Path(exists=True))

LOG_DIR_TESTS = ConfigOptionId(
    'log.dir.tests',
    'Specifies directory of test specific log files',
    default='${log.dir}/tests',
    option_type=Path(exists=False))
