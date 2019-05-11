from zaf.config.options import ConfigOptionId
from zaf.config.types import Path
from zaf.messages.message import EndpointId, MessageId

Z2_REPORTS = ConfigOptionId('reports.z2', 'Generate a Z2 report', option_type=bool, default=False)

Z2_REPORTS_FILE = ConfigOptionId(
    'reports.z2.file',
    'Write the report to this path. If no path is given the report will be stored in output_dir',
    default='${output.dir}/reports/z2/z2-results.json',
    option_type=Path())

Z2_REPORTS_URL = ConfigOptionId('reports.z2.url', 'Upload the report to this Z2 instance.')

Z2_REPORTS_JOB_NAME = ConfigOptionId(
    'reports.z2.job.name', 'Name of the job that initiated this K2 run.')

Z2_REPORTS_BUILD_NUMBER = ConfigOptionId(
    'reports.z2.build.number',
    'Build number of the job that initiated this K2 run.',
    option_type=int)

Z2_REPORTS_ENDPOINT = EndpointId('Z2_REPORTER_ENDPOINT', 'The Z2 reporter endpoint')

Z2_INTERNAL_PUBLISH_REPORT_REQUEST = MessageId(
    'Z2_INTERNAL_PUBLISH_REPORT_REQUEST', """\
    Request sent internally to indicate when a report should be published.

    data: The Z2 report to publish.
    """)
