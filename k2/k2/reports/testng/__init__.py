from zaf.config.options import ConfigOptionId
from zaf.config.types import Path

REPORTS_TESTNG = ConfigOptionId(
    'reports.testng', 'Generate a TestNG XML report', option_type=bool, default=False)
REPORTS_TESTNG_FILE = ConfigOptionId(
    'reports.testng.file',
    'Write the report to this path. If no path is given the report will be stored in output_dir',
    default='${output.dir}/reports/testng/testng-results.xml',
    option_type=Path())
