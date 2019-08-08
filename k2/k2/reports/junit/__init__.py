from zaf.config.options import ConfigOptionId
from zaf.config.types import Path

REPORTS_JUNIT = ConfigOptionId(
    'reports.junit', 'Generate a JUnit XML report', option_type=bool, default=False)
REPORTS_JUNIT_FILE = ConfigOptionId(
    'reports.junit.file',
    'Write the report to this path. If no path is given the report will be stored in output_dir',
    default='${output.dir}/reports/junit/junit-results.xml',
    option_type=Path())
