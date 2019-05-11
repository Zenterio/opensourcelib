from zaf.config.options import ConfigOptionId
from zaf.config.types import Path

PROFILING_DIR = ConfigOptionId(
    'profiling.dir', 'Profiling directory', option_type=Path(), default='${output.dir}/profiling')
PROFILING_CSV = ConfigOptionId(
    'profiling.report.csv',
    'If set, writes statistics in CSV format to file specified by profiling.csv.path',
    option_type=bool,
    default=False)
PROFILING_CSV_PATH = ConfigOptionId(
    'profiling.report.csv.path',
    'Generate profiling CSV report to specified file.',
    option_type=Path(),
    default='${profiling.dir}/report.csv')
PROFILING_JSON = ConfigOptionId(
    'profiling.report.json',
    'If set, writes statistics in JSON format to file specified by profiling.json.path',
    option_type=bool,
    default=False)
PROFILING_JSON_PATH = ConfigOptionId(
    'profiling.report.json.path',
    'Generate profiling JSON report to specified file.',
    option_type=Path(),
    default='${profiling.dir}/report.json')
PROFILING_TEXT = ConfigOptionId(
    'profiling.report.text',
    'Prints statistics in human readable text format',
    option_type=bool,
    default=False)
PROFILING_TEXT_PATH = ConfigOptionId(
    'profiling.report.text.path',
    'Generate profiling text report to specified file.',
    option_type=Path(),
    default='${profiling.dir}/report.txt')
